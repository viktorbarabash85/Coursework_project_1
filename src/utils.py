import json
import os
from datetime import datetime
from typing import Any, Dict, List, Union

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException

# Веб-страницы. Страница "Главная". Вспомогательные функции

load_dotenv(".env")
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
STOCK_API_KEY = os.getenv("STOCK_API_KEY")


def validate_input_date() -> str:
    """
    Запрашивает у пользователя ввод даты и проверяет корректность формата.

    Если пользователь вводит некорректный формат даты, функция запрашивает ввод повторно до тех пор,
    пока не будет предоставлен правильный формат.

    :return: Корректная дата в формате 'YYYY-MM-DD HH:MM:SS'
    """
    while True:
        print("Введите дату и время в формате 'YYYY-MM-DD HH:MM:SS': ")
        input_date = input(">>> ").strip().lower()
        try:
            datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
            return input_date  # Возвращаем корректную дату
        except ValueError:
            print(
                "Ошибка: Неверный формат даты. Ожидаемый формат: 'YYYY-MM-DD HH:MM:SS'. Пожалуйста, попробуйте снова."
            )


def load_operations_data() -> List[Dict[str, Any]]:
    """
    Загружает данные операций из файла xlsx и преобразует их в список словарей.

    :return: Список операций в формате словаря.
    """
    file_path = os.path.join("data", "operations_21_24.xlsx")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    # Загружаем данные с преобразованием дат
    operations = pd.read_excel(file_path)
    operations["Дата операции"] = pd.to_datetime(
        operations["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    operations.columns = operations.columns.astype(str)
    return operations.to_dict(orient="records")  # Здесь ключи будут строками


def filter_operations_by_date(operations: List[Dict[str, Any]], input_date: str) -> List[Dict[str, Any]]:
    """
    Фильтрует операции в заданном диапазоне дат.

    :param operations: Список операций.
    :param input_date: Входная дата в формате 'YYYY-MM-DD HH:MM:SS'.
    :return: Отфильтрованный список операций.
    """
    try:
        date_obj = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError(f"Неверный формат даты: {input_date}. Ожидаемый формат: 'YYYY-MM-DD HH:MM:SS'")

    start_date = date_obj.replace(day=1).strftime("%Y-%m-%d")
    end_date = date_obj.strftime("%Y-%m-%d")

    # Отфильтруем только операции с корректными датами
    filtered_operations = []
    for op in operations:
        op_date = op.get("Дата операции")
        if isinstance(op_date, str):
            if start_date <= op_date <= end_date:
                filtered_operations.append(op)

    return filtered_operations


def calculate_greeting() -> str:
    """
    Возвращает приветствие в зависимости от текущего времени суток.

    :return: Приветствие пользователя.
    """
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        return "Добрый день"
    elif 18 <= current_hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_card_summary(operations: List[Dict[str, Any]]) -> List[Dict[str, Union[str, float]]]:
    """
    Создает сводку по картам с учетом затрат в указанный период и рассчитывает кэшбэк (1 рубль на каждые 100 рублей).
    Учитывает все карты пользователя без операций в указанный период.

    :param operations: Список операций.
    :return: Сводка по картам.
    """

    all_operations = load_operations_data()
    all_cards = set(
        str(op.get("Номер карты", "")).strip()[-4:]
        for op in all_operations
        if str(op.get("Номер карты", "")).strip() not in ["", "nan", "Не указано"]
    )

    # Словарь для хранения информации по активным картам
    card_summary = {card: {"total_spent": 0.0, "cashback": 0.0, "active": False} for card in all_cards}

    for op in operations:
        last_digits = str(op.get("Номер карты", "")).strip()[-4:]
        if last_digits not in card_summary:
            continue

        amount = float(op.get("Сумма операции", 0))
        category = str(op.get("Категория", "")).lower()

        if amount < 0:
            card_summary[last_digits]["total_spent"] += amount

        if category != "переводы" and amount < 0:
            cashback = float(-amount // 100)
        else:
            cashback = 0.0

        card_summary[last_digits]["cashback"] += cashback
        card_summary[last_digits]["active"] = True

    # Разделяем карты на активные и неактивные
    active_cards = [
        {
            "last_digits": str(card),
            "total_spent": float(round(data["total_spent"], 2)),
            "cashback": float(round(data["cashback"], 2)),
        }
        for card, data in card_summary.items()
        if data["active"]
    ]

    inactive_cards = [
        {
            "last_digits": str(card),
            "total_spent": float(round(data["total_spent"], 2)),
            "cashback": float(round(data["cashback"], 2)),
        }
        for card, data in card_summary.items()
        if not data["active"]
    ]

    return active_cards + inactive_cards


# Получение 5 топовых транзакций
def get_top_transactions(operations: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Union[str, float]]]:
    """
    Извлекает топ-N транзакций по сумме.

    :param operations: Список операций.
    :param top_n: Количество транзакций в топе.
    :return: Список топовых транзакций.
    """
    # Фильтруем только транзакции с отрицательной суммой
    filtered_operations = [op for op in operations if float(op.get("Сумма операции", 0)) < 0]

    # Сортируем по убыванию суммы операции
    sorted_operations = sorted(filtered_operations, key=lambda x: abs(float(x.get("Сумма операции", 0))), reverse=True)

    return [
        {
            "date": datetime.strptime(op.get("Дата операции", ""), "%Y-%m-%d").strftime("%d.%m.%Y"),
            "amount": round(float(op.get("Сумма операции", 0)), 2),
            "category": op.get("Категория", "Не указано"),
            "description": op.get("Описание", "Не указано"),
        }
        for op in sorted_operations[:top_n]
    ]


# Загрузка пользовательских настроек
def load_user_settings() -> Dict[str, Union[List[str], str]]:
    """
    Загружает пользовательские настройки из файла JSON.

    :return: Словарь с настройками пользователя.
    """
    file_path = "user_settings.json"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# Получение курсов валют
def fetch_currency_rates() -> List[Dict[str, Union[str, float]]]:
    """
    Получает курсы валют через API.

    :return: Список курсов тех валют, которые указаны в пользовательских настройках.
    """

    settings = load_user_settings()
    currencies = settings.get("user_currencies", [])
    rates = []

    for currency in currencies:
        try:
            url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/{currency}"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise ValueError("Не удалось получить курс валют")
            data = response.json()
            rate = float(data.get("conversion_rates", {}).get("RUB"))
            if not rate:
                raise ValueError(f"нет данных по валюте {currency}")
            rates.append({"currency": str(currency), "rate": float(round(rate, 2))})
        except RequestException as e:
            raise ValueError(f"Ошибка при получении курсов валют для {currency}: {e}") from e
        except (ValueError, KeyError) as e:
            raise ValueError(f"Ошибка обработки данных для {currency}: {e}") from e

    return rates


# Получение цен акций
def fetch_stock_prices() -> List[Dict[str, Union[str, float]]]:
    """
    Получает цены акций через API.

    :return: Список цен тех акций, которые указаны в пользовательских настройках.
    """

    settings = load_user_settings()
    stocks = settings.get("user_stocks")

    if not stocks:
        return []

    prices = []
    errors = []

    for stock in stocks:
        try:
            url = f"https://api.polygon.io/v2/aggs/ticker/{stock}/prev?adjusted=true&apiKey={STOCK_API_KEY}"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise ValueError("Не удалось узнать цены на акции")
            data = response.json()
            if not data["results"]:
                raise ValueError(f"нет данных по акции {stock}")
            closing_price = data["results"][0].get("c")
            prices.append({"stock": stock, "price": round(closing_price, 2)})
        except RequestException:
            raise ValueError("Не удалось узнать цены на акции")
        except (ValueError, KeyError):
            errors.append(f"нет данных по акции {stock}")

    if errors:
        raise ValueError("; ".join(errors))

    return prices
