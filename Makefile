# Makefile для Python проекта

# Определите переменные для лучшей читаемости и удобства использования
PYTHON = python
PIP = pip
FLASK_APP = app.py

# Установка всех зависимостей из файла requirements.txt
install:
    $(PIP) install -r requirements.txt

# Запуск вашего Flask приложения
run:
    $(PYTHON) $(FLASK_APP)

# Очистка кэша Python и других временных файлов
clean:
    find . -type f -name '*.pyc' -delete
    find . -type d -name '__pycache__' -delete