import unittest
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest
from requests import RequestException

from src.utils import (
    calculate_greeting,
    fetch_currency_rates,
    fetch_stock_prices,
    filter_operations_by_date,
    get_card_summary,
    get_top_transactions,
    load_operations_data,
    load_user_settings,
    validate_input_date,
)


# Тест для validate_input_date
@patch("builtins.input", side_effect=["2023-12-31 12:00:00", "invalid date"])
def test_validate_input_date_valid(mock_input: MagicMock) -> None:
    """
    Тестирует функцию validate_input_date, проверяя, что она возвращает
    корректную дату при правильном вводе.
    """
    assert validate_input_date() == "2023-12-31 12:00:00"


@patch("builtins.input", side_effect=["invalid date", "2023-12-31 12:00:00"])
def test_validate_input_date_invalid_then_valid(mock_input: MagicMock) -> None:
    """
    Тестирует функцию validate_input_date, проверяя, что она может
    обработать некорректный ввод и вернуть правильный результат при
    следующем корректном вводе.
    """
    assert validate_input_date() == "2023-12-31 12:00:00"


# Тест для load_operations_data
@patch("pandas.read_excel")
def test_load_operations_data(mock_read_excel: MagicMock) -> None:
    """
    Тестирует функцию load_operations_data, проверяя, что она корректно
    загружает данные операций и преобразует даты в нужный формат.
    """
    # Создаем настоящий DataFrame для тестирования с датами в нужном формате
    mock_data = pd.DataFrame(
        {
            "Дата операции": ["01.12.2023 12:00:00"],
            "Номер карты": ["*3456"],
            "Сумма операции": [-1000],
            "Категория": ["покупка"],
        }
    )

    # Настраиваем mock.read_excel для возврата нашего DataFrame
    mock_read_excel.return_value = mock_data

    with patch("os.path.exists", return_value=True):
        result = load_operations_data()

        # Проверяем, что результат содержит правильное количество элементов
        assert len(result) == 1
        # Проверяем, что дата операции правильно преобразована
        assert result[0]["Дата операции"] == "2023-12-01"


def test_load_operations_data_file_not_found() -> None:
    """Тест на выброс FileNotFoundError, если файл не найден."""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError) as excinfo:
            load_operations_data()
        assert "Файл data\\operations_21_24.xlsx не найден." in str(excinfo.value)


# Тест для filter_operations_by_date
def test_filter_operations_by_date() -> None:
    """
    Тестирует функцию filter_operations_by_date, проверяя, что она
    корректно фильтрует операции по заданной дате.
    """
    operations = [{"Дата операции": "2023-12-01"}, {"Дата операции": "2023-12-09"}, {"Дата операции": "2023-11-15"}]
    input_date = "2023-12-15 12:00:00"
    result = filter_operations_by_date(operations, input_date)

    # Проверяем, что возвращаются правильные операции
    assert len(result) == 2
    assert result[0]["Дата операции"] == "2023-12-01"  # Проверяем первую операцию
    assert result[1]["Дата операции"] == "2023-12-09"  # Проверяем вторую операцию


def test_filter_operations_by_date_invalid_format() -> None:
    """Тест на выброс ValueError при неверном формате даты."""
    operations = [{"Дата операции": "2023-10-01"}, {"Дата операции": "2023-10-02"}]
    with pytest.raises(
        ValueError, match="Неверный формат даты: invalid_date. Ожидаемый формат: 'YYYY-MM-DD HH:MM:SS'"
    ):
        filter_operations_by_date(operations, "invalid_date")


# Тест для calculate_greeting
@patch("src.utils.datetime")
def test_calculate_greeting(mock_datetime: MagicMock) -> None:
    """
    Тестирует функцию calculate_greeting, проверяя, что она возвращает
    корректное приветствие в зависимости от времени суток.
    """
    mock_datetime.now.return_value = datetime(2023, 12, 15, 8, 0, 0)
    assert calculate_greeting() == "Доброе утро"


@pytest.mark.parametrize(
    "mock_hour, expected_greeting",
    [
        (8, "Доброе утро"),
        (12, "Добрый день"),
        (17, "Добрый день"),
        (19, "Добрый вечер"),
        (23, "Доброй ночи"),
        (3, "Доброй ночи"),
    ],
)
@patch("src.utils.datetime")
def test_calculate_all_greeting(mock_datetime: MagicMock, mock_hour: int, expected_greeting: str) -> None:
    """
    Тестирует функцию calculate_greeting с параметрами, проверяя,
    что она возвращает корректное приветствие в зависимости от времени суток.
    """
    mock_datetime.now.return_value = datetime(2023, 12, 15, mock_hour, 0, 0)
    assert calculate_greeting() == expected_greeting


