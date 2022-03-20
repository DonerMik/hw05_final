Yatube - соц. сеть для дневников. Использовалась MVT архитектура с применением пагинации постов, верификации данных, кеширования, восстановления пароля через почту. Написаны тесты проверяющие систему.

НАСТРОЙКА ПРОЕКТА:

1)Клонировать репозиторий и перейти в него в командной строке:

git clone https://github.com/account_name/hw05_final/

cd hw05_final

2)Cоздать и активировать виртуальное окружение:

python3 -m venv env

source env/bin/activate

3)Установить зависимости из файла requirements.txt:

python3 -m pip install --upgrade pip

pip install -r requirements.txt

4)Выполнить миграции:

python3 manage.py migrate

5)Запустить проект:

python3 manage.py runserver

Запустите проект по адресу http://127.0.0.1:8000/redoc/
