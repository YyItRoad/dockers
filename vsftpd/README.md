```
docker run -d -v ~/files:/home/vsftpd \
-p 20:20 -p 21:21 -p 21100-21110:21100-21110 \
-e FTP_USER=admin -e FTP_PASS=123456 \
-e PASV_ADDRESS=192.168.110.20 -e PASV_MIN_PORT=21100 -e PASV_MAX_PORT=21110 \
--name vsftpd --restart=always fauria/vsftpd
```

`FTP_USER` 用户名

`FTP_PASS` 密码

`PASV_ADDRESS`需要替换为主机ip