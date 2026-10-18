# Управление экспериментами с MLflow и ClearML

Обучение модели редко ограничивается одним запуском. Меняются данные,
гиперпараметры, код и версии библиотек. Если результаты записаны только в
консоль или notebook, сравнить запуски и воспроизвести лучший вариант трудно.

Система управления экспериментами хранит параметры запуска, метрики, файлы и
сведения о модели в одной структуре. В этой практике используются MLflow и
ClearML.

## Что считается воспроизводимым запуском

Для запуска должны быть известны:

- версия кода;
- версия данных или способ их получить;
- схема разделения на train, validation и test;
- случайное зерно;
- гиперпараметры модели;
- версии зависимостей;
- итоговые метрики;
- сохранённая модель;
- формат входных данных модели.

Одной метрики недостаточно. Значение `accuracy = 0.91` бесполезно, если нельзя
определить, на каких данных и с какими параметрами оно получено.

## Experiment и run

Experiment объединяет запуски одной задачи. Например, все попытки построить
классификатор для набора Wine можно хранить в одном experiment.

Run описывает один конкретный запуск. У него есть собственные параметры,
метрики, теги и артефакты.

| Сущность | Пример |
|---|---|
| Experiment | `wine-classification` |
| Run | обучение Random Forest с `max_depth=8` |
| Parameter | `max_depth=8` |
| Metric | `f1_weighted=0.94` |
| Tag | `model_family=random_forest` |
| Artifact | модель, график или JSON-отчёт |

Параметр задаётся до обучения и описывает конфигурацию. Метрика получается в
результате вычисления. Тег нужен для поиска и группировки. Артефакт является
файлом, который относится к запуску.

# MLflow

## Tracking URI

Tracking URI определяет, куда MLflow записывает информацию о запусках.

Для локальной работы без отдельного сервера можно использовать SQLite:

```python
import mlflow

mlflow.set_tracking_uri("sqlite:///mlflow.db")
```

Файл `mlflow.db` содержит метаданные experiments и runs. Артефакты моделей
сохраняются рядом в локальной директории MLflow. Такой режим подходит для
обучения и проверки кода на одном компьютере.

В актуальных версиях MLflow старый файловый tracking backend находится в режиме
сопровождения. Для новой практики следует использовать SQLite.

Для совместной работы можно запустить Tracking Server:

```bash
mlflow server --host 127.0.0.1 --port 8080
```

Клиент должен использовать тот же адрес и порт:

```python
mlflow.set_tracking_uri("http://127.0.0.1:8080")
```

Если сервер запущен на `8080`, обращение к `9090` завершится ошибкой соединения.

## Создание эксперимента

Повторный вызов `create_experiment` с существующим именем завершится ошибкой.
Для notebook удобнее сначала проверить наличие эксперимента:

```python
experiment_name = "wine-classification"
experiment = mlflow.get_experiment_by_name(experiment_name)

if experiment is None:
    experiment_id = mlflow.create_experiment(experiment_name)
else:
    experiment_id = experiment.experiment_id
```

`experiment_id` является строковым идентификатором. В `start_run` нужно
передавать именно его, а не объект `Experiment`.

## Ручное логирование

Ручное логирование делает состав запуска явным:

```python
with mlflow.start_run(experiment_id=experiment_id, run_name="logreg-c1"):
    mlflow.log_param("C", 1.0)
    mlflow.log_metric("f1_weighted", 0.93)
    mlflow.set_tag("model_family", "logistic_regression")
```

Несколько параметров и метрик можно записать словарями:

```python
mlflow.log_params({"C": 1.0, "max_iter": 500})
mlflow.log_metrics({"accuracy": 0.92, "f1_weighted": 0.91})
```

Названия должны быть одинаковыми во всех сравниваемых запусках. Если один run
записывает `f1`, а другой `f1_score`, сортировка потребует дополнительной
обработки.

## Autolog

MLflow умеет автоматически собирать параметры и часть метрик:

```python
mlflow.sklearn.autolog()
```

Autolog сокращает код, но не отменяет проектирование эксперимента. Нужно заранее
решить, какие метрики определяют качество и какие артефакты потребуются для
проверки результата.

В учебной работе полезно сначала выполнить ручное логирование. Так видно, какие
данные попадают в систему и почему.

## Логирование модели

Модель следует сохранять вместе со схемой входа и примером данных:

```python
from mlflow.models import infer_signature

signature = infer_signature(X_train, model.predict(X_train))
mlflow.sklearn.log_model(
    sk_model=model,
    artifact_path="model",
    signature=signature,
    input_example=X_train.iloc[:5],
)
```

Signature фиксирует имена и типы входных столбцов, а также структуру выхода.
Это позволяет раньше обнаружить несовместимый запрос к модели.

## Поиск запусков

Запуски одного experiment можно получить как таблицу:

```python
runs = mlflow.search_runs(
    experiment_ids=[experiment_id],
    order_by=["metrics.f1_weighted DESC"],
)
```

Каждая строка соответствует одному run. Параметры доступны в столбцах с
префиксом `params.`, метрики с префиксом `metrics.`, теги с префиксом `tags.`.

Лучший run выбирают по метрике validation. Test используют после выбора
конфигурации. Если постоянно выбирать модель по test, test перестаёт быть
независимой оценкой.

## Загрузка модели

Модель можно загрузить по идентификатору run:

```python
model_uri = f"runs:/{run_id}/model"
loaded_model = mlflow.sklearn.load_model(model_uri)
predictions = loaded_model.predict(X_test)
```

После загрузки нужно проверить не только отсутствие ошибки, но и совпадение
предсказаний на фиксированном наборе данных.

## Артефакты

Артефактами могут быть:

- сериализованная модель;
- матрица ошибок;
- таблица предсказаний;
- JSON с результатами;
- график обучения;
- описание набора данных.

В артефакты не следует помещать credentials, локальные конфигурации и файлы,
содержащие персональные данные без разрешения.

## Подбор гиперпараметров

Каждую проверяемую конфигурацию нужно хранить как отдельный run. Тогда таблица
запусков показывает связь между параметрами и результатом.

Пример цикла:

```python
for max_depth in [3, 6, 9]:
    with mlflow.start_run(experiment_id=experiment_id):
        mlflow.log_param("max_depth", max_depth)
        model = train_model(max_depth=max_depth)
        mlflow.log_metric("f1_weighted", evaluate(model))
```

Для небольшого учебного поиска обычного цикла достаточно. GridSearchCV или
Optuna нужны, когда они решают отдельную задачу, а не скрывают логику практики.

# ClearML

## Подключение

Рекомендуемый способ настройки SDK:

```bash
clearml-init
```

Команда создаёт пользовательскую конфигурацию вне репозитория.

Можно использовать переменные окружения. В PowerShell:

```powershell
$env:CLEARML_WEB_HOST="https://app.clear.ml"
$env:CLEARML_API_HOST="https://api.clear.ml"
$env:CLEARML_FILES_HOST="https://files.clear.ml"
$env:CLEARML_API_ACCESS_KEY="YOUR_CLEARML_ACCESS_KEY"
$env:CLEARML_API_SECRET_KEY="YOUR_CLEARML_SECRET_KEY"
```

Подставьте свои ключи вместо `YOUR_CLEARML_ACCESS_KEY` и
`YOUR_CLEARML_SECRET_KEY`. Не сохраняйте заполненные команды в notebook,
исходном коде или Git.

## Task

Основная сущность ClearML называется Task. Она соответствует одному запуску:

```python
from clearml import Task

task = Task.init(
    project_name="MIIT/MLOps/practice_4/ivanov",
    task_name="random-forest-depth-8",
    reuse_last_task_id=False,
)
```

После создания Task можно подключить параметры:

```python
params = {"max_depth": 8, "n_estimators": 200}
task.connect(params, name="model")
```

## Метрики и артефакты

Одиночное итоговое значение:

```python
logger = task.get_logger()
logger.report_single_value("f1_weighted", 0.94)
```

Значения по итерациям:

```python
logger.report_scalar(
    title="validation",
    series="f1_weighted",
    iteration=1,
    value=0.94,
)
```

Файл или объект можно загрузить как артефакт:

```python
task.upload_artifact("evaluation", artifact_object="evaluation.json")
```

В конце локального запуска Task нужно закрыть:

```python
task.close()
```

## Модель в ClearML

Файл модели можно связать с Task через `OutputModel`:

```python
from clearml import OutputModel

output_model = OutputModel(
    task=task,
    framework="scikit-learn",
    name="wine-classifier",
)
output_model.update_weights(weights_filename="model.joblib")
output_model.publish()
```

`publish()` делает модель опубликованной версией. Вызывать его следует после
проверки файла и метрик.

# Сравнение MLflow и ClearML

| Возможность | MLflow | ClearML |
|---|---|---|
| Локальный старт без сервера | SQLite tracking URI | Offline mode, но обычная работа рассчитана на server |
| Experiment tracking | Да | Да |
| Хранение моделей | Model artifacts и registry | OutputModel и model registry |
| Датасеты | Не основной компонент Tracking | ClearML Dataset |
| Агенты и очереди | Не основной компонент | Встроены в платформу |
| Подключение кода | Явные вызовы и autolog | Task и auto-connect |

Выбор системы зависит от инфраструктуры. Для практики важно понять общие
сущности: запуск, параметры, метрики, артефакты и модель.

# Типовые ошибки

## Разные порты

Tracking Server и `set_tracking_uri` должны использовать один порт. Проверьте
команду запуска и значение URI.

## Несуществующий experiment

`get_experiment_by_name` возвращает `None`, если experiment не найден. Перед
обращением к `experiment_id` обработайте этот случай.

## Объект вместо ID

`start_run(experiment_id=...)` ожидает идентификатор, а не объект experiment.

## Зависимость от порядка запуска ячеек

Notebook должен выполняться сверху вниз после перезапуска kernel. Ячейка не
должна использовать переменную, которая была создана только при старом запуске.

## Credentials в notebook

Credentials из source и outputs попадают в файл `.ipynb`. Используйте
`clearml-init` или переменные окружения, установленные вне notebook.

## Непроверенная загрузка модели

Факт загрузки не доказывает эквивалентность. Сравните предсказания исходной и
загруженной модели на одном наборе.

# Минимальная проверка эксперимента

Перед сдачей убедитесь, что:

- notebook выполняется сверху вниз в чистом kernel;
- каждый run содержит параметры и одинаковый набор метрик;
- случайное зерно зафиксировано;
- лучшая конфигурация выбирается по validation;
- модель загружается по URI или ID;
- предсказания после загрузки совпадают;
- credentials отсутствуют в репозитории;
- отчёт содержит идентификаторы запусков и обоснование выбора модели.
