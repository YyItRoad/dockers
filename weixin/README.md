### 使用Docker部署
docker pull zixia/wechaty:latest

需要安装`express`

`docker run -it -p 8000:3000 -e TZ="Asia/Shanghai" --name wechaty -v $PWD:/bot zixia/wechaty:latest bot.js`

然后Ctrl+P+Q即可退出控制台，但是容器没有退出，可使用命令查看