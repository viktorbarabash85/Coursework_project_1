import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Generator
from unittest.mock import MagicMock, mock_open, patch

import pytest


# =============================================
# 1. Фикстуры для Веб-страницы. Страница "Главная"
# =============================================

@pytest.fixture
def mock_generate_main_page_data() -> MagicMock:
    """
    Фикстура для мока функции generate_main_page_data.
    """
    mock_func = MagicMock()
    mock_func.return_value = {
        "greeting": "Добрый день",
        "cards": [{"card_number": "1234", "total_spent": 100, "cashback": 1}],
        "top_transactions": [{"amount": 100}],
        "currency_rates": {"USD": 75.5, "EUR": 80.2},
        "stock_prices": {"AAPL": 150, "GOOGL": 2800},
    }
    return mock_func


@pytest.fixture
def mock_load_user_settings() -> Generator:
    """
    Фикстура для замены функции загрузки пользовательских настроек.
    """
    with patch("utils.load_user_settings") as mock_settings:
        mock_settings.return_value = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}
        yield mock_settings  # Возвращаем замоканную функцию


@pytest.fixture
def test_operations_data() -> list[dict]:
    """
    Фикстура для тестовых данных операций.
    """
    return [
        {"Дата операции": "2023-10-01", "Сумма операции": -1000, "Номер карты": "1234", "Категория": "покупка"},
        {"Дата операции": "2023-10-02", "Сумма операции": -200, "Номер карты": "5678", "Категория": "переводы"},
        {"Дата операции": "2023-10-03", "Сумма операции": -900, "Номер карты": "1234", "Категория": "покупка"},
        {"Дата операции": "2023-10-04", "Сумма операции": -200, "Номер карты": "5678", "Категория": "переводы"},
        {"Дата операции": "2023-10-05", "Сумма операции": -550, "Номер карты": "1234", "Категория": "покупка"},
        {"Дата операции": "2023-10-06", "Сумма операции": -200, "Номер карты": "5678", "Категория": "переводы"},
    ]


@pytest.fixture
def mock_user_settings() -> Generator:
    """
    Фикстура для мокирования пользовательских настроек.
    """
    settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "TSLA"]}
    with patch("builtins.open", mock_open(read_data=json.dumps(settings))):
        yield settings


@pytest.fixture
def mock_requests_get() -> Generator:
    """
    Фикстура для мокирования HTTP запросов.
    """
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "conversion_rates": {"RUB": 74.5},
            "results": [{"c": 125.0}],
        }
        yield mock_get


# =============================================
# 2. Фикстуры для Сервисы. "Выгодные категории повышенного кешбэка"
# =============================================

@pytest.fixture
def mock_operations_data_2() -> list[dict]:
    """
    Фикстура для тестовых данных операций.
    """
    return [
        {"Дата операции": "2023-03-01", "Категория": "Еда", "Сумма операции": -1000, "Статус": "SUCCESS"},
        {"Дата операции": "2023-03-02", "Категория": "Транспорт", "Сумма операции": -500, "Статус": "SUCCESS"},
        {"Дата операции": "2023-03-03", "Категория": "Развлечения", "Сумма операции": -2000, "Статус": "SUCCESS"},
        {"Дата операции": "2023-03-04", "Категория": "Переводы", "Сумма операции": -1500, "Статус": "SUCCESS"},
        {"Дата операции": "2023-03-05", "Категория": "Наличные", "Сумма операции": -100, "Статус": "FAILED"},
    ]


