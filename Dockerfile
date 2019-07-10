FROM python:3
COPY ./ws_parser ./
RUN pip install -r requirements.txt