# Тест для get_card_summary
@patch("src.utils.load_operations_data")
def test_get_card_summary(mock_load_operations_data: MagicMock) -> None:
    """
    Тестирует функцию get_card_summary, проверяя, что она правильно
    обрабатывает операции и формирует сводку по картам с учетом затрат и кэшбэка.
    """
    # Мокируем данные операций
    mock_load_operations_data.return_value = [
        {"Номер карты": "1234 5678 9012 3456", "Сумма операции": -1000, "Категория": "покупка"},
        {"Номер карты": "1234 5678 9012 3456", "Сумма операции": -500, "Категория": "покупка"},
        {"Номер карты": "1234 5678 9012 3456", "Сумма операции": -200, "Категория": "переводы"},
        {"Номер карты": "9876 5432 1098 7654", "Сумма операции": -1500, "Категория": "покупка"},
        {"Номер карты": "9876 5432 1098 7654", "Сумма операции": -300, "Категория": "покупка"},
        {"Номер карты": "4321 8765 2109 8765", "Сумма операции": 200, "Категория": "переводы"},
    ]

    result = get_card_summary(mock_load_operations_data.return_value)

    expected_results = [
        {"last_digits": "3456", "total_spent": -1700.0, "cashback": 15.0},  # Приводим к float  # Приводим к float
        {"last_digits": "7654", "total_spent": -1800.0, "cashback": 18.0},  # Приводим к float  # Приводим к float
        {"last_digits": "8765", "total_spent": 0.0, "cashback": 0.0},
    ]

    for expected in expected_results:
        result_card = next((card for card in result if card["last_digits"] == expected["last_digits"]), None)
        assert result_card is not None, f"Карта с последними цифрами {expected['last_digits']} не найдена."
        assert result_card["total_spent"] == expected["total_spent"], (
            f"Общая сумма затрат для карты {expected['last_digits']} должна быть {expected['total_spent']}, "
            f"но получено {result_card['total_spent']}"
        )
        assert result_card["cashback"] == expected["cashback"], (
            f"Кэшбэк для карты {expected['last_digits']} должен быть {expected['cashback']}, "
            f"но получено {result_card['cashback']}"
        )


def test_get_card_summary_no_matching_card(test_operations_data: list[dict]) -> None:
    """Тест на то, что функция возвращает карты с нулевыми значениями, если нет совпадений по картам."""
    operations = [
        {"Дата операции": "2023-10-01", "Сумма операции": -1000, "Номер карты": "9999", "Категория": "покупка"}
    ]

    # Мокируем функцию load_operations_data
    with patch("src.utils.load_operations_data") as mock_load_operations_data:
        # Настраиваем мок, чтобы он возвращал test_operations_data
        mock_load_operations_data.return_value = test_operations_data

        summary = get_card_summary(operations)

        # Ожидаем, что вернется список с картами из test_operations_data, у которых суммы будут 0.0
        expected_summary = [
            {"last_digits": "1234", "total_spent": 0.0, "cashback": 0.0},
            {"last_digits": "5678", "total_spent": 0.0, "cashback": 0.0},
        ]

        # Проверка без учета порядка
        assert sorted(summary, key=lambda x: x["last_digits"]) == sorted(
            expected_summary, key=lambda x: x["last_digits"]
        )


# Тест для get_top_transactions
def test_get_top_transactions() -> None:
    """
    Тестирует функцию get_top_transactions, проверяя, что она возвращает
    топ-5 транзакций с наибольшими расходами.
    """
    operations = [
        {"Дата операции": "2023-12-09", "Сумма операции": -600, "Категория": "еда", "Описание": "кафе"},
        {"Дата операции": "2023-12-08", "Сумма операции": -100, "Категория": "еда", "Описание": "кафе"},
        {"Дата операции": "2023-12-07", "Сумма операции": -1000, "Категория": "еда", "Описание": "кафе"},
        {"Дата операции": "2023-12-06", "Сумма операции": -1500, "Категория": "переводы", "Описание": "ЖКХ"},
        {"Дата операции": "2023-12-05", "Сумма операции": -5100, "Категория": "еда", "Описание": "кафе"},
        {"Дата операции": "2023-12-04", "Сумма операции": -100, "Категория": "еда", "Описание": "кафе"},
        {"Дата операции": "2023-12-03", "Сумма операции": -2200, "Категория": "еда", "Описание": "кафе"},
        {"Дата операции": "2023-12-02", "Сумма операции": -5000, "Категория": "переводы", "Описание": "кредит"},
        {"Дата операции": "2023-12-01", "Сумма операции": -500, "Категория": "еда", "Описание": "кафе"},
    ]

    result = get_top_transactions(operations)

    # Проверяем, что возвращается 5 транзакций с наибольшими расходами
    assert len(result) == 5
    assert result[0]["amount"] == -5100
    assert result[1]["amount"] == -5000
    assert result[2]["amount"] == -2200
    assert result[3]["amount"] == -1500
    assert result[4]["amount"] == -1000


