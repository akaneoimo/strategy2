FROM python:3.7

WORKDIR /app

COPY requirements.txt .

RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["./start.sh"]