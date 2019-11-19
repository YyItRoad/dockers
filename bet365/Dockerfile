FROM markadams/chromium-xvfb-py3:latest

COPY . /usr/src/app

RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /usr/src/app

ENTRYPOINT [ "python3" ]

EXPOSE 8066

CMD [ "./bet365_if_yy.py" ]