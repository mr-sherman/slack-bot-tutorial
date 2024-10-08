FROM python:3.12

WORKDIR /python-docker

COPY ./magic-eightball.py magic-eightball.py
COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

CMD [ "python3", "-u" , "magic-eightball.py"]%
