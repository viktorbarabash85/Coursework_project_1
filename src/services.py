import json
import logging
from datetime import datetime
from functools import partial, reduce
from heapq import nlargest
from typing import Any, Dict, List, Tuple

from src.utils import load_operations_data, setup_logger

"""2. Выгодные категории повышенного кешбэка."""

# Запускаем функцию библиотеки logging для логирования данного файла
logger = setup_logger("services - profit_cashback", "services")


def _is_valid_operation(op: Dict[str, Any], year: int, month: int) -> bool:
    """
    Проверяет, соответствует ли операция заданным критериям для подсчета кэшбэка.

    :param op: Операция в виде словаря с данными о дате, категории, сумме и статусе.
    :param year: Год, с которым сравнивается дата операции.
    :param month: Месяц, с которым сравнивается дата операции.
    :return: True, если операция валидна, иначе False.
    """
    try:
        operation_date = datetime.strptime(op.get("Дата операции", ""), "%Y-%m-%d")
        return (
            operation_date.year == year
            and operation_date.month == month
            and op.get("Категория") not in ("Переводы", "Наличные", "Списание ошибочно зачисленных средств")
            and op.get("Статус") != "FAILED"
            and op.get("Сумма операции", 0) < 0
        )
    except ValueError as e:
        logger.error(f"Ошибка проверки на соответствие критериям. Ошибка: {e}")
        return False


def filter_operations(operations: List[Dict[str, Any]], year: int, month: int) -> List[Dict[str, Any]]:
    """
    Фильтрует проверенные операции в _is_valid_operation.

    :param operations: Список операций для фильтрации.
    :param year: Год для фильтрации операций.
    :param month: Месяц для фильтрации операций.
    :return: Список отфильтрованных операций.
    """
    logger.info("Выполняется фильтрация операций для подсчета кэшбэка")
    filter_by_month_year = partial(_is_valid_operation, year=year, month=month)
    return list(filter(filter_by_month_year, operations))


def calculate_cashback(operation: Dict[str, Any]) -> Tuple[str, float]:
    """
    Рассчитывает кэшбэк для каждой операции.

    :param operation: Операция в виде словаря с данными о категории и сумме.
    :return: Кортеж, содержащий категорию и сумму кэшбэка.
    """
    category: str = operation.get("Категория", "")
    amount: float = operation.get("Сумма операции", 0.0)
    cashback: float = float(-amount // 100)
    return category, cashback


def analyze_cashback(operations: List[Dict[str, Any]], year: int, month: int) -> Dict[str, float]:
    """
    Анализирует кэшбэк по категориям за указанный год и месяц.

    :param operations: Список операций для анализа.
    :param year: Год для анализа операций.
    :param month: Месяц для анализа операций.
    :return: Словарь с категориями и суммами кэшбэка.
    """
    filtered_operations = filter_operations(operations, year, month)
    cashback_results: List[Tuple[str, float]] = list(map(calculate_cashback, filtered_operations))

    cashback_by_category: Dict[str, float] = reduce(
        lambda acc, item: {**acc, item[0]: acc.get(item[0], 0) + item[1]},
        cashback_results,
        {},
    )

    # Удаляем категории с пустыми значениями
    cashback_by_category = {k: v for k, v in cashback_by_category.items() if k and v > 0}

    # Сортируем и выбираем топ-3 категории
    top_cashback: Dict[str, float] = dict(nlargest(3, cashback_by_category.items(), key=lambda x: x[1]))

    logger.info("Топ-3 категорий кэшбэка выбраны.")
    return top_cashback


def log_filtered_operations(filtered_operations: List[Dict[str, Any]]) -> None:
    """
    Логирует отфильтрованные операции отдельно от их обработки.

    :param filtered_operations: Список отфильтрованных операций.
    """
    filtered = []
    for op in filtered_operations:
        filtered.append(op)
    logger.info(f"Фильтрация операций завершена. Найдено {len(filtered)} операций.")


def log_top_cashback(top_cashback: Dict[str, float]) -> None:
    """
    Логирует топовые категории кэшбэка отдельно от их вычисления.

    :param top_cashback: Словарь с топовыми категориями и суммами кэшбэка.
    """
    for category, amount in top_cashback.items():
        logger.info(f"Категория: {category}, сумма кэшбэка: {amount}")


def run_profit_cashback() -> None:
    """
    Основная функция запуска анализа кэшбэка.
    """
    print("_" * 40)
    print('"Выгодные категории повышенного кешбэка".\n')
    print("Сервис анализирует наиболее выгодные категории для выбора в качестве категорий повышенного кешбэка.\n")
    try:
        logger.info("Загрузка данных операций из файла.")
        data = load_operations_data()
        logger.info("Данные операций успешно загружены.")
        while True:
            year_input = input("Введите год для анализа (2021-2024):\n>>> ")
            if year_input.isdigit() and 2021 <= int(year_input) <= 2024:
                year = int(year_input)
                break
            else:
                print("Ошибка. Некорректный ввод года. Повторите попытку.")
                logger.error(f"Некорректный ввод года: {year_input}.")
        while True:
            month_input = input("Введите номер месяца для анализа (1-12):\n>>> ")
            if month_input.isdigit() and 1 <= int(month_input) <= 12:
                month = int(month_input)
                break
            print("Ошибка. Некорректный ввод месяца. Повторите попытку.")
            logger.error(f"Некорректный ввод месяца: {month_input}.")

    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        return

    print("_" * 40)

    print("\nПоиск Топ-3 категорий кэшбэка....")
    print("_" * 40)

    # Анализ кэшбэка по категориям
    filtered_operations = filter_operations(data, year, month)
    log_filtered_operations(filtered_operations)

    cashback_results = analyze_cashback(data, year, month)
    log_top_cashback(cashback_results)

    # Выводим результаты в формате JSON
    print(json.dumps(cashback_results, ensure_ascii=False, indent=4))
    print("_" * 40)


if __name__ == "__main__":
    run_profit_cashback()
