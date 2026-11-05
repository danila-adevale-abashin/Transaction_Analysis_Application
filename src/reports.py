import functools
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from src.utils import read_transactions_excel

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_DIR / "reports.log", mode="w", encoding="utf-8")

    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def report_decorator(filename: str = "report.csv"):
    """Декоратор для сохранения результатов отчета в файл."""

    def decorator(func: Callable[..., pd.DataFrame]) -> Callable[..., pd.DataFrame]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> pd.DataFrame:

            result = func(*args, **kwargs)

            try:
                # Используем to_csv, чтобы сохранить таблицу
                result.to_csv(filename, index=False, encoding="utf-8")
                logger.info(f"Отчет успешно сохранен в {filename}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета: {e}")

            return result

        return wrapper

    return decorator


@report_decorator("spending_by_category.csv")
def spending_by_category(transactions: pd.DataFrame, category: str, date: str = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние 3 месяца (90 дней).

    :param transactions: Датафрейм с транзакциями
    :param category: Название категории
    :param date: Опциональная дата в формате 'YYYY-MM-DD'
    :return: Отфильтрованный Датафрейм
    """
    # Определяем целевую дату
    if date is None:
        target_date = datetime.now()
    else:
        target_date = datetime.strptime(date, "%Y-%m-%d")

    # Вычисляем дату начала (ровно 90 дней назад)
    start_date = target_date - timedelta(days=90)

    # Делаем копию датафрейма, чтобы не менять оригинал
    df = transactions.copy()

    # Фильтруем по дате
    date_col = "date" if "date" in df.columns else "Дата операции"
    df[date_col] = pd.to_datetime(df[date_col])

    # Фильтруем по датам (от start_date до target_date)
    df_filtered = df[(df[date_col] >= start_date) & (df[date_col] <= target_date)]

    # Фильтруем по категории
    cat_col = "default_category" if "default_category" in df.columns else "Категория по-умолчанию"
    df_filtered = df_filtered[df_filtered[cat_col] == category]

    # Берем только расходы (отрицательные суммы)
    amount_col = "amount" if "amount" in df.columns else "Сумма операции"
    df_filtered = df_filtered[df_filtered[amount_col] < 0]

    return df_filtered


if __name__ == "__main__":
    print("--- ОТЧЕТ ПО КАТЕГОРИИ ---")

    data_list = read_transactions_excel("../data/Operations Sun Oct 01 2023-Mon Nov 02 2026.xlsx")

    df = pd.DataFrame(data_list)

    result_df = spending_by_category(df, "Переводы", "2026-11-02")

    print(f"Найдено строк: {len(result_df)}")
    print(result_df.head(10))
