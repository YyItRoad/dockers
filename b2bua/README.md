### 添加接口请求

创建镜像`docker build -t b2bua:1.0 .`

git clone https://github.com/sobomax/libelperiodic.git && cd libelperiodic/ && ./configure && make && make install && ldconfig && export LD_LIBRARY_PATH=/usr/local/lib && pip3 install .

pip3 install git+https://github.com/sobomax/libelperiodic

pip install

b2bua -l 144.202.10.54 -L "/root/b2bua/log/sippy.log"

b2bua -L "/root/b2bua/log/sippy.log"

docker run -p 4160:4160/udp --name b2bua -v $PWD/b2bua:/root/b2bua --restart=always -d b2bua:1.0
