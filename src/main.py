# from utils import main_page, events_page
# from cashback import profitable_categories, invest_savings, simple_search, search_by_phone, search_transfers
# from reports import expenses_by_category, expenses_by_weekday, expenses_on_weekend
from src.services import run_profit_cashback
from src.views import run_main_page


def main() -> None:
    """
    Приложение для анализа транзакций из Excel-файла.
    Генерирует JSON-данные для веб-страниц, формирует Excel-отчеты, а также предоставлять другие сервисы.
    """

    print(f"Привет! Добро пожаловать в программу работы с банковскими транзакциями.")

    while True:
        print("_" * 40)
        print("\nВыберите номер категории:")
        print("1. Веб-страницы")
        print("2. Отчеты")
        print("3. Сервисы")
        print("0. Выход")

        category_choice = input(">>> ").strip().upper()

        if category_choice == '1':
            while True:
                print("_" * 40)
                print("\nВыберите номер задачи для Веб-страниц:")
                print("1. Главная")
                print("2. События")
                print("0. Вернуться в главное меню")

                task_choice = input(">>> ").strip().upper()

                if task_choice == '1':
                    run_main_page()
                elif task_choice == '2':
                    events_page()
                elif task_choice == '0':
                    break
                else:
                    print("\nНеверный выбор, пожалуйста, попробуйте снова.")

        elif category_choice == '2':
            while True:
                print("_" * 40)
                print("\nВыберите номер задачи для Сервисов:")
                print("1. Выгодные категории повышенного кешбэка")
                print("2. Инвесткопилка")
                print("3. Простой поиск")
                print("4. Поиск по телефонным номерам")
                print("5. Поиск переводов физическим лицам")
                print("0. Вернуться в главное меню")

                task_choice = input(">>> ").strip().upper()

                if task_choice == '1':
                    print("Запуск сервиса 'Выгодные категории повышенного кешбэка'...")
                    run_profit_cashback()
                elif task_choice == '2':
                    print("Запуск сервиса 'Инвесткопилка'...")
                    invest_savings()
                elif task_choice == '3':
                    print("Запуск сервиса 'Простой поиск'...")
                    simple_search()
                elif task_choice == '4':
                    print("Запуск сервиса 'Поиск по телефонным номерам'...")
                    search_by_phone()
                elif task_choice == '5':
                    print("Запуск сервиса 'Поиск переводов физическим лицам'...")
                    search_transfers()
                elif task_choice == '0':
                    break  # Возврат в главное меню
                else:
                    print("Неверный выбор, пожалуйста, попробуйте снова.")

        elif category_choice == '3':
            while True:
                print("_" * 40)
                print("\nВыберите номер задачи для Отчетов:")
                print("1. Траты по категории")
                print("2. Траты по дням недели")
                print("3. Траты в рабочий/выходной день")
                print("0. Вернуться в главное меню")

                task_choice = input(">>> ").strip().upper()

                if task_choice == '1':
                    print("Запуск отчета 'Траты по категории'...")
                    expenses_by_category()
                elif task_choice == '2':
                    print("Запуск отчета 'Траты по дням недели'...")
                    expenses_by_weekday()
                elif task_choice == '3':
                    print("Запуск отчета 'Траты в рабочий/выходной день'...")
                    expenses_on_weekend()
                elif task_choice == '0':
                    break  # Возврат в главное меню
                else:
                    print("Неверный выбор, пожалуйста, попробуйте снова.")

        elif category_choice == '0':
            print("Выход из программы...")
            break  # Завершение программы

        else:
            print("Неверный выбор, пожалуйста, попробуйте снова.")

if __name__ == "__main__":
    main()
