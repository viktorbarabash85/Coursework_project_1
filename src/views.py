import json
import logging

from src.utils import (calculate_greeting, fetch_currency_rates, fetch_stock_prices, filter_operations_by_date,
                       get_card_summary, get_top_transactions, load_operations_data, setup_logger, validate_input_date)

"""1. Веб-страницы. Страница "Главная"."""

# Запускаем функцию библиотеки logging для логирования данного файла
logger = setup_logger("views - home_page", "views")


def run_main_page() -> None:
    """
    Запускает логику генерации данных для главной страницы.
    """
    # logger.info("Запуск страницы 'Главная'.")
    print("_" * 40)
    print(
        'Страница "Главная".\n\n Предоставляет JSON-ответ с данными о расходах за месяц. '
        "Имеются данные с операциями за 2021-2024 годы. Выводится анализ данных с начала месяца введенной даты."
    )

    # Вводим дату и время в формате YYYY-MM-DD HH:MM:SS (например: 2024-12-28 19:30:00)
    user_input_date = validate_input_date()
    logger.info("Пользователь ввел дату: %s", user_input_date)

    print("_" * 40)

    # Генерируем данные для страницы "Главная"
    main_page_data = generate_main_page_data(user_input_date)

    # Печатаем результат в формате JSON
    print(json.dumps(main_page_data, indent=4, ensure_ascii=False))
    logger.info("Данные для главной страницы сгенерированы и выведены.")


def generate_main_page_data(input_date: str) -> dict:
    """
    Веб-страница "Главная". Функция для генерации данных

    :param input_date: Строка для ввода даты и времени в формате YYYY-MM-DD HH:MM:SS
    :return: JSON-ответ (Приветствие; По каждой карте: последние 4 цифры карты; общая сумма расходов;
    кешбэк (1 рубль на каждые 100 рублей); Топ-5 транзакций по сумме платежа; Курс валют; Стоимость акций.)
    """
    # Загрузка данных операций из файла
    logger.info("Загрузка данных операций из файла.")
    operations = load_operations_data()
    logger.info("Данные операций успешно загружены.")

    # Фильтруем операции за указанный диапазон
    logger.info("Фильтрация операций по дате: %s", input_date)
    filtered_operations = filter_operations_by_date(operations, input_date)

    # Приветствие в зависимости от текущего времени
    greeting = calculate_greeting()

    # Создаем сводку по картам (номер карты, общие затраты и кэшбэк)
    logger.info("Создание сводки по картам.")
    card_summary = get_card_summary(filtered_operations)

    # Получаем топовые транзакции по расходам
    logger.info("Получение топовых транзакций по сумме расходов.")
    top_transactions = get_top_transactions(filtered_operations)

    # Получаем курсы валют через API
    logger.info("Получение курсов валют.")
    currency_rates = fetch_currency_rates()

    # Получаем цены акций через API
    logger.info("Получение цен акций.")
    stock_prices = fetch_stock_prices()

    # Компилируем все данные в словарь для страницы "Главная"
    logger.info("Компиляция данных для главной страницы завершена.")
    return {
        "greeting": greeting,  # Приветствие пользователя
        "cards": card_summary,  # Сводка по картам
        "top_transactions": top_transactions,  # Топовые транзакции
        "currency_rates": currency_rates,  # Курсы валют
        "stock_prices": stock_prices,  # Цены акций
    }


if __name__ == "__main__":
    run_main_page()
