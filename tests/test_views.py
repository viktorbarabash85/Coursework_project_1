import json
from unittest.mock import MagicMock, patch

from src.views import run_main_page  # Импортируем функцию для тестирования
from src.views import generate_main_page_data


@patch("builtins.input", side_effect=["2024-12-01 12:00:00"])  # Мокаем ввод пользователя
@patch("builtins.print")  # Мокаем вывод в консоль
@patch("src.views.generate_main_page_data")  # Мокаем функцию generate_main_page_data
def test_run_main_page(mock_generate_main_page_data: MagicMock, mock_print: MagicMock, mock_input: MagicMock) -> None:
    """
    Тестирует функцию run_main_page, проверяя корректность вызовов функций и вывода данных.
    """

    # Настраиваем возвращаемое значение замоканной функции generate_main_page_data
    mock_generate_main_page_data.return_value = {
        "greeting": "Добрый день",
        "cards": [{"last_digits": "1234", "total_spent": 100, "cashback": 1}],
        "top_transactions": [
            {"date": "01.12.2024", "amount": 100.0, "category": "Супермаркеты", "description": "Лента"}
        ],
        "currency_rates": [{"currency": "USD", "rate": 75.5}, {"currency": "EUR", "rate": 80.2}],
        "stock_prices": [{"stock": "AAPL", "price": 150}, {"stock": "GOOGL", "price": 2800}],
    }

    # Запускаем тестируемую функцию
    run_main_page()
    # Проверяем, что print вызван с ожидаемым разделителем
    mock_print.assert_any_call("_" * 40)

    # Проверяем, что print вызван с ожидаемым текстом
    mock_print.assert_any_call(
        'Страница "Главная".\n\n Предоставляет JSON-ответ с данными о расходах за месяц. '
        "Имеются данные с операциями за 2021-2024 годы. Выводится анализ данных с начала месяца введенной даты."
    )

    # Проверяем, что print вызван с ожидаемым текстом
    mock_print.assert_any_call("Введите дату и время в формате 'YYYY-MM-DD HH:MM:SS': ")

    # Проверяем, что input вызван с правильным приглашением
    mock_input.assert_called_once_with(">>> ")

    # Проверяем, что generate_main_page_data вызван с правильным аргументом
    mock_generate_main_page_data.assert_called_once_with("2024-12-01 12:00:00")

    # Проверяем, что print вызван с ожидаемым разделителем
    mock_print.assert_any_call("_" * 40)

    # Проверяем, что print вызван с ожидаемым результатом в формате JSON
    mock_print.assert_any_call(
        json.dumps(
            {
                "greeting": "Добрый день",
                "cards": [{"last_digits": "1234", "total_spent": 100, "cashback": 1}],
                "top_transactions": [
                    {"date": "01.12.2024", "amount": 100.0, "category": "Супермаркеты", "description": "Лента"}
                ],
                "currency_rates": [{"currency": "USD", "rate": 75.5}, {"currency": "EUR", "rate": 80.2}],
                "stock_prices": [{"stock": "AAPL", "price": 150}, {"stock": "GOOGL", "price": 2800}],
            },
            indent=4,
            ensure_ascii=False,
        )
    )


# Мокаем все вспомогательные функции
@patch("src.views.load_operations_data")
@patch("src.views.filter_operations_by_date")
@patch("src.views.calculate_greeting")
@patch("src.views.get_card_summary")
@patch("src.views.get_top_transactions")
@patch("src.views.fetch_currency_rates")
@patch("src.views.fetch_stock_prices")
def test_generate_main_page_data(
    mock_fetch_stock_prices: MagicMock,
    mock_fetch_currency_rates: MagicMock,
    mock_get_top_transactions: MagicMock,
    mock_get_card_summary: MagicMock,
    mock_calculate_greeting: MagicMock,
    mock_filter_operations_by_date: MagicMock,
    mock_load_operations_data: MagicMock,
    mock_generate_main_page_data: MagicMock,
) -> None:
    """
    Тестирует функцию generate_main_page_data, проверяя вызовы зависимых функций.
    """

    # Настраиваем возвращаемые значения замоканных функций
    mock_load_operations_data.return_value = [{"id": 1, "date": "2024-12-01", "amount": 100}]
    mock_filter_operations_by_date.return_value = [{"id": 1, "date": "2024-12-01", "amount": 100}]
    mock_calculate_greeting.return_value = "Добрый день"
    mock_get_card_summary.return_value = [{"last_digits": "1234", "total_spent": 100, "cashback": 1}]
    mock_get_top_transactions.return_value = [{"amount": 100}]
    mock_fetch_currency_rates.return_value = {"USD": 75.5, "EUR": 80.2}
    mock_fetch_stock_prices.return_value = {"AAPL": 150, "GOOGL": 2800}

    # Запускаем тестируемую функцию
    result = generate_main_page_data("2024-12-01 12:00:00")

    # Проверяем, что все зависимости вызваны корректно
    mock_load_operations_data.assert_called_once()
    mock_filter_operations_by_date.assert_called_once_with(
        [{"id": 1, "date": "2024-12-01", "amount": 100}], "2024-12-01 12:00:00"
    )
    mock_calculate_greeting.assert_called_once()
    mock_get_card_summary.assert_called_once_with([{"id": 1, "date": "2024-12-01", "amount": 100}])
    mock_get_top_transactions.assert_called_once_with([{"id": 1, "date": "2024-12-01", "amount": 100}])
    mock_fetch_currency_rates.assert_called_once()
    mock_fetch_stock_prices.assert_called_once()

    # Проверяем результат
    assert result == {
        "greeting": "Добрый день",
        "cards": [{"last_digits": "1234", "total_spent": 100, "cashback": 1}],
        "top_transactions": [{"amount": 100}],
        "currency_rates": {"USD": 75.5, "EUR": 80.2},
        "stock_prices": {"AAPL": 150, "GOOGL": 2800},
    }