# Тест для load_user_settings
@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["EUR"]}')
@patch("os.path.exists", return_value=True)
def test_load_user_settings(mock_exists: MagicMock, mock_file: MagicMock) -> None:
    """
    Тестирует функцию load_user_settings, проверяя, что она корректно
    загружает настройки пользователя из файла.
    """
    result = load_user_settings()
    assert "user_currencies" in result


def test_load_user_settings_file_not_found() -> None:
    """Тест на выброс FileNotFoundError, если файл не найден."""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError, match="Файл user_settings.json не найден."):
            load_user_settings()


# Тест для fetch_currency_rates
@patch("requests.get")
@patch("os.path.exists", return_value=True)  # Замокать os.path.exists
@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD"]}')  # Замокать open
def test_fetch_currency_rates(mock_open: MagicMock, mock_exists: MagicMock, mock_get: MagicMock) -> None:
    """
    Тестирует функцию fetch_currency_rates, проверяя, что она корректно
    получает курсы валют из API.
    """
    # Замокать ответ API
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"conversion_rates": {"RUB": 75, "USD": 1}}
    result = fetch_currency_rates()

    assert len(result) == 1  # Ожидаем, что вернется один курс
    assert result[0]["currency"] == "USD"  # Проверяем, что валюта USD
    assert result[0]["rate"] == 75  # Проверяем, что курс для USD равен 75


def test_fetch_currency_rates_no_data(mock_requests_get: MagicMock) -> None:
    """Тест на выброс ValueError, если нет данных по валюте."""
    # Мокируем функцию load_user_settings, чтобы вернуть фиктивные настройки
    with patch("src.utils.load_user_settings", return_value={"user_currencies": ["USD", "EUR"]}):
        mock_requests_get.return_value.json.return_value = {"conversion_rates": {}}
        with pytest.raises(ValueError, match="нет данных по валюте USD"):
            fetch_currency_rates()


