# Docker для воспроизводимого обучения модели

Docker позволяет упаковать код, зависимости и настройки запуска в образ. Один
и тот же образ можно запустить на компьютере разработчика, в CI или на сервере,
если там доступен совместимый Docker Engine.

В этой практике контейнер выполняет конечную задачу: обучает модель Iris,
сохраняет модель и метрики, затем завершает работу.

## Основные понятия

| Понятие | Значение |
|---|---|
| Dockerfile | Текстовый файл с инструкциями сборки образа |
| Образ | Неизменяемый шаблон с файлами, зависимостями и настройками запуска |
| Контейнер | Запущенный экземпляр образа |
| Build context | Каталог файлов, доступных инструкциям `COPY` и `ADD` |
| Слой | Изменение файловой системы, сохранённое при сборке образа |
| Registry | Хранилище образов, например Docker Hub |
| Volume | Хранилище данных под управлением Docker |
| Bind mount | Прямое подключение каталога хоста к контейнеру |

Образ и контейнер не являются одним объектом. Команда `docker build` создаёт
образ. Команда `docker run` создаёт из образа новый контейнер и запускает в нём
процесс.

## Файлы практики

```text
practice_5/
  Dockerfile
  .dockerignore
  requirements.txt
  requirements-dev.txt
  train_model.py
  docker.ipynb
  explained.md
  docker_practice.md
  tests/
    test_training.py
```

`requirements.txt` содержит только библиотеки, необходимые внутри образа.
`requirements-dev.txt` дополнительно содержит инструменты для notebook и
тестов. Благодаря этому в рабочий образ не устанавливаются `pytest`, Jupyter и
другие инструменты разработки.

## Скрипт обучения

`train_model.py` выполняет следующие операции:

1. читает параметры из переменных окружения;
2. загружает набор Iris;
3. делит данные на train и test со стратификацией;
4. обучает `RandomForestClassifier`;
5. сохраняет модель в `iris_random_forest.joblib`;
6. сохраняет параметры и метрики в `metrics.json`.

Доступные переменные:

| Переменная | Значение по умолчанию | Назначение |
|---|---:|---|
| `MODEL_DIR` | каталог `models` рядом со скриптом | Каталог результатов |
| `MODEL_VERSION` | `1.0.0` | Версия модели в метаданных |
| `N_ESTIMATORS` | `100` | Количество деревьев |
| `TEST_SIZE` | `0.3` | Доля тестовой выборки |
| `RANDOM_STATE` | `42` | Seed для воспроизводимости |

При локальном запуске результаты появляются в `practice_5/models`. В образе
`MODEL_DIR` переопределён значением `/app/models`.

## Разбор Dockerfile

### Синтаксис Dockerfile

```dockerfile
# syntax=docker/dockerfile:1
```

Первая строка выбирает актуальную стабильную версию синтаксиса Dockerfile 1
для BuildKit.

### Базовый образ

```dockerfile
FROM python:3.12-slim
```

`FROM` начинает этап сборки и задаёт исходную файловую систему. Тег `3.12-slim`
фиксирует версию Python и выбирает уменьшенный Debian-based образ. Использование
одного `latest` не фиксирует версию окружения.

### Аргументы сборки и метки

```dockerfile
ARG BUILD_DATE=unknown
ARG VCS_REF=unknown

LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}"
```

`ARG` существует во время сборки. Значения передаются через `--build-arg`.
`LABEL` сохраняет метаданные в образе. Токены и пароли нельзя передавать через
`ARG`: они могут попасть в историю сборки и provenance.

Область видимости `ARG` зависит от расположения. Аргумент перед первым `FROM`
можно использовать в самом `FROM`, но он не становится автоматически доступен
внутри этапа:

```dockerfile
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim
ARG PYTHON_VERSION
RUN echo "Python version: ${PYTHON_VERSION}"
```

Повторный `ARG PYTHON_VERSION` после `FROM` делает значение доступным для
последующих инструкций этого этапа.

### Переменные контейнера

```dockerfile
ENV MODEL_DIR=/app/models \
    N_ESTIMATORS=100 \
    TEST_SIZE=0.3 \
    RANDOM_STATE=42
```

