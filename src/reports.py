import json
import os
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional

import pandas as pd

from src.utils import setup_logger


"""3. Отчеты. "Траты по категории"."""

# Запускаем универсальную функцию "setup_logger" для логирования данного файла
logger = setup_logger("reports - spending_by_category", "reports")

# Путь для сохранения отчетов
REPORTS_DIR = "reports/spending_by_category"
os.makedirs(REPORTS_DIR, exist_ok=True)

custom_file_name: Optional[str] = None


# Декоратор для сохранения результата отчета
def save_report_to_file() -> Callable[[Callable[..., Dict[str, Any]]], Callable[..., Dict[str, Any]]]:
    """Декоратор, сохраняющий результат функции в файл JSON."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            report = func(*args, **kwargs)
            global REPORTS_DIR
            global custom_file_name

            # Определяем имя для файла-отчета
            file_name = os.path.join(
                REPORTS_DIR,
                (
                    custom_file_name
                    if custom_file_name
                    else f"spending_{report['general_information']['category']}_"
                    f"{report['general_information']['start_date'].replace('-', '')}_"
                    f"{report['general_information']['end_date'].replace('-', '')}"
                ),
            )

            # Логирование выбранного имени файла
            logger.info(f'Выбрано название файла для отчета: "{file_name}"')

            # Сохранение в JSON-отчет
            json_path = f"{file_name}.json"
            with open(json_path, "w", encoding="utf-8") as json_file:
                json.dump(report, json_file, ensure_ascii=False, indent=4, default=str)

            logger.info(f'Сохранен файл-отчет "{custom_file_name}.json"')

            return report

        return wrapper

    return decorator


# Функция "Траты по категории"
@save_report_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Возвращает траты по заданной категории за последние три месяца от переданной даты.

    :param transactions: DataFrame с транзакциями
    :param category: Название категории
    :param date: Опциональная дата (если не передана, используется текущая)
    :return: Словарь с данными по тратам
    """

    # Определяем стартовую дату для отсчета
    current_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
    start_date = current_date - timedelta(days=90)

    # Преобразуем столбец "Дата операции" в datetime, если это необходимо
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%Y-%m-%d")

    # Фильтрация по дате, сумме и категории
    filtered_data = transactions[
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= current_date)
        & (transactions["Категория"].str.lower() == category.lower())
        & (transactions["Сумма операции"] < 0)
    ]
    print("_" * 40)

    # Общие сведения
    if filtered_data.empty:
        logger.info(
            f'Данных по введенной категории "{category}" '
            f'за период "{start_date.date()}" - "{current_date.date()}" не найдено.'
        )
        return {
            "general_information": {
                "category": category,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": current_date.strftime("%Y-%m-%d"),
                "total_spent": 0,
                "transactions_count": 0,
            },
            "detailed_information": [],
        }

    total_spent = round(filtered_data["Сумма операции"].sum(), 2)
    general_info = {
        "category": category,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": current_date.strftime("%Y-%m-%d"),
        "total_spent": float(total_spent),
        "transactions_count": len(filtered_data),
    }

    # detailed_info.columns = ["date_amount", "transaction_amount", "category"]
    # detailed_info = filtered_data[["Дата операции", "Сумма операции", "Категория"]].copy()

    detailed_info = filtered_data[["Дата операции", "Сумма операции", "Категория"]]
    detailed_info.columns = pd.Index(["date_amount", "transaction_amount", "category"])
    detailed_info_dict = detailed_info.to_dict(orient="records")

    return {"general_information": general_info, "detailed_information": detailed_info_dict}


