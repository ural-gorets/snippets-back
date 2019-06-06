Для запуска проекта необходимо:

1. Установить пакеты Python из списка в requirements.txt
2. Содать пустую базу данных postgresql.
3. Прописать параметры подключения к ней:
    run.py
      class Config(Object):
        SQLALCHEMY_DATABASE_URI = "postgresql://<пользователь>:<пароль>@<url>:<порт>/<имя БД>"
        например: SQLALCHEMY_DATABASE_URI = "postgresql://test_task:qwerty@localhost:5432/db"
4. Создать структуру базы через миграцию.
    Запустить команду: python manage.py db migrate
        Будет создан файл миграции: ./migrations/versions/xxxxxxxxxx_.py
        На следующем шаге будет выполнен код из функции Upgrade этого файла.
    Запустить команду: python manage.py db upgrade
5. Для старта сервера под Linux запустить файл run_lin.
