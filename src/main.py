import logging
import os
from pathlib import Path

import pandas as pd

from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import read_transactions_excel
from src.wiews import main_page_view

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_DIR / "reports.log", mode="w", encoding="utf-8")

    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def main():
    data_path = "data/Operations Sun Oct 01 2023-Mon Nov 02 2026.xlsx"

    print("Привет! Добро пожаловать в приложение для анализа транзакций.")

    if not os.path.exists(data_path):
        print(f"Ошибка: Файл {data_path} не найден. Проверьте путь.")
        return

    print("Загрузка данных...")
    transactions = read_transactions_excel(data_path)
    if not transactions:
        print("Не удалось загрузить данные.")
        return

    while True:
        print("\nВыберите действие:")
        print("1. Главная страница (JSON)")
        print("2. Инвесткопилка")
        print("3. Отчет: Траты по категории")
        print("0. Выход")

        choice = input("\nВаш выбор: ")

        if choice == "0":
            print("До свидания!")
            break

        elif choice == "1":
            date_input = input("Введите дату и время (YYYY-MM-DD HH:MM:SS): ")
            try:
                json_result = main_page_view(date_input, transactions)
                print("\n--- JSON ДЛЯ ГЛАВНОЙ СТРАНИЦЫ ---")
                print(json_result)
            except Exception as e:
                print(f"Ошибка при генерации страницы: {e}")

        elif choice == "2":
            month = input("Введите месяц (YYYY-MM): ")
            limit = int(input("Введите лимит округления (10, 50, 100): "))
            try:
                saved = investment_bank(month, transactions, limit)
                print(f"\nС лимитом {limit} руб. удалось бы отложить: {saved} руб.")
            except Exception as e:
                print(f"Ошибка при расчете: {e}")

        elif choice == "3":
            category = input("Введите категорию (например, 'Супермаркеты', 'Переводы' и т.п.): ")
            date_input = input("Введите конечную дату (YYYY-MM-DD) или нажмите Enter для текущей: ")
            if not date_input:
                date_input = None

            try:
                df = pd.DataFrame(transactions)
                result_df = spending_by_category(df, category, date_input)
                print(f"\nОтчет сохранен в файл 'spending_by_category.csv'")
                print(f"Количество найденных транзакций: {len(result_df)}")
            except Exception as e:
                print(f"Ошибка при создании отчета: {e}")

        else:
            print("Неверный ввод. Попробуйте снова.")


if __name__ == "__main__":
    main()