`ENV` сохраняется в образе и доступен при запуске контейнера. Значение можно
переопределить флагом `-e`:

```bash
docker run --rm -e N_ESTIMATORS=200 miit-iris-trainer:1.0
```

`ARG` используется для сборки, `ENV` для настройки запуска. Секреты не следует
записывать ни в `ARG`, ни в `ENV` Dockerfile.

### Рабочий каталог

```dockerfile
WORKDIR /app
```

`WORKDIR` задаёт текущий каталог для следующих `RUN`, `COPY`, `CMD` и
`ENTRYPOINT`. Абсолютный путь устраняет зависимость от настроек базового образа.

### Установка зависимостей и кэш

```dockerfile
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY train_model.py ./
```

Зависимости копируются раньше исходного кода. Если изменился только
`train_model.py`, Docker может повторно использовать слой с установленными
библиотеками. Если сначала выполнить `COPY . .`, любое изменение проекта может
сбросить кэш установки зависимостей.

Флаг `--no-cache-dir` относится к кэшу `pip` внутри образа. Он не выключает
кэш сборки Docker. Полная сборка без Docker cache запускается командой
`docker build --no-cache ...`.

### Непривилегированный пользователь

```dockerfile
RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid 10001 --no-log-init --create-home appuser

USER 10001:10001
```

По умолчанию процесс в контейнере запускается от `root`. Здесь создаётся
отдельный пользователь с фиксированными UID и GID. До переключения пользователя
каталог `/app/models` создаётся и передаётся ему через `chown`.

### Команда запуска

```dockerfile
CMD ["python", "train_model.py"]
```

`CMD` не выполняется во время `docker build`. Команда запускается только при
создании контейнера. Аргументы после имени образа полностью заменяют `CMD`:

```bash
docker run --rm miit-iris-trainer:1.0 python --version
```

В этом контейнере выполнится `python --version`, а обучение не запустится.

## RUN, CMD и ENTRYPOINT

| Инструкция | Когда работает | Назначение |
|---|---|---|
| `RUN` | Во время сборки | Устанавливает пакеты или изменяет файлы образа |
| `CMD` | При запуске контейнера | Задаёт команду или аргументы по умолчанию |
| `ENTRYPOINT` | При запуске контейнера | Фиксирует основной исполняемый файл |

Для сочетания `ENTRYPOINT` и `CMD` рекомендуется exec form:

```dockerfile
ENTRYPOINT ["python", "train_model.py"]
CMD ["--help"]
```

Аргументы `docker run image ...` заменяют `CMD` и добавляются к exec form
`ENTRYPOINT`. Сам `ENTRYPOINT` можно переопределить флагом `--entrypoint`:

```bash
docker run --rm --entrypoint python image:tag --version
```

Поэтому утверждение, что `ENTRYPOINT` невозможно заменить, неверно.

## Слои и история образа

`RUN`, `COPY` и `ADD` обычно создают изменения файловой системы. `CMD`,
`ENTRYPOINT`, `ENV`, `EXPOSE`, `LABEL` и `USER` в основном меняют конфигурацию
образа. Не каждая строка Dockerfile добавляет содержательный слой с файлами.

Удаление файла в следующем `RUN` не убирает его из предыдущего слоя. Поэтому
установка пакетов и очистка временных файлов выполняются в одной инструкции:

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
```

Историю сборки можно посмотреть командой:

```bash
docker image history miit-iris-trainer:1.0
```

## Контекст сборки и .dockerignore

Последняя точка в команде является контекстом сборки:

```bash
docker build -t miit-iris-trainer:1.0 .
```

`COPY` может читать только файлы из этого каталога. `.dockerignore` исключает
Git metadata, виртуальные окружения, кэши, notebook, тесты и обученные модели.
Это уменьшает контекст и не позволяет случайно отправить лишние файлы Docker
daemon.

`.dockerignore` не заменяет `.gitignore`. Первый управляет контекстом Docker,
второй управляет файлами Git.

## COPY и ADD

`COPY` переносит локальные файлы из контекста в образ. Для обычного копирования
следует использовать именно `COPY`.

`ADD` дополнительно умеет распаковывать локальные tar-архивы и принимать
удалённые источники. Используйте его только тогда, когда требуется эта
дополнительная семантика.

## EXPOSE и публикация порта

`EXPOSE 8000` документирует, что процесс ожидает соединения на порту `8000`,
но не открывает порт на хосте. Публикация выполняется при запуске:

```bash
docker run --rm -p 127.0.0.1:8000:8000 image:tag
```

Первое число является портом хоста, второе портом контейнера. Обучающий
контейнер этой практики не запускает HTTP-сервис, поэтому ему не нужны
`EXPOSE` и `-p`.

## Постоянное хранение результатов

Файлы внутри writable layer контейнера удаляются вместе с контейнером. Модель и
метрики необходимо сохранять во внешнее хранилище.

Именованный volume создаётся и подключается так:

```bash
docker volume create miit-iris-models

