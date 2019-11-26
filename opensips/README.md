### 1.创建镜像目前
`docker build -t opensips:3.0 .`

### 2.运行容器
`docker run -p 5060:5060/udp -d --name opensips -e TZ="Asia/Shanghai" -v $PWD/opensips:/etc/opensips/ opensips/opensips:3.0`