@pytest.fixture
def mock_operations_data_filtered() -> list[dict]:
    """
    Фикстура для тестовых данных операций.
    """
    return [
        {"Дата операции": "2023-03-01", "Категория": "Еда", "Статус": "SUCCESS", "Сумма операции": -1000},
        {"Дата операции": "2023-03-02", "Категория": "Транспорт", "Статус": "SUCCESS", "Сумма операции": -500},
        {"Дата операции": "2023-03-03", "Категория": "Развлечения", "Статус": "SUCCESS", "Сумма операции": -2000},
        {"Дата операции": "2023-03-04", "Категория": "Кафе", "Статус": "SUCCESS", "Сумма операции": -1500},
        {"Дата операции": "2023-03-05", "Категория": "Образование", "Статус": "SUCCESS", "Сумма операции": -3000},
        {"Дата операции": "2023-03-06", "Категория": "Спорт", "Статус": "SUCCESS", "Сумма операции": -1200},
        {"Дата операции": "2023-03-07", "Категория": "Путешествия", "Статус": "SUCCESS", "Сумма операции": -2500},
        {"Дата операции": "2023-03-08", "Категория": "Магазин", "Статус": "SUCCESS", "Сумма операции": -800},
        {"Дата операции": "2023-03-09", "Категория": "Книги", "Статус": "SUCCESS", "Сумма операции": -600},
        {"Дата операции": "2023-03-10", "Категория": "Здоровье", "Статус": "SUCCESS", "Сумма операции": -400},
        {"Дата операции": "2023-03-11", "Категория": "Развлечения", "Статус": "SUCCESS", "Сумма операции": -1800},
        {"Дата операции": "2023-03-12", "Категория": "Транспорт", "Статус": "SUCCESS", "Сумма операции": -700},
        {"Дата операции": "2023-03-13", "Категория": "Еда", "Статус": "SUCCESS", "Сумма операции": -1300},
        {"Дата операции": "2023-03-14", "Категория": "Образование", "Статус": "SUCCESS", "Сумма операции": -900},
    ]


@pytest.fixture
def mock_load_operations_data() -> dict:
    """
    Фикстура для тестовых данных операций.
    """
    return {"Дата операции": "2020-03-15", "Категория": "Переводы", "Сумма операции": 100, "Статус": "SUCCESS"}


# =============================================
# 3. Фикстуры для Отчеты. "Расходы по категориям"
# =============================================

@pytest.fixture
def empty_transactions():
    """
    Фикстура с пустыми тестовыми данными операций.
    """
    # Возвращаем пустой DataFrame
    return pd.DataFrame(columns=["Дата операции", "Сумма операции", "Категория"])


@pytest.fixture
def mock_read_excel():
    """
    Фикстура мока загрузки excel.
    """
    with patch("pandas.read_excel", return_value=MagicMock()) as mock:
        yield mock


@pytest.fixture
def mock_transactions() -> pd.DataFrame:
    """
    Создает фиктивный DataFrame с данными о транзакциях.
    """
    data = {
        "Дата операции": ["2024-01-01", "2024-02-15", "2024-03-10"],
        "Категория": ["еда", "транспорт", "еда"],
        "Сумма операции": [-100.0, -50.0, -200.0],
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_transactions_2():
    """
    Мокированные данные транзакций.
    """
    data = {
        "Дата операции": [
            "2024-10-01 12:00:00",
            "2024-10-15 12:00:00",
            "2024-12-05 12:00:00",
            "2024-11-01 12:00:00",
            "2024-12-25 12:00:00",
        ],
        "Сумма операции": [
            -100.0,
            -100.0,
            -300.0,
            -150.0,
            -50.0
        ],
        "Категория": [
            "Еда",
            "Еда",
            "Еда",
            "Транспорт",
            "Транспорт"
        ],
    }

    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    return df


@pytest.fixture
def mock_date():
    """
    Мокированная текущая дата для тестов.
    """
    # return datetime(2024, 12, 31)
    return str("2024-12-31")


@pytest.fixture
def fake_transactions():
    """
    Фиктивные данные транзакций.
    """
    data = {
        "Дата операции": [
            datetime(2024, 10, 1, 12, 0, 0),
            datetime(2024, 10, 15, 12, 0, 0),
            datetime(2024, 11, 1, 12, 0, 0),
            datetime(2024, 12, 25, 12, 0, 0),
        ],
        "Сумма операции": [-100.0, -300.0, -150.0, -50.0],
        "Категория": ["Еда", "Еда", "Транспорт", "Транспорт"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def fake_report():
    """
    Фиктивный отчёт, возвращаемый spending_by_category.
    """
    return {
        "general_information": {
            "category": "Еда",
            "start_date": "2024-09-15",
            "end_date": "2024-12-15",
            "total_spent": 400.0,
            "transactions_count": 2,
        },
        "detailed_information": [
            {"date_amount": "2024-10-01", "transaction_amount": -100.0, "category": "Еда"},
            {"date_amount": "2024-10-15", "transaction_amount": -300.0, "category": "Еда"},
        ],
    }
