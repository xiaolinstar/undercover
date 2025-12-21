FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -i https://mirrors.tencent.com/pypi/simple --upgrade pip
RUN pip install --no-cache-dir -i https://mirrors.tencent.com/pypi/simple -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.main:app", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info"]
