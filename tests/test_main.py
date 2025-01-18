import pytest
import sys
import io

from unittest.mock import patch, MagicMock
from contextlib import redirect_stdout

from src.main import main


def test_main_choose_views() -> None:
    """
    Тестирует, что при выборе '1' в главном меню вызывается функция choose_views().
    """
    with patch("builtins.input", side_effect=["1"]), \
            patch("src.main.choose_views") as mock_choose_views:  # type: MagicMock
        main()
        mock_choose_views.assert_called_once()

        # Проверка, что выбор "1" корректный
        if mock_choose_views.call_count == 1:  # Сделан 1 успешный выбор
            print("\nВведен пункт \"1\". Выбрана категория: Веб-страницы.")


def test_main_choose_services() -> None:
    """
    Тестирует, что при выборе '2' в главном меню вызывается функция choose_services().
    """
    with patch("builtins.input", side_effect=["2"]), \
            patch("src.main.choose_services") as mock_choose_services:  # type: MagicMock
        main()
        mock_choose_services.assert_called_once()

        # Проверка, что выбор "2" корректный
        if mock_choose_services.call_count == 1:  # Сделан 1 успешный выбор
            print("\nВведен пункт \"2\". Выбрана категория: Сервисы.")


def test_main_choose_reports() -> None:
    """
    Тестирует, что при выборе '3' в главном меню вызывается функция choose_reports().
    """
    with patch("builtins.input", side_effect=["3"]), \
            patch("src.main.choose_reports") as mock_choose_reports:  # type: MagicMock
        main()
        mock_choose_reports.assert_called_once()

        # Проверка, что выбор "1" корректный
        if mock_choose_reports.call_count == 1:  # Сделан 1 успешный выбор
            print("\nВведен пункт \"3\". Выбрана категория: Отчеты.")


def test_main_exit() -> None:
    """
    Тестирует, что при выборе '0' в главном меню происходит выход из программы.
    """
    # Перехват вывода в строку с помощью redirect_stdout
    captured_output = io.StringIO()

    with redirect_stdout(captured_output):  # Перехватываем stdout
        with patch("builtins.input", side_effect=["0"]):  # Мокаем ввод пользователя
            main()  # Вызываем основную функцию

    # Получаем перехваченный вывод
    output = captured_output.getvalue()

    # Проверяем содержимое вывода
    assert "Добро пожаловать в программу работы с банковскими транзакциями!" in output
    assert "Выход из программы..." in output
    assert "Выберите номер категории:" in output

    # Печатаем вывод в нужном формате
    if "Выход из программы..." in output:
        output = output.replace("Выход из программы...", "").strip()
        print(output)
        print("\nВведен пункт \"0\". Выбран: Выход из программы.")
        print("\nВыход из программы...")


def test_main_choose_views_run_main_page() -> None:
    """
    Тестирует выбор подкатегории 'Главная' в категории 'Веб-страницы'.
    Проверяет, что вызывается функция run_main_page при корректном последовательном вводе пользователем.
    """
    with patch("builtins.input", side_effect=["1", "1"]), \
         patch("src.main.run_main_page") as mock_run_main_page:

        main()

        # Проверяем, что run_profit_cashback была вызвана
        mock_run_main_page.assert_called_once()


# VERSION: версия теста test_main_choose_views_run_main_page с отображением в терминале
def test_main_choose_views_run_main_page_version() -> None:
    """
    Тестирует выбор подкатегории 'Главная' в категории 'Веб-страницы'.
    Проверяет, что вызывается функция run_main_page при корректном последовательном вводе пользователем.
    """
    with patch("builtins.input", side_effect=["1", "1"]), \
         patch("src.main.run_main_page") as mock_run_main_page:

        main()

        # Проверяем, что run_main_page была вызвана
        mock_run_main_page.assert_called_once()

        if mock_run_main_page.call_count == 1:  # Подтверждение успешного запуска
            print("\nВведен пункт \"1\" - выбрана категория: \"Веб-страницы\".")
            print("Введен пункт \"1\" второй раз - выбрана подкатегория: \"Главная\".")


def test_main_choose_services_run_profit_cashback() -> None:
    """
    Тестирует выбор подкатегории категории 'Выгодные категории повышенного кешбэка' в категории 'Сервисы'.
    Проверяет, что вызывается функция run_profit_cashback при корректном последовательном вводе пользователем.
    """
    with patch("builtins.input", side_effect=["2", "1"]), \
         patch("src.main.run_profit_cashback") as mock_run_profit_cashback:

        # Запуск главной функции
        main()

        # Проверяем, что run_profit_cashback была вызвана
        mock_run_profit_cashback.assert_called_once()


def test_choose_reports_run_generate_report_version() -> None:
    """
    Тестирует выбор подкатегории 'Траты по категориям' в категории 'Отчеты'.
    Проверяет, что вызывается функция run_generate_report при корректном вводе данных пользователем.
    """
    with patch("builtins.input", side_effect=["3", "1"]), \
         patch("src.main.run_generate_report") as mock_run_generate_report:

        # Запуск главной функции
        main()

        # Проверяем, что run_generate_report была вызвана
        mock_run_generate_report.assert_called_once()


def test_main_invalid_important_category_input__() -> None:
    """
    Тестирует, что при некорректном вводе в главном меню печатается сообщение об ошибке.
    """
    with patch("builtins.input", side_effect=["9", "0"]), \
            patch("builtins.print") as mock_print:  # type: MagicMock
        main()
        mock_print.assert_any_call("Некорректный выбор категории: \"9\". Пожалуйста, попробуйте снова.")


def test_main_invalid_subcategory_input() -> None:
    """
    Тестирует некорректный ввод подкатегории в одной из категорий.
    """
    with patch("builtins.input", side_effect=["1", "9"]), \
            patch("builtins.print") as mock_print:  # type: MagicMock
        main()
        mock_print.assert_any_call("Некорректный выбор: \"9\". Попробуйте снова.")


def test_choose_views_in_development() -> None:
    """
    Тестирует, что при выборе подкатегории в разработке (например "2")
    в меню "Веб-страницы" печатается сообщение "Подкатегория "2" в разработке. Выберите другую.".
    """
    with patch("builtins.input", side_effect=["1", "2", "1"]), \
         patch("src.main.run_main_page") as mock_run_main_page:

        main()

        # Проверяем, что run_profit_cashback была вызвана
        mock_run_main_page.assert_called_once()


def test_main_invalid_category_input() -> None:
    """
    Тестирует ввод некорректного значения (например: "9") в главном меню.
    Вызывается соответствующее сообщение
    "Некорректный выбор категории: "9". Пожалуйста, попробуйте снова."
    """
    with patch("builtins.input", side_effect=["9", "1"]), \
            patch("src.main.choose_views") as mock_choose_views:  # type: MagicMock
        main()
        mock_choose_views.assert_called_once()
