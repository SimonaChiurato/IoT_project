FROM python:3.10-alpine
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "./TelegramBot.py", "192.168.1.8:8087"]
