import logging
from pathlib import Path
import pandas as pd
import json

logger = logging.getLogger(__name__)

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def read_transactions_excel(file_path: str) -> list[dict]:
    """Читает Excel-файл с транзакциями и возвращает список словарей."""
    logger.info(f"Чтение данных из Excel: {file_path}")

    try:
        # Читаем Excel
        df = pd.read_excel(file_path)
        df = df.fillna("")

        transactions = []
        for _, row in df.iterrows():
            transactions.append({
                'account_name': row['Имя счёта'],
                'card_number': row['Номер карты'],
                'date': row['Дата операции'],
                'amount': row['Сумма операции'],
                'currency_operation': row['Валюта операции'],
                'amount_in_the_account_currency': row['Сумма в валюте счёта'],
                'currency_in_the_account_currency': row['Валюта счёта'],
                'status': row['Статус'],
                'default_category': row['Категория по-умолчанию'],
                'your_category': row['Ваша категория'],
                'mcc': row['MCC'],
                'description': row['Описание'],
                'message': row['Сообщение'],
                'rounding_in': row['Округление'],
                'amount_of_the_rounding_operation': row['Сумма операции с округлением'],
                'bonus_and_cashback': row['Бонусы (включая кэшбэк)'],
                'analytics': row['Учёт в аналитике'],
            })
        return transactions
    except Exception as e:
        logger.error(f"Ошибка при чтении Excel файла: {e}")
        return []


def load_user_settings(file_path: str = "user_settings.json") -> dict:
    """Читает настройки пользователя из JSON-файла."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Файл настроек {file_path} не найден.")
        return {"user_currencies": [], "user_stocks": []}
    except json.JSONDecodeError:
        logger.error(f"Ошибка чтения JSON в файле {file_path}.")
        return {"user_currencies": [], "user_stocks": []}