def test_fetch_currency_rates_api_failure(mock_requests_get: MagicMock) -> None:
    """Тест на выброс ValueError, если не удалось получить курс валют."""
    with patch(
        "src.utils.load_user_settings",
        return_value={"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "TSLA"]},
    ):
        mock_requests_get.return_value.status_code = 500  # Эмуляция ошибки API
        with pytest.raises(ValueError, match="Не удалось получить курс валют"):
            fetch_currency_rates()


def test_fetch_currency_rates_failure(mock_requests_get: MagicMock) -> None:
    """Тест на выброс ValueError при ошибке получения курсов валют."""
    currency = "USD"
    with patch("src.utils.load_user_settings", return_value={"user_currencies": [currency]}):
        mock_requests_get.side_effect = RequestException("Ошибка сети")  # Эмуляция ошибки сети
        with pytest.raises(ValueError, match=f"Ошибка при получении курсов валют для {currency}: Ошибка сети"):
            fetch_currency_rates()


# Тест для fetch_stock_prices
@patch("requests.get")
@patch("src.utils.load_user_settings")  # Замокать load_user_settings
def test_fetch_stock_prices(mock_load_settings: MagicMock, mock_get: MagicMock) -> None:
    """
    Тестирует функцию fetch_stock_prices, проверяя, что она корректно
    получает цены акций из API на основе пользовательских настроек.
    """
    # Задайте фиктивные настройки с пользовательскими акциями
    mock_load_settings.return_value = {"user_stocks": ["AAPL", "GOOGL"]}

    # Создаем моки для ответов API
    mock_aapl_response = MagicMock()
    mock_aapl_response.json.return_value = {"results": [{"c": 150}]}
    mock_aapl_response.status_code = 200

    mock_googl_response = MagicMock()
    mock_googl_response.json.return_value = {"results": [{"c": 2800}]}
    mock_googl_response.status_code = 200

    # Настраиваем side_effect для mock_get, чтобы возвращать разные ответы
    mock_get.side_effect = [mock_aapl_response, mock_googl_response]

    # Вызов функции
    result = fetch_stock_prices()

    # Проверка результатов
    assert len(result) == 2  # Ожидаем 2 акции
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.00
    assert result[1]["stock"] == "GOOGL"
    assert result[1]["price"] == 2800.00


def test_fetch_stock_prices_no_stocks(mock_user_settings: dict[str, list[str]]) -> None:
    """Тест на возврат пустого списка, если нет акций."""
    with patch("src.utils.load_user_settings", return_value={"user_stocks": []}):
        prices = fetch_stock_prices()
        assert prices == []


def test_fetch_stock_prices_api_failure(mock_requests_get: MagicMock) -> None:
    """Тест на выброс ValueError, если не удалось получить данные по акциям."""
    with patch(
        "src.utils.load_user_settings",
        return_value={"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "TSLA"]},
    ):
        mock_requests_get.return_value.status_code = 500  # Эмуляция ошибки API
        with pytest.raises(ValueError, match="нет данных по акции AAPL"):
            fetch_stock_prices()


class TestFetchStockPrices(unittest.TestCase):

    @patch("src.utils.load_user_settings", return_value={"user_stocks": ["AAPL"]})
    @patch("src.utils.requests.get")
    def test_fetch_stock_prices_request_exception(
        self, mock_get: MagicMock, mock_load_user_settings: MagicMock
    ) -> None:
        # Настраиваем мок, чтобы он выбрасывал исключение RequestException
        mock_get.side_effect = RequestException

        # Проверяем, что функция вызывает ValueError с правильным сообщением
        with self.assertRaises(ValueError) as context:
            fetch_stock_prices()

        self.assertEqual(str(context.exception), "Не удалось узнать цены на акции")


def test_fetch_stock_prices_no_data(mock_requests_get: MagicMock) -> None:
    """Тест на выброс ValueError, если нет данных по акции."""
    # Мокируем функцию load_user_settings, чтобы она возвращала нужные настройки
    with patch(
        "src.utils.load_user_settings",
        return_value={"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "TSLA"]},
    ):
        mock_requests_get.return_value.json.return_value = {"results": []}
        with pytest.raises(ValueError, match="нет данных по акции AAPL"):
            fetch_stock_prices()


@pytest.mark.parametrize(
    "stocks, expected_errors",
    [
        (["AAPL", "GOOGL"], ["нет данных по акции AAPL", "нет данных по акции GOOGL"]),
    ],
)
@patch("src.utils.load_user_settings", return_value={"user_stocks": ["AAPL", "GOOGL"]})  # Мокируем функцию
@patch("requests.get")  # Мокируем запрос
def test_fetch_stock_prices_error_handling(
    mock_requests_get: MagicMock, mock_load_user_settings: MagicMock, stocks: list[str], expected_errors: list[str]
) -> None:
    """Тест на обработку ошибок при получении цен на акции."""
    mock_requests_get.return_value.json.return_value = {"results": []}  # Эмуляция отсутствия данных
    mock_requests_get.return_value.status_code = 200  # Эмуляция успешного запроса
    with pytest.raises(ValueError) as excinfo:
        fetch_stock_prices()

    # Проверяем, что все ожидаемые ошибки присутствуют в сообщении
    for error in expected_errors:
        assert error in str(excinfo.value)


def test_fetch_stock_prices_api_failure_2(mock_requests_get: MagicMock) -> None:
    """Тест на выброс ValueError, если не удалось получить цены на акции."""
    with patch(
        "src.utils.load_user_settings",
        return_value={"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "TSLA"]},
    ):
        mock_requests_get.return_value.status_code = 500  # Эмуляция ошибки API
        with pytest.raises(ValueError, match="нет данных по акции AAPL; нет данных по акции TSLA"):
            fetch_stock_prices()


def test_fetch_stock_prices_success(mock_requests_get: MagicMock) -> None:
    """Тест на успешное получение цен на акции."""
    with patch("src.utils.load_user_settings", return_value={"user_currencies": ["USD"], "user_stocks": ["AAPL"]}):
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json = lambda: {"results": [{"c": 150.00}]}

        prices = fetch_stock_prices()
        assert prices == [{"stock": "AAPL", "price": 150.00}]


def test_fetch_stock_prices_api_failure_3(mock_requests_get: MagicMock) -> None:
    """Тест на выброс ValueError, если не удалось получить цены на акции."""
    with patch(
        "src.utils.load_user_settings",
        return_value={"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "TSLA"]},
    ):
        mock_requests_get.return_value.status_code = 500  # Эмуляция ошибки API
        mock_requests_get.return_value.json = lambda: {}  # Эмуляция пустого ответа JSON

        with pytest.raises(ValueError, match="нет данных по акции AAPL; нет данных по акции TSLA"):
            fetch_stock_prices()