docker run --rm \
  --mount type=volume,source=miit-iris-models,target=/app/models \
  miit-iris-trainer:1.0
```

После завершения контейнера volume остаётся. Его содержимое можно проверить
через тот же образ:

```bash
docker run --rm \
  --mount type=volume,source=miit-iris-models,target=/app/models \
  --entrypoint sh \
  miit-iris-trainer:1.0 \
  -c "ls -l /app/models && cat /app/models/metrics.json"
```

Bind mount подключает конкретный каталог хоста. Для PowerShell:

```powershell
New-Item -ItemType Directory -Force models

docker run --rm `
  --mount "type=bind,source=$((Resolve-Path models).Path),target=/app/models" `
  miit-iris-trainer:1.0
```

Именованный volume удобен для хранения данных под управлением Docker. Bind
mount удобен, когда файлы должны сразу появиться в выбранном каталоге хоста.
Для новых команд предпочтительнее явный синтаксис `--mount`, хотя `-v` также
поддерживается.

## Инструкция VOLUME

`VOLUME ["/app/models"]` объявляет предполагаемую точку монтирования, но не
задаёт каталог хоста. Без явного `--mount` Docker может создать анонимный
volume.

Legacy builder отбрасывает изменения, внесённые в объявленный volume
последующими шагами сборки. BuildKit сохраняет такие изменения. Не следует
строить Dockerfile на различии этих режимов: подготовьте содержимое до
`VOLUME` или подключайте хранилище только при `docker run`.

В Dockerfile практики инструкция `VOLUME` не используется. Точка хранения
задаётся явно через `--mount` в команде запуска.

## Сборка и запуск практики

Откройте терминал в `practice_5`.

Локальная проверка Python:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python train_model.py
```

Сборка образа:

```bash
docker build \
  --build-arg BUILD_DATE=2026-11-10 \
  --build-arg VCS_REF=local \
  -t miit-iris-trainer:1.0 .
```

Запуск с volume и изменённым количеством деревьев:

```bash
docker volume create miit-iris-models

docker run --rm \
  --mount type=volume,source=miit-iris-models,target=/app/models \
  -e N_ESTIMATORS=200 \
  miit-iris-trainer:1.0
```

Проверка пользователя и конфигурации образа:

```bash
docker image inspect miit-iris-trainer:1.0
docker run --rm --entrypoint id miit-iris-trainer:1.0
```

## Типовые ошибки

### Docker CLI есть, Engine недоступен

Команда `docker version` показывает секцию Client, но завершается ошибкой
подключения. Запустите Docker Desktop или Docker daemon и повторите проверку.

### COPY не находит файл

Проверьте текущий каталог, путь контекста в `docker build` и правила
`.dockerignore`. Файл за пределами build context скопировать нельзя.

### Результаты исчезли

Контейнер был запущен без volume или bind mount. Файлы остались в writable
layer удалённого контейнера.

### Permission denied в /app/models

Пользователь контейнера не имеет права записи в подключённый каталог. Для bind
mount проверьте права каталога хоста. Для volume проверьте владельца каталога в
образе и UID процесса.

### Изменение переменной не влияет на сборку

Уточните, где она нужна. `ARG` передаётся при `docker build`, `ENV` или `-e`
используются при `docker run`.

## Официальная документация

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Build cache optimization](https://docs.docker.com/build/cache/optimize/)
- [Volumes](https://docs.docker.com/engine/storage/volumes/)
- [Bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)
- [Building best practices](https://docs.docker.com/build/building/best-practices/)
