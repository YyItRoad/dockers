[FreeSwitch控制台以及ESL常用命令/API命令大全](https://wsonh.com/article/93.html)

### 1. 安装部署
`docker run -p 5060:5060/udp --name fs -e TZ="Asia/Shanghai" --restart=always -v $PWD/freeswitch/:/etc/freeswitch -d -t safarov/freeswitch:1.8.5`

### 2.配置信息
1. 基本参数`vars.xml`
2. 创建落地`sip_profiles/external`
3. DialPlan`dialplan/public`
4. acl配置`autoload_configs/acl.conf.xml`
5. modules配置`autoload_configs/modules.conf.xml`
6. cps配置`autoload_configs/switch.conf.xml`
   1. 内核数据库配置为sqlite内存`<param name="core-db-dsn" value="sqlite://:memory:" />`
7. socket配置`autoload_configs/event_socket.conf.xml `

### 3.常用命令
1. 状态`sofia status`
2. 系统参数`global_getvar`
3. 日志级别`console loglevel 4`
4. 开启或关闭Sip的SDP信息`sofia profile internal siptrace on / off` 

### 4.esl
1. 外呼`originate sofia/external/${called}@${vos_ip} &echo XML default test ${caller}`
2. 播放录音`{ignore_early_media=true,batch_id=100005,called_num=15545330724,action=playback}sofia/external/771115545330724@118.190.148.109 &playback(/etc/freeswitch/file_records/games/card_20191125_16.wav) XML default test 128888815`
3. 铃音录制`{ignore_early_media=false,batch_id=100001,called_num=15545330724,action=playback}sofia/external/771115545330724@118.190.148.109 &record(/etc/freeswitch/file_records/games/card_20191125_16.wav) XML default test 128888815`
4. 呼叫参数
   1. 早期媒体(运营商声音)`ignore_early_media=false`
   2. 配置语音编码`absolute_codec_string=PCMA`
5. Inbound
   状态过滤
    ```js
    conn.filter("Event-Name", "CHANNEL_HANGUP");
    conn.subscribe('all');
    conn.on("esl::event::**", function (event) {});
    ```
6. OutBound

### 5.抓包工具sngrep
sngrep port 5060

`vi /etc/yum.repos.d/irontec.repo`

```js
[irontec]
name=Irontec RPMs repository
baseurl=http://packages.irontec.com/centos/$releasever/$basearch/
```
`rpm --import http://packages.irontec.com/public.key`
`yum install sngrep`
