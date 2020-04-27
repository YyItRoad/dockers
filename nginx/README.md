### 拉取最新镜像
docker pull nginx:latest

### 部署服务
docker run -p 80:80 -p 443:443 --name nginx -v $PWD/nginx/www:/www -v $PWD/nginx/ssl:/etc/nginx/ssl/ -v $PWD/nginx/conf/nginx.conf:/etc/nginx/nginx.conf -v $PWD/nginx/logs:/logs -d nginx  
