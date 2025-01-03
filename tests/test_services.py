from typing import Any, Dict, List, Tuple
from unittest.mock import call, patch

import pytest

from src.services import (_is_valid_operation, analyze_cashback, calculate_cashback, filter_operations,
                          log_filtered_operations, log_top_cashback, run_profit_cashback)


def test_is_valid_operation_invalid_date() -> None:
    op = {"Дата операции": "2023-03-15", "Категория": "Переводы", "Сумма операции": 100, "Статус": "SUCCESS"}
    assert _is_valid_operation(op, 2022, 3) is False


@patch("src.services.logger.error")
def test_invalid_date_format(mock_logger_error) -> None:
    operation = {
        "Дата операции": "2023/12/15",  # Некорректный формат даты
        "Категория": "Продукты",
        "Статус": "OK",
        "Сумма операции": -1000,
    }
    # Проверяем результат работы функции
    result = _is_valid_operation(operation, 2023, 15)
    assert result is False  # Убедимся, что функция вернула False

    # Проверяем, что ошибка логировалась
    mock_logger_error.assert_called_once_with(
        "Ошибка проверки на соответствие критериям. Ошибка: time data '2023/12/15' does not match format '%Y-%m-%d'"
    )


@pytest.mark.parametrize(
    "operation, year, month, expected",
    [
        (
            {"Дата операции": "2023-03-01", "Категория": "Еда", "Сумма операции": -1000, "Статус": "SUCCESS"},
            2023,
            3,
            True,
        ),
        (
            {"Дата операции": "2023-03-01", "Категория": "Переводы", "Сумма операции": -1000, "Статус": "SUCCESS"},
            2023,
            3,
            False,
        ),
        (
            {"Дата операции": "2023-03-01", "Категория": "Наличные", "Сумма операции": -1000, "Статус": "FAILED"},
            2023,
            3,
            False,
        ),
        (
            {"Дата операции": "2023-02-01", "Категория": "Еда", "Сумма операции": -1000, "Статус": "SUCCESS"},
            2023,
            3,
            False,
        ),
    ],
)
def test_is_valid_operation(operation: Dict[str, Any], year: int, month: int, expected: bool) -> None:
    """
    Тестирует функцию _is_valid_operation для проверки валидности операции.

    :param operation: Операция в виде словаря с данными о дате, категории, сумме и статусе.
    :param year: Год, с которым сравнивается дата операции.
    :param month: Месяц, с которым сравнивается дата операции.
    :param expected: Ожидаемый результат (True, если операция валидна, иначе False).
    """
    assert _is_valid_operation(operation, year, month) == expected


def test_filter_operations(mock_operations_data_2: List[Dict[str, Any]]) -> None:
    """
    Тестирует функцию filter_operations для фильтрации операций по дате.

    :param mock_operations_data_2: Мокированные данные операций для тестирования.
    """
    with patch("src.services.logger"):
        filtered = filter_operations(mock_operations_data_2, 2023, 3)
        assert filtered == [
            {"Дата операции": "2023-03-01", "Категория": "Еда", "Сумма операции": -1000, "Статус": "SUCCESS"},
            {"Дата операции": "2023-03-02", "Категория": "Транспорт", "Сумма операции": -500, "Статус": "SUCCESS"},
            {"Дата операции": "2023-03-03", "Категория": "Развлечения", "Сумма операции": -2000, "Статус": "SUCCESS"},
        ]  # Должно остаться 3 операции


@pytest.mark.parametrize(
    "operation, expected",
    [
        ({"Категория": "Еда", "Сумма операции": -1000}, ("Еда", 10.0)),
        ({"Категория": "Транспорт", "Сумма операции": -500}, ("Транспорт", 5.0)),
        ({"Категория": "Развлечения", "Сумма операции": -2000}, ("Развлечения", 20.0)),
        ({"Категория": "Кафе", "Сумма операции": -1500}, ("Кафе", 15.0)),
        ({"Категория": "Образование", "Сумма операции": -3000}, ("Образование", 30.0)),
        ({"Категория": "Спорт", "Сумма операции": -1200}, ("Спорт", 12.0)),
        ({"Категория": "Путешествия", "Сумма операции": -2500}, ("Путешествия", 25.0)),
        ({"Категория": "Магазин", "Сумма операции": -800}, ("Магазин", 8.0)),
        ({"Категория": "Книги", "Сумма операции": -600}, ("Книги", 6.0)),
        ({"Категория": "Здоровье", "Сумма операции": -400}, ("Здоровье", 4.0)),
    ],
)
def test_calculate_cashback(operation: Dict[str, Any], expected: Tuple[str, float]) -> None:
    """
    Тестирует функцию calculate_cashback для проверки расчета кэшбэка для различных операций.

    :param operation: Словарь, представляющий операцию.
    :param expected: Ожидаемый результат (категория и кэшбэк).
    """
    result = calculate_cashback(operation)
    assert result == expected


