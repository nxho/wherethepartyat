FROM python:3.11.4-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p static/uploads

CMD [ "python", "./upload-service.py" ]
