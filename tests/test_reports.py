import logging
import os
import json
import sys

from typing import Callable, Any, Dict
from unittest import mock

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open, MagicMock

from src.reports import run_generate_report, save_report_to_file, spending_by_category, logger
from src.reports import REPORTS_DIR



@mock.patch("src.reports.run_generate_report")
def test_main_function(mock_run_generate_report):
    """
    Тестирует выполнение главной функции.
    Проверяем, что вызов run_generate_report происходит без ошибок.
    """
    mock_run_generate_report()
    mock_run_generate_report.assert_called_once()


@pytest.mark.parametrize("category,date,expected", [
    ("еда", "2024-03-31", {"total_spent": -300.0, "transactions_count": 2}),
    ("транспорт", "2024-03-31", {"total_spent": -50.0, "transactions_count": 1}),
    ("одежда", "2024-03-31", {"total_spent": 0, "transactions_count": 0}),
])
def test_spending_by_category_general(mock_transactions, category, date, expected):
    """Тестирует общую информацию для разных категорий."""
    result = spending_by_category(mock_transactions, category, date)
    general_info = result["general_information"]

    assert general_info["total_spent"] == expected["total_spent"]
    assert general_info["transactions_count"] == expected["transactions_count"]


def test_no_data_for_category(empty_transactions):
    """
    Тестирует случай, когда нет данных для выбранной категории за указанный период.
    Проверяет, что возвращается нулевой отчет.
    """
    result = spending_by_category(empty_transactions, "еда", "2024-03-31")
    general_info = result["general_information"]

    assert general_info["total_spent"] == 0
    assert general_info["transactions_count"] == 0
    assert result["detailed_information"] == []


def test_spending_by_category_invalid_date(mock_transactions):
    """Тестирует обработку некорректной даты."""
    with pytest.raises(ValueError):
        spending_by_category(mock_transactions, "еда", "некорректная-дата")


@mock.patch("src.reports.logger")
@mock.patch("pandas.read_excel", side_effect=Exception("File not found"))
def test_run_generate_report_loading_error(mock_read_excel, mock_logger):
    """
    Тестирует обработку ошибки при загрузке данных в run_generate_report.
    Проверяется, что логируется ошибка и программа завершает выполнение.
    """
    with pytest.raises(SystemExit):  # Ожидаем завершение программы
        run_generate_report()

    mock_logger.error.assert_called_with("Ошибка при загрузке данных: File not found")


def test_spending_by_category_2(mock_transactions_2, mock_date):
    """
    Тест функции spending_by_category.
    """

    # Параметры теста
    category = "Еда"
    date = datetime.strptime(mock_date, "%Y-%m-%d")

    # Ожидаемые значения
    expected_general_info = {
        "category": category,
        "start_date": (date - timedelta(days=90)).strftime("%Y-%m-%d"),
        "end_date": mock_date,
        "total_spent": -400.0,
        "transactions_count": 2,
    }

    report = spending_by_category(mock_transactions_2, category, mock_date)

    assert report["general_information"] == expected_general_info
    assert len(report["detailed_information"]) == 2

    for record in report["detailed_information"]:
        assert record["category"].lower() == category.lower()


def test_spending_by_category_with_mock(mock_transactions_2):
    """
    Тест функции spending_by_category с замокированным текущим временем.
    """

    # Параметры теста
    category = "Еда"
    mock_now = datetime(2024, 12, 31)
    expected_general_info = {
        "category": category,
        "start_date": "2024-10-02",
        "end_date": "2024-12-31",
        "total_spent": -400.0,
        "transactions_count": 2,
    }

    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.strptime.side_effect = datetime.strptime

        report = spending_by_category(mock_transactions_2, category, date=mock_now.strftime("%Y-%m-%d"))

    assert report["general_information"] == expected_general_info
    assert len(report["detailed_information"]) == 2

    for record in report["detailed_information"]:
        assert record["category"].lower() == category.lower()


@patch("builtins.input")
@patch("src.reports.os.makedirs")  # Мокируем os.makedirs
@patch("builtins.open", new_callable=mock_open)  # Мокируем open для проверки записи файла
@patch("pandas.read_excel")  # Подмена загрузки Excel-файла
@patch("src.reports.spending_by_category")  # Замена реальной функции spending_by_category
def test_run_generate_report(
    mock_spending_by_category,
    mock_read_excel,
    mock_open_instance,
    mock_makedirs,
    mock_input
):
    """
    Мокированный тест функции run_generate_report.
    Принимает мокированный ввод данных от пользователя и корректно реагирует на нах.
    Корректно обрабатывает их с помощью мокированной функции `spending_by_category`.
    """

    # Мокация ввода: задаем значения, которые должны быть возвращены
    mock_input.side_effect = ["2024-12-15", "нет", "Еда", ""]

    # Подмена возвращаемого значения для pandas.read_excel
    mock_read_excel.return_value = pd.DataFrame({
        "Дата операции": ["2024-10-01", "2024-10-15"],
        "Сумма операции": [-100.0, -300.0],
        "Категория": ["Еда", "Еда"]
    })

    # Подмена результата функции spending_by_category
    mock_spending_by_category.return_value = {
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

    # Запуск тестируемой функции
    run_generate_report()


# Фиктивная функция для тестирования декоратора save_report_to_file (расположен ниже)
@save_report_to_file()
def dummy_function():
    return {
        "general_information": {
            "category": "еда",
            "start_date": "2024-01-01",
            "end_date": "2024-03-31",
            "total_spent": 1234.56,
            "transactions_count": 10,
        },
        "detailed_information": [
            {"date_amount": "2024-01-02", "transaction_amount": -100, "category": "еда"},
            {"date_amount": "2024-01-05", "transaction_amount": -200, "category": "еда"},
        ],
    }

@patch("src.reports.open", new_callable=mock_open)
def test_save_report_to_file(mock_open_instance):
    """
    Тестирует декоратор save_report_to_file:
    1. Проверяет, что файл создается.
    2. Проверяет, что в файл записываются корректные данные.
    """
    # Вызываем функцию, обернутую в декоратор
    dummy_function()

    # Проверяем, что файл был создан с корректным именем
    expected_file_name = os.path.join(
        REPORTS_DIR, "spending_еда_20240101_20240331.json"
    )
    mock_open_instance.assert_called_once_with(expected_file_name, "w", encoding="utf-8")

    # Проверяем, что в файл записаны корректные данные
    handle = mock_open_instance()

    # Собираем все данные, которые были записаны через handle.write
    written_data = "".join(call.args[0] for call in handle.write.call_args_list)

    # Формируем ожидаемые данные
    expected_data = json.dumps(
        dummy_function(),
        ensure_ascii=False,
        indent=4,
        default=str,
    )

    # Проверяем, что итоговое содержимое соответствует ожидаемому
    assert written_data == expected_data