def test_analyze_cashback(mock_operations_data_filtered: List[Dict[str, Any]]) -> None:
    """
    Тестирует функцию analyze_cashback для анализа операций и расчета кэшбэка по заданным категориям.

    :param mock_operations_data_filtered: Мокированные данные операций для анализа.
    """
    with patch("src.services.filter_operations", return_value=mock_operations_data_filtered), patch(
        "src.services.calculate_cashback"
    ) as mock_calculate_cashback:
        mock_calculate_cashback.side_effect = lambda op: (op["Категория"], float(-op["Сумма операции"] // 100))
        results = analyze_cashback(mock_operations_data_filtered, 2023, 3)

        # Ожидаемые результаты для топ-3 категорий
        expected_results = {"Образование": 39.0, "Развлечения": 38.0, "Путешествия": 25.0}

        assert results == expected_results


@patch("builtins.input", side_effect=["2023", "12"])  # Корректные год и месяц
@patch(
    "src.services.load_operations_data",
    return_value=[
        {"Дата операции": "2023-12-01", "Категория": "Продукты", "Сумма операции": -500, "Статус": "COMPLETED"}
    ],
)
@patch("src.services.analyze_cashback", return_value={"Продукты": 5})
def test_run_profit_cashback_2(mock_analyze_cashback, mock_load_operations_data, mock_input) -> None:
    """
    Проверяет корректную последовательность выполнения функций.
    Результат анализа корректно выводится
    """
    with patch("builtins.print") as mock_print:
        run_profit_cashback()

    # Проверяем, что данные загружены
    mock_load_operations_data.assert_called_once()

    # Проверяем, что анализ кэшбэка выполнен
    mock_analyze_cashback.assert_called_once_with(
        [{"Дата операции": "2023-12-01", "Категория": "Продукты", "Сумма операции": -500, "Статус": "COMPLETED"}],
        2023,
        12,
    )

    # Проверяем вывод результата
    mock_print.assert_any_call('{\n    "Продукты": 5\n}')


@patch("src.services.logger")  # Замокайте именно логгер, а не функцию
def test_log_filtered_operations(mock_logger) -> None:
    filtered_ops = [{"Дата операции": "2023-03-15", "Категория": "Покупки", "Сумма операции": -100}]
    log_filtered_operations(filtered_ops)

    # Здесь мы проверяем, что логирование произошло с ожидаемым сообщением
    mock_logger.info.assert_called_once_with("Фильтрация операций завершена. Найдено 1 операций.")


@patch("src.services.logger")
def test_log_top_cashback(mock_logger) -> None:
    top_cashback = {"Покупки": 100.0, "Рестораны": 50.0}
    log_top_cashback(top_cashback)
    mock_logger.info.assert_any_call("Категория: Покупки, сумма кэшбэка: 100.0")
    mock_logger.info.assert_any_call("Категория: Рестораны, сумма кэшбэка: 50.0")


@patch("src.services.load_operations_data")
@patch("builtins.input", side_effect=["2023", "3"])
@patch("src.services.logger")
def test_run_profit_cashback(mock_logger, mock_input, mock_load_data) -> None:
    mock_load_data.return_value = [{"Дата операции": "2023-03-15", "Категория": "Покупки", "Сумма операции": -100}]
    run_profit_cashback()
    mock_logger.info.assert_any_call("Данные операций успешно загружены.")


@patch("builtins.input", side_effect=["abc", "2025", "2023"])  # год (not) -> год (not) -> год (ок)
@patch("src.services.logger.error")
def test_invalid_year_input(mock_logger_error, mock_input) -> None:
    """
    Некорректный ввод года
    """
    with patch("src.services.load_operations_data", return_value=[]):
        run_profit_cashback()

    # Проверяем, что логирование некорректного года выполнено
    mock_logger_error.assert_any_call("Некорректный ввод года: abc.")
    mock_logger_error.assert_any_call("Некорректный ввод года: 2025.")


@patch("builtins.input", side_effect=["2024", "0", "13", "6"])  # год (ок) -> месяц (not) -> not -> ок
@patch("src.services.logger.error")
def test_invalid_month_input(mock_logger_error, mock_input) -> None:
    """
    Проверяем, что логгер фиксирует ошибки при некорректном вводе месяца.
    """
    with patch("src.services.load_operations_data", return_value=[]):  # Подмена данных
        run_profit_cashback()

    # Ожидаемые вызовы логгера для месяцев
    expected_calls = [
        call("Некорректный ввод месяца: 0."),  # Некорректный ввод "0"
        call("Некорректный ввод месяца: 13."),  # Некорректный ввод "13"
    ]

    # Проверяем, что все вызовы логгера для месяца были сделаны
    mock_logger_error.assert_has_calls(expected_calls, any_order=False)
    print(mock_logger_error.call_args_list)

    # Убедимся, что вызова "Ошибка при загрузке данных" нет
    for error_call in mock_logger_error.call_args_list:
        assert "Ошибка при загрузке данных" not in error_call[0][0]


@patch("src.services.load_operations_data", side_effect=Exception("Ошибка загрузки данных"))
@patch("src.services.logger.error")
def test_data_load_error(mock_logger_error, mock_load_operations_data) -> None:
    run_profit_cashback()

    # Проверяем, что ошибка загрузки данных залогирована
    mock_logger_error.assert_called_once_with("Ошибка при загрузке данных: Ошибка загрузки данных")
