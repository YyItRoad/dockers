#!/usr/bin/env python3
#
# Copyright (c) 2003-2005 Maxim Sobolev. All rights reserved.
# Copyright (c) 2006-2014 Sippy Software, Inc. All rights reserved.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import threading
import multiprocessing
import sys
import os
import getopt
import time
from sippy.Core.EventDispatcher import ED2
from sippy.misc import daemonize
from sippy.StatefulProxy import StatefulProxy
from sippy.SipTransactionManager import SipTransactionManager
from sippy.SipCallId import SipCallId
from sippy.SipLogger import SipLogger
from sippy.SipConf import SipConf
from sippy.UaStateDead import UaStateDead
from sippy.CCEvents import CCEventDisconnect, CCEventTry, CCEventRing, CCEventFail
from sippy.UA import UA
from requests_futures.sessions import FuturesSession
from urllib.parse import parse_qs
import asyncio
import grequests


class CallController(object):
    id = 1
    global_config = None
    uaA = None
    uaO = None
    cId = None
    # 主叫
    cli = None
    # 被叫
    cld = None
    # 小号
    _number = None
    _invite_event = None
    _media = None

    time_invite = None

    nh_addr = None

    def __init__(self, global_config):
        self.id = CallController.id
        CallController.id += 1
        self.global_config = global_config
        # self.invite_session = global_config['_invite_session']
        self.session = global_config['_request_session']
        self.uaA = UA(self.global_config, event_cb=self.recvEvent, conn_cbs=(self.aConn,),
                      ring_cbs=(self.aRing,), disc_cbs=(self.aDisc,), fail_cbs=(self.aDisc,))
        self.uaO = None

    def addRequest(self, task):
        cli, cld, number, state = task
        root = 'http://218.104.49.221:8801'
        if root.startswith('11888857'):
            root = 'http://218.104.49.217:8801'
        url = root + '/api/fs/calling?caller=%s&called=%s&number=%s&state=%s' % (
            cli, cld, number, state)
        try:
            if state == 'invite':
                self.session.get(url, timeout=8, hooks=dict(
                    response=self.requestCallback))
            else:
                self.session.get(url, timeout=3, hooks=dict(
                    response=self.requestCallback))
        except Exception as e:
            self.createUa0({state: "0", "url": url, "error": e})

    def aRing(self, ua, rtime, origin, result=0):
        if ua.lSDP != None and self._media == None:
            self._media = 1
            self.addRequest((self.cli, self.cld, self._number, 'media'))

    def aDisc(self, ua, rtime, origin, result=0):
        if self._number != '0':
            self.addRequest((self.cli, self.cld, self._number, 'hangup'))

    def aConn(self, ua, rtime, origin):
        self.addRequest((self.cli, self.cld, self._number, 'answer'))

    def requestCallback(self, resp, *args, **kwargs):
        query = parse_qs(resp.url)
        param = {query['state'][0]: resp.text, "url": resp.url,
                 "diff": round(time.time() * 1000) - self.time_invite}
        print('threading.currentThread =>', threading.currentThread().ident)
        ED2.callFromThread(self.createUa0, param)

    def createUa0(self, param):
        self.global_config['_sip_logger'].write(
            'requestCallback %s==>' % (self.id), param)
        res = param.get('invite')
        if (res == None):
            return
        if res == "0":
            self._number = res
            self.uaA.recvEvent(CCEventFail(
                (480, 'No Number'), rtime=self._invite_event.rtime))
        else:
            self._number, _type, _gateway, _vos_ip = res.split("|")
            cId, cGUID, cli, cld, body, auth, caller_name = self._invite_event.getData()
            oli = self.cli
            if _type == "3":
                oli = cli + cld[8:]
            event = self._invite_event
            event.data = (SipCallId(), cGUID, oli, self._number,
                          body, auth, caller_name)
            parts = _vos_ip.split(':')
            port = '5060'
            if len(parts) == 2:
                port = parts[1]
            self.uaO = UA(self.global_config, event_cb=self.recvEvent,
                          nh_address=tuple([parts[0], int(port)]))
            self.uaO.recvEvent(event)

    def recvEvent(self, event, ua):
        if ua == self.uaA:
            if self.uaO == None and self._invite_event == None:
                if not isinstance(event, CCEventTry) or self._number != None:
                    # Some weird event received
                    self.uaA.recvEvent(CCEventDisconnect())
                    return
                self.cId, cGUID, self.cli, self.cld, body, auth, caller_name = event.getData()
                self._invite_event = event
                self.global_config['_sip_logger'].write(
                    'recvEvent %s==>%s|%s' % (self.id, self.cli, self.cld))
                self.time_invite = int(round(time.time() * 1000))
                self.addRequest((self.cli, self.cld, '0', 'invite'))
            elif self.uaO != None:
                self.uaO.recvEvent(event)
        else:
            self.uaA.recvEvent(event)


