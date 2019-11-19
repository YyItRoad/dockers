const {
    Wechaty, log
} = require('wechaty')
const qrTerm = require('qrcode-terminal')
const express = require('express');
const app = express();
const bot = new Wechaty();
const SecretKey = '';

bot.on('scan', onScan)
bot.on('login', onLogin)
bot.on('message', onMessage)
bot.on('logout', onLogout)
bot.on('error', onError)

bot.start().catch(log.error());

function onScan (qrcode, status) {
    qrTerm.generate(qrcode, { small: true })  // show qrcode on console
}

function onLogin (user) {
    log.info(`${user} login`)
}

function onMessage (msg) {
    if (msg.type() === bot.Message.Type.Text) {
        //log.info(`${msg.from()}->${msg.room() || msg.to()}:${msg.text()}`);
    }
}

function onLogout (user) {
    log.info(`${user} logout`)
}

function onError (e) {
    log.error(e)
}

async function find (name = '文件传输助手', room = false) {
    try {
        let user;
        if (room) {
            user = await bot.Room.find({ topic: name });
        } else {
            user = await bot.Contact.find({ name });
        }
        return user;
    } catch (error) {
        log.error(error);
    }
}

async function sendMsg (to, msg, group) {
    let user = await find(to, group == 1);
    if (user && msg && msg.length > 0) {
        log.info(`${user} -> ${msg}`);
        return user.say(msg)
    } else {
        return '用户不存在';
    }
}


app.get('/', function (req, res) {
    res.send('hello world');
});

app.get('/send', async function (req, res) {
    if (req.query.key === SecretKey) {
        res.send(await sendMsg(req.query.name, req.query.msg, req.query.group));
    } else {
        res.redirect('/');
    }
});

app.listen(3000, (res) => {
    log.info('wechat listen on 3000');
});
