import pytest
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd
import json


@pytest.fixture
def mock_generate_main_page_data():
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
def mock_utils(mocker):
    """
    Фикстура для мока всех функций из utils.
    """
    mocker.patch("src.utils.load_operations_data", return_value=[{"amount": 100}, {"amount": 200}])
    mocker.patch("src.utils.filter_operations_by_date", return_value=[{"amount": 100}])
    mocker.patch("src.utils.calculate_greeting", return_value="Добрый день")
    mocker.patch("src.utils.get_card_summary", return_value=[{"card_number": "1234", "total_spent": 100, "cashback": 1}])
    mocker.patch("src.utils.get_top_transactions", return_value=[{"amount": 100}])
    mocker.patch("src.utils.fetch_currency_rates", return_value={"USD": 75.5, "EUR": 80.2})
    mocker.patch("src.utils.fetch_stock_prices", return_value={"AAPL": 150, "GOOGL": 2800})
    return mocker


@pytest.fixture
def mock_load_user_settings():
    """Фикстура для замены функции загрузки пользовательских настроек."""
    with patch('utils.load_user_settings') as mock_settings:
        mock_settings.return_value = {
            "user_currencies": ["USD", "EUR"],
            "user_stocks": ["AAPL", "GOOGL"]
        }
        yield mock_settings  # Возвращаем замоканную функцию

@pytest.fixture
def test_operations_data():
    """Фикстура для тестовых данных операций."""
    return [
        {"Дата операции": "2023-10-01", "Сумма операции": -1000, "Номер карты": "1234", "Категория": "покупка"},
        {"Дата операции": "2023-10-02", "Сумма операции": -200, "Номер карты": "5678", "Категория": "переводы"},
        {"Дата операции": "2023-10-03", "Сумма операции": -900, "Номер карты": "1234", "Категория": "покупка"},
        {"Дата операции": "2023-10-04", "Сумма операции": -200, "Номер карты": "5678", "Категория": "переводы"},
        {"Дата операции": "2023-10-05", "Сумма операции": -550, "Номер карты": "1234", "Категория": "покупка"},
        {"Дата операции": "2023-10-06", "Сумма операции": -200, "Номер карты": "5678", "Категория": "переводы"}
    ]

@pytest.fixture
def mock_api_response():
    """Фикстура для замены ответов API."""
    with patch('requests.get') as mock_get:
        yield mock_get  # Возвращаем замоканную функцию

@pytest.fixture
def set_env_variables(monkeypatch):
    """Фикстура для установки переменных окружения."""
    monkeypatch.setenv("API_KEY", "test_api_key")  # Устанавливаем переменную окружения
    yield  # Возвращаем управление для выполнения тестов
    monkeypatch.undo()  # Возвращаем переменные окружения к исходному состоянию



@pytest.fixture
def mock_date_input():
    """Фикстура для замены ввода даты."""
    with patch("builtins.input", return_value="2024-01-01 12:00:00"):
        yield

@pytest.fixture
def mock_file_operations_data():
    """Фикстура для мокирования данных из файла Excel."""
    mock_data = [
        {"Дата операции": "2024-01-01", "Номер карты": "1234", "Сумма операции": -100.0, "Категория": "покупки"},
        {"Дата операции": "2024-01-02", "Номер карты": "5678", "Сумма операции": -200.0, "Категория": "покупки"},
    ]
    with patch("pandas.read_excel", return_value=pd.DataFrame(mock_data)):
        yield mock_data

@pytest.fixture
def mock_user_settings():
    """Фикстура для мокирования пользовательских настроек."""
    settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "TSLA"]}
    with patch("builtins.open", mock_open(read_data=json.dumps(settings))):
        yield settings

@pytest.fixture
def mock_requests_get():
    """Фикстура для мокирования HTTP запросов."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "conversion_rates": {"RUB": 74.5},
            "results": [{"c": 125.0}],
        }
        yield mock_get

@pytest.fixture
def mock_operations_data():
    """Фикстура для замены данных операций."""
    return [
        {"Дата операции": "2024-01-01", "Сумма операции": -500, "Номер карты": "5507000000005091", "Категория": "Покупки"},
        {"Дата операции": "2024-01-10", "Сумма операции": -1500, "Номер карты": "5507000000007197", "Категория": "Развлечения"},
        {"Дата операции": "2024-01-20", "Сумма операции": 1000, "Номер карты": "5507000000004556", "Категория": "Переводы"},
    ]

@pytest.fixture
def mock_currency_api_response():
    """Фикстура для замены ответа API курсов валют."""
    return {
        "conversion_rates": {
            "RUB": 75.23
        }
    }

@pytest.fixture
def mock_stock_api_response():
    """Фикстура для замены ответа API акций."""
    return {
        "results": [{"c": 150.5}]
    }

@pytest.fixture
def mock_operations():
    """Фикстура для предоставления тестовых данных операций."""
    return [
        {"Номер карты": "*9002", "Дата операции": "2024-12-12", "Сумма операции": -100, "Категория": "переводы"},
        {"Номер карты": "*9001", "Дата операции": "2024-12-11", "Сумма операции": -150, "Категория": "покупка"},
        {"Номер карты": "*9005", "Дата операции": "2024-12-10", "Сумма операции": -6050, "Категория": "переводы"},
        {"Номер карты": "*9004", "Дата операции": "2024-12-09", "Сумма операции": -300, "Категория": "покупка"},
        {"Номер карты": "*9003", "Дата операции": "2024-12-08", "Сумма операции": -100, "Категория": "переводы"},
        {"Номер карты": "*9002", "Дата операции": "2024-12-07", "Сумма операции": -3500, "Категория": "покупка"},
        {"Номер карты": "*9001", "Дата операции": "2024-12-06", "Сумма операции": -1100, "Категория": "переводы"},
        {"Номер карты": "*9005", "Дата операции": "2024-12-05", "Сумма операции": -150, "Категория": "покупка"},
        {"Номер карты": "*9004", "Дата операции": "2024-12-04", "Сумма операции": -4000, "Категория": "переводы"},
        {"Номер карты": "*9003", "Дата операции": "2024-12-03", "Сумма операции": -350, "Категория": "покупка"},
        {"Номер карты": "*9002", "Дата операции": "2024-12-02", "Сумма операции": -100, "Категория": "переводы"},
        {"Номер карты": "*9001", "Дата операции": "2024-12-01", "Сумма операции": -3500, "Категория": "покупка"}
    ]