# Функция для получения необходимых данных для генерации отчета
def run_generate_report() -> None:
    """
    Запуск генерации отчета о тратах по категории.

    Считывает входные данные из Excel. Пользователь выбирает категорию, дату и сохраняет результат.
    """

    print("_" * 40)
    print(
        '"Траты по категории".\n\n Формирует JSON-отчет о тратах по заданной категории  (от переданной даты).'
        "Имеются данные с операциями за 2021-2024 годы. Выводится отчет за последние три месяца (от переданной даты)."
    )

    # Загрузка данных из файла
    data_path = "data/operations_21_24.xlsx"
    logger.info(f'Загрузка данных операций из файла: "{data_path}"')
    try:
        transactions = pd.read_excel(data_path)
        logger.info("Данные операций успешно загружены.")
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        exit()

    print("_" * 40)

    # Ввод даты
    while True:
        date = input(
            "\nВведите дату (в формате YYYY-MM-DD (пример: 2024-12-15), или нажмите Enter для текущей даты): "
        ).strip()
        if not date:
            date: Optional[str] = None
            chosen_date = datetime.now().strftime("%Y-%m-%d")
            print(f"Выбрана дата: {chosen_date}")
            logger.info(f'Пользователем выбрана текущая дата: "{chosen_date}"')
            break
        try:
            datetime.strptime(date, "%Y-%m-%d")
            print(f"Выбрана дата: {date}")
            logger.info(f'Пользователем ввел дату: "{date}"')
            break
        except ValueError:
            logger.error(f'Ошибка. Дата "{date}" введена некорректно. Пример: 2024-12-31')
            print("Ошибка. Дата введена некорректно.")

    # Получение списка всех имеющихся категорий
    available_categories = sorted(transactions["Категория"].dropna().astype(str).unique())

    # Предложение ознакомиться со списком категорий
    show_categories = (
        input("\nЖелаете для ознакомления вывести весь список ваших категорий? (да/нет): ").strip().lower()
    )
    if show_categories == "да":
        print("\nСписок категорий:\n")
        print(", ".join(available_categories))
        category_prompt = "\nВведите категорию из предложенных выше: "
    else:
        category_prompt = "\nВведите название категории: "

    # Ввод категории
    while True:
        category = input(category_prompt).strip()
        if category.lower() in [cat.lower() for cat in available_categories]:
            logger.info(f'Пользователь выбрал категорию: "{category}"')
            break
        else:
            print(f'\nКатегория "{category}" не найдена среди ваших операций.')
            retry = (
                input(
                    '\nНажмите "нет" для повторного ввода категории, '
                    'или "да", если хотите сохранить нулевой отчет? (да/нет): '
                )
                .strip()
                .lower()
            )
            if retry == "да":
                logger.info(f'Пользователь решил сохранить нулевой отчет для категории: "{category}"')
                break

    # Ввод имени файла
    global custom_file_name
    custom_file_name = input(
        "\nВведите название файла для отчета (или нажмите Enter для стандартного имени): "
    ).strip()
    if custom_file_name:
        logger.info(f'Пользователь ввел название отчета: "{custom_file_name}"')
    else:
        custom_file_name = None
        logger.info(f'Пользователь выбрал название отчета по-умолчанию: "{custom_file_name}"')

    print(f'\nОтчет о тратах по категории "{category}" сохранен.')

    # Генерация отчета
    report = spending_by_category(transactions, category=category, date=date)

    # _Вывод результатов в терминал
    general_info = report["general_information"]
    detailed_info = pd.DataFrame(report["detailed_information"])

    print("\nОбщие сведения:")
    print(f"Категория: {general_info['category']}")
    print(f"Начало периода: {general_info['start_date']}")
    print(f"Конец периода: {general_info['end_date']}")
    print(f"Всего потрачено: {general_info['total_spent']}")
    print(f"Количество операций: {general_info['transactions_count']}")

    if not detailed_info.empty:
        print("\nДетальные сведения:")
        detailed_info.columns = pd.Index(["Дата операции", "Сумма операции", "Категория"])
        print(detailed_info.to_string(index=False))
    else:
        print("\nДетальные сведения: 0.")


if __name__ == "__main__":
    run_generate_report()
