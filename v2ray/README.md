docker pull v2ray/official

docker run -d --name v2ray -v $PWD/v2ray:/etc/v2ray -p 8080:8080 v2ray/official  v2ray -config=/etc/v2ray/config.json