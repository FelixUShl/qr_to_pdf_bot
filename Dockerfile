FROM python:3-alpine

COPY . .

WORKDIR .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]