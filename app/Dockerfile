FROM python:3.11-alpine

COPY requirements.txt /

RUN pip install -U pip setuptools

RUN pip install -r requirements.txt

COPY app.py /

WORKDIR /

CMD ["python", "app.py"]