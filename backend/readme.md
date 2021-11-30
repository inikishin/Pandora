## Database

На данном этапе используем контейнеризацию СУБД. База будет храниться в отдельном volume. 
В папках проекта базу не храним.

### !!! Необходимо сделать скрипт создания резервной копии и выкладывание его на Google Drive !!!

###Работа с Volume
* Создание нового volume: `docker volume create pandora-db`
* Определение свойств volume: `docker volume inspect pandora-db`
* Опция подключения volume при создании контейнера: `--mount type=volume,source=pandora-db,target=/var/lib/postgresql/data/pgdata`

###Создание нового контейнера
Команда создания контейнера принимает следующие параметры:

* Присваиваем имя контейнеру `pandora-db`
* Пробрасываем порт `5432`
* Задаем админский пароль к БД
* Указываем имя базы данных, создаваемой при инициализации `pandora`
* Указываем папку, в которой будет храниться база в контейнере `/var/lib/postgresql/data/pgdata`
* Маунтим volume
* Указываем имя образа `postgres`

Опционально можно не привязывать volume, а дать ссылку на конкретную локальную папку на хосте. Для этого вместо 
опции `--mount` указывается следующая опция `-v "/home/darkstorn/PycharmProjects/pandora/Pandora/backend/db":/var/lib/postgresql/data`,
где в кавычках указывается абсолютный путь к каталогу на хосте.

```commandline
sudo docker run --name pandora-db \
                -p 5432:5432 \
                -e POSTGRES_PASSWORD=pass \
                -e POSTGRES_DB=pandora \
                -e PGDATA=/var/lib/postgresql/data/pgdata \
                -d \
                --mount type=volume,source=pandora-db,target=/var/lib/postgresql/data/pgdata \
                postgres
```

###Запуск созданного контейнера
Запускаем командой `sudo docker container start pandora-db`

###Запуск celery
Запускаем контейнер redis `sudo docker container start celery-brocker`
Запускаем воркера celery `celery -A backend worker -l INFO`