# Практическая работа по Git

После завершения каждого пункта, предполагается, что вы пушите все изменения в удалённый репозиторий.

1. Создайте новый репозиторий с названием по шаблону:

    `mlops-git-<your_surname>`

    Клонируйте удалённый репозиторий в локальный.

2. Создайте файл `app.py` с содержимым `print("Start app")` и сделайте первый коммит

3. Создайте ветку `feature/train` (от `main`)

4. Создайте ветку `feature/metrics` (от `main`)
    
    Добавьте файл `metrics.py` с содержимым `print("Compute my metric")`

    Добавьте в файл `app.py` строку `print("Print metric")`

5. Выполните слияние `feature/metrics` в `main`

6. В ветке `feature/train` добавьте файл `train.py` с содержимым `print("Train my model")`

    Сделайте 3 коммита:

    * Создайте файл `train.py` с содержимым `print("Model training")`
    * Измените `app.py` так:

            print("Start app")
            print("Train my model")
            print("Print metric")

    * Измените `app.py` так:

            print("Start app")
            print("Train my model")
            print("Some bug")
            print("Print metric")

7. Выполните слияние `feature/train` в `main` без бага в `app.py`, но что бы баг был виден в истории git.

8. В `main` добавьте в конец `app.py` строку `print("Metrics branch commit")`. Не делайте коммит. Перенесите изменения в `feature/metrics` и закомитьте.

9. В `feature/metrics` добавьте в конец `app.py` строку `print("Train branch commit")`. Сделайте коммит. Перенесите изменения в `feature/train`.

9. В `feature/metrics` в конец файла `metrics.py` добавьте отдельными коммитами:

    * `print("Good commit_1")`
    * `print("Bad commit_1")`
    * `print("Bad commit_2")`
    ....
    * `print("Bad commit_N")`

    Откатите плохие коммиты, сохранив `Good commit1`, таким образом, что бы плохие коммиты не засоряли историю git.

    P.S. N - очень большое число и ручное исправление займёт очень много времени.