FROM python

WORKDIR /main

COPY . /main

RUN pip install telebot pybit pycryptodome


CMD [ "python3", "main.py" ]