### SS
docker run -dt --name ss -p 80:80 -p 443:443/udp mritd/shadowsocks -m "ss-server" -s "-s 0.0.0.0 -p 80 -m chacha20 -k bocai1222 --fast-open" -x -e "kcpserver" -k "-t 127.0.0.1:80 -l :443 -mode fast2"
### SSR
docker run --privileged -d -p 8008:8008/tcp -p 8008:8008/udp --name ssr-bbr-docker letssudormrf/ssr-bbr-docker -p 8008 -k bocai1222 -m rc4-md5 -O auth_aes128_md5 -o plain

### Tool
https://github.com/ShadowsocksR-Live/ssrMac
