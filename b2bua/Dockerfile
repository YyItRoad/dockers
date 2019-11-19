FROM python

WORKDIR  /root/b2bua

COPY . /root/b2bua

RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

RUN git clone https://github.com/sobomax/libelperiodic.git && cd libelperiodic/ && ./configure && make && make install && ldconfig && export LD_LIBRARY_PATH=/usr/local/lib  && pip3 install .

RUN pip install /root/b2bua

EXPOSE 5060/udp

CMD ["/bin/bash", "run.sh"]