class CallMap(object):
    global_config = None
    proxy = None
    # rc1 = None
    # rc2 = None

    def __init__(self, global_config):
        self.global_config = global_config
        self.proxy = StatefulProxy(
            global_config, self.global_config['nh_addr'])
        # gc.disable()
        # gc.set_debug(gc.DEBUG_STATS)
        # gc.set_threshold(0)
        # print gc.collect()

    def recvRequest(self, req, sip_t):
        if req.getHFBody('to').getTag() != None:
            # Request within dialog, but no such dialog
            return (req.genResponse(481, 'Call Leg/Transaction Does Not Exist'), None, None)
        if req.getMethod() == 'INVITE':
            # New dialog
            cc = CallController(self.global_config)
            return cc.uaA.recvRequest(req, sip_t)
        if req.getMethod() == 'REGISTER':
            # Registration
            return self.proxy.recvRequest(req)
        if req.getMethod() in ('NOTIFY', 'PING'):
            # Whynot?
            return (req.genResponse(200, 'OK'), None, None)
        print("==> Not Implemented", req)
        return (req.genResponse(501, 'Not Implemented'), None, None)


def main_func():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'fl:p:n:L:')
    except getopt.GetoptError:
        print(
            'usage: b2bua.py [-l addr] [-p port] [-n addr] [-f] [-L logfile]')
        sys.exit(1)
    laddr = None
    lport = None
    logfile = '/var/log/sippy.log'
    global_config = {'nh_addr': ['127.0.0.1', 5060]}
    foreground = False
    for o, a in opts:
        if o == '-f':
            foreground = True
            continue
        if o == '-l':
            laddr = a
            continue
        if o == '-p':
            lport = int(a)
            continue
        if o == '-L':
            logfile = a
        if o == '-n':
            if a.startswith('['):
                parts = a.split(']', 1)
                global_config['nh_addr'] = [parts[0] + ']', 5060]
                parts = parts[1].split(':', 1)
            else:
                parts = a.split(':', 1)
                global_config['nh_addr'] = [parts[0], 5060]
            if len(parts) == 2:
                global_config['nh_addr'][1] = int(parts[1])
            continue
    global_config['nh_addr'] = tuple(global_config['nh_addr'])

    if not foreground:
        daemonize(logfile)

    SipConf.my_uaname = 'vos 2.1.10'
    SipConf.allow_formats = (0, 8, 18, 100, 101)
    global_config['_sip_address'] = SipConf.my_address
    global_config['_sip_port'] = SipConf.my_port
    if laddr != None:
        global_config['_sip_address'] = laddr
    if lport != None:
        global_config['_sip_port'] = lport
    global_config['_sip_logger'] = SipLogger('b2bua')
    # global_config['_invite_session'] = FuturesSession(max_workers=200)
    global_config['_request_session'] = FuturesSession(max_workers=200)

    global_config['_sip_logger'].write(
        global_config['_sip_address'], ":", global_config['_sip_port'])

    cmap = CallMap(global_config)

    global_config['_sip_tm'] = SipTransactionManager(
        global_config, cmap.recvRequest)

    ED2.loop()


if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', True)
    main_func()
