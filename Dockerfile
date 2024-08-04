# Используем базовый образ Python
FROM python:3.9

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта в контейнер
COPY . .

# Опционально: устанавливаем переменные окружения
ENV TELEGRAM_TOKEN=your_token
ENV CHAT_ID=your_chat_id
ENV HOST=your_host
ENV PORT=your_port
ENV USER=your_user
ENV PASSWORD=your_password
ENV DB_NAME=your_db_name
ENV DB_USER=your_db_user
ENV DB_PASSWORD=your_db_password
ENV DB_HOST=your_db_host
ENV DB_PORT=your_db_port

# Запускаем бота при старте контейнера
CMD ["python", "main.py"]
