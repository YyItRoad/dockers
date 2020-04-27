# dockers
## Centos7 安装
```
curl -sSL https://get.docker.com/ | sh
sudo systemctl enable docker
sudo systemctl start docker
 ```
 ## Dockerfile时区修改
```
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
```
### [1.bet365自动下注](./bet365/README.md)

### [2.微信机器人](./weixin/README.md)

### [3.b2bua-python](./b2bua/README.md)

### [3.opensips-b2bua](./opensips/README.md)

### [4.freeswitch](./freeswitch/README.md)

### [5.nginx](./nginx/README.md)