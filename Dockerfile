FROM python:3

RUN apt-get update && apt-get install -y pdftk

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./fahrgastrechte.py" ]
