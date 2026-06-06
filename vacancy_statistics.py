import os
import requests
import time
import temp_text
import argparse
from terminaltables import AsciiTable
from dotenv import load_dotenv


def get_sj_vacancy_data(sj_token, keyword, area_id):
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {"X-Api-App-Id": sj_token}
    DEVELOPMENT_CATEGORY_ID = 33
    vacancy_sj_data = []
    page = 0
    while True:
        params = {
            "page": page,
            "count": 100,
            "town": area_id,
            "catalogues": DEVELOPMENT_CATEGORY_ID,
            "keyword": f"{keyword} программист",
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        loaded_page = response.json()
        if not loaded_page["objects"]:
            break
        vacancy_sj_data.extend(loaded_page["objects"])
        temp_text.prnt(f"🔄 Загрузка данных с SuperJob для {keyword}...")
        page += 1
        time.sleep(0.5)
    return vacancy_sj_data


def get_hbr_vacancy_data(language, area_id):
    page = 1
    vacancy_hbr_data = []
    url = "https://career.habr.com/api/frontend/vacancies"
    while True:
        params = {
            "q": language,
            "page": page,
            "locations[]": area_id,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        page_payload = response.json()
        vacancy_hbr_data.append(page_payload)
        total_pages = page_payload["meta"]["totalPages"]
        if page >= total_pages or total_pages == 0:
            break
        temp_text.prnt(f"🔄 Загрузка данных с Habr для {language}...")
        page += 1
        time.sleep(0.5)
    return vacancy_hbr_data


def get_sj_area_id(sj_token, town):
    url = "https://api.superjob.ru/2.0/towns/"
    params = {
        "keyword": town
    }
    headers = {"X-Api-App-Id": sj_token}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    area_sj_id = response.json()["objects"]
    if not area_sj_id:
        area_sj_id = None
    else:
        area_sj_id = response.json()["objects"][0]["id"]
    return area_sj_id


def get_hbr_area_id(town):
    url = "https://career.habr.com/api/frontend/suggestions/locations"
    params = {
        "term": town
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    if not response.json()["list"]:
        area_hbr_id = None
    else:
        area_hbr_id = response.json()["list"][0]["value"]
    return area_hbr_id


def extract_sj_salary(vacancies_sj_data):
    salary_from = []
    salary_to = []
    for vacancy in vacancies_sj_data:
        if vacancy["currency"] != "rub":
            continue
        else:
            salary_from.append(vacancy["payment_from"])
            salary_to.append(vacancy["payment_to"])
    return salary_from, salary_to


def extract_hbr_salaries(vacancies_hbr_data):
    salary_from = []
    salary_to = []
    for page in vacancies_hbr_data:
        vacancies = page["list"]
        for vacancy in vacancies:
            if not vacancy["salary"]:
                continue
            sal_from = vacancy["salary"]["from"]
            sal_to = vacancy["salary"]["to"]
            if vacancy["salary"]["currency"] != "rur":
                continue
            else:
                salary_from.append(sal_from)
                salary_to.append(sal_to)
    return salary_from, salary_to


def calculate_salaries(salary_from, salary_to):
    salary_data = []
    for sal_from, sal_to in zip(salary_from, salary_to):
        if not sal_from and not sal_to:
            continue
        elif not sal_to:
            avg = sal_from * 1.2
            salary_data.append(avg)
        elif not sal_from:
            avg = sal_to * 0.8
            salary_data.append(avg)
        else:
            avg = (sal_from + sal_to) / 2
            salary_data.append(avg)
    return salary_data


def get_average_salary(salary_data):
    if not salary_data:
        average_salary = 0
    else:
        average_salary = int(sum(salary_data) / len(salary_data))
    return average_salary


def create_table(overall_statistics, town, keyword):
    if not town:
        table = AsciiTable(overall_statistics, f"{keyword} all")
    else:
        table = AsciiTable(overall_statistics, f"{keyword} {town}")
    return table


def main():
    languages = [
        "Python",
        "Javascript",
        "Java",
        "C#",
        "C++",
        "PHP",
        "Ruby",
        "TypeScript",
    ]
    overall_hbr_statistics = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата",
        ]
    ]

    parser = argparse.ArgumentParser(
        description=r"""
        Утилита для анализа зарплат IT-вакансий с данных SuperJob и Habr Career.
        Пример ввода:
        python .\vacancy_statistics.py # Общая статистика
        python .\vacancy_statistics.py --mode town --town Москва # Статистика для города Москва
        """,
        epilog="""
        Для работы программы требуется файл .env с переменной SJ_TOKEN.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter

    )
    parser.add_argument(
        "--mode",
        choices=["all", "town"],
        default="all",
        help="""
        Режимы работы программы: 
        all - общая статистика, 
        town - статистика для конкретного города, 
        default - all
        """
    )
    parser.add_argument(
        "--town",
        type=str,
        help="""
        Используется при mode=town,
        Пример: --town Москва
        """
    )
    args = parser.parse_args()
    try:
        load_dotenv()
        sj_token = os.environ["SJ_TOKEN"]
    except KeyError:
        print("Не найдена переменная 'SJ_TOKEN'"
              "в .env файле")
        return

    try:
        if not args.town:
            hbr_area_id = None
        else:
            hbr_area_id = get_hbr_area_id(args.town)
            if not hbr_area_id:
                print(f"город {args.town} не найден")
                return
        for language in languages:
            hbr_vacancies_data = get_hbr_vacancy_data(language, hbr_area_id)
            salary_from, salary_to = extract_hbr_salaries(hbr_vacancies_data)
            hbr_salary_data = calculate_salaries(salary_from, salary_to)
            overall_hbr_statistics.append(
                [
                    language,
                    hbr_vacancies_data[0]["meta"]["totalResults"],
                    len(hbr_salary_data),
                    get_average_salary(hbr_salary_data)
                ]
            )
    except requests.exceptions.ConnectionError:
        print("Ошибка соединения. Проверьте подключение")
        return

    hbr_statistics = create_table(overall_hbr_statistics, args.town, keyword="Habr")
    print(hbr_statistics.table)

    overall_sj_statistics = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата",
        ]
    ]

    try:
        if not args.town:
            sj_area_id = None
        else:
            sj_area_id = get_sj_area_id(sj_token, args.town)
            if not sj_area_id:
                print(f"город {args.town} не найден")
                return
        for language in languages:
            sj_vacancies_data = get_sj_vacancy_data(sj_token, language, sj_area_id)
            salary_from, salary_to = extract_sj_salary(sj_vacancies_data)
            salary_data = calculate_salaries(salary_from, salary_to)
            overall_sj_statistics.append(
                [
                    language,
                    len(sj_vacancies_data),
                    len(salary_data),
                    get_average_salary(salary_data),
                ]
            )
    except requests.exceptions.ConnectionError:
        print("Ошибка соединения. Проверьте подключение")
        return

    table = create_table(overall_sj_statistics, args.town, keyword="SuperJob")
    print(table.table)


if __name__ == "__main__":
    main()

