# Сравниваем вакансии программистов

## vacancy_statistics.py

Утилита для анализа зарплат IT-вакансий с данных SuperJob и Habr Career.

**Как установить:**

- Должен быть установлен `Python` версии 3.10
- Используйте `pip` для установки зависимостей

```bash
pip install -r requirements.txt
```

**Запуск**

Получите токен на сайтe [SuperJob](https://api.superjob.ru/). Создайте `.env` файл в корне проекта и скопируйте содержимое из `.env.example в .env`. Вставьте ваш реальный токен в файл `.env`. Используйте `--help` для подсказки. Режимы работы программы `--mode{all, town} `, где *all* - это общие данные, *town* - данные для конкретного города. По умолчанию выставлен режим `{all}`. Загрузка данных занимает несколько минут.

**Пример ввода:**
- `python .\vacancy_statistics.py`
- `python .\vacancy_statistics.py --mode town --town Москва`

**Вывод:**

![img](https://i.ibb.co/GQ77nGL9/Stn-ZO1-XSFZZu-XUDVu-JL-Uz-YEa-Kcsb-JTZEVGiv-B-zc-Ua-XNYFPX96q-Jn-Uo-Yb1-GW0-MXnp7-Rjvd7-R9q-P0-Nb-Uav-Ewz.jpg)

**Цель проекта**

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org.](https://dvmn.org/)
