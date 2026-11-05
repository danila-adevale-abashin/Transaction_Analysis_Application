import json
import logging
import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

from src.utils import load_user_settings, read_transactions_excel

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_DIR / "wiews.log", mode="w", encoding="utf-8")

    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def get_greeting(current_time: datetime) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    hour = current_time.hour

    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_card_stats(transactions: list[dict]) -> list[dict]:
    """Возвращает статистику по каждой карте (сумма расходов, кешбэк)."""
    cards = {}

    for t in transactions:
        amount = t.get("amount", 0)
        card = t.get("card_number", "")
        # Вытаскиваем кешбэк из Excel (если он пустой, считаем за 0)
        cashback = t.get("bonus_and_cashback", 0)

        # Ищем только карты и только расходы
        if card and amount < 0:
            last_digits = card.replace("*", "").strip()

            # Если карты еще нет в словаре, создаем для нее ячейки
            if last_digits not in cards:
                cards[last_digits] = {"spent": 0, "cashback": 0}

            # Прибавляем сумму траты (по модулю)
            cards[last_digits]["spent"] += abs(amount)
            # Прибавляем реальный кешбэк из файла
            cards[last_digits]["cashback"] += abs(cashback)

    # Собираем итоговый список для JSON
    result = []
    for last_digits, data in cards.items():
        result.append(
            {
                "last_digits": last_digits,
                "total_spent": round(data["spent"], 2),
                "cashback": round(data["cashback"], 2),
            }
        )

    return result


def get_top_transactions(transactions: list[dict], limit: int = 5) -> list[dict]:
    """Возвращает топ-N транзакций по сумме платежа (только расходы)."""

    # Фильтруем данные только по расходам
    expenses = [t for t in transactions if t.get("amount", 0) < 0]

    # Сортируем по модулю суммы
    sorted_expenses = sorted(expenses, key=lambda x: abs(x.get("amount", 0)), reverse=True)

    # Отбор указанного количества для ТОП
    top_expenses = sorted_expenses[:limit]

    result = []
    for t in top_expenses:
        raw_date = t.get("date")
        if hasattr(raw_date, "strftime"):
            formatted_date = raw_date.strftime("%d.%m.%Y")
        else:
            try:
                dt = datetime.strptime(str(raw_date)[:10], "%Y-%m-%d")
                formatted_date = dt.strftime("%d.%m.%Y")
            except ValueError:
                formatted_date = str(raw_date)

        result.append(
            {
                "date": formatted_date,
                "amount": round(abs(t.get("amount", 0)), 2),
                "category": t.get("default_category", ""),
                "description": t.get("description", ""),
            }
        )

    return result


def get_currency_rates(currencies: list[str]) -> list[dict]:
    """Получает курсы валют через API apilayer."""
    api_key = os.getenv("EXCHANGE_API_KEY")

    if not api_key:
        logger.error("API-ключ для валют не найден в .env")
        return []

    result = []
    for currency in currencies:
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={currency}&amount=1"
        headers = {"apikey": api_key}

        try:
            # Делаем запрос
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Проверяем, что нет ошибки 401 или 500

            data = response.json()

            # Достаем результат (курс 1 единицы валюты в рублях)
            rate = data.get("result")

            if rate:
                result.append({"currency": currency, "rate": round(rate, 2)})

        except requests.RequestException as e:
            logger.error(f"Ошибка API при получении курса {currency}: {e}")
            # Если ошибка, просто пропускаем эту валюту, чтобы программа не упала

    return result


def get_stock_prices(stocks: list[str]) -> list[dict]:
    """Получает текущие цены на акции через API Finnhub."""
    api_key = os.getenv("FINNHUB_API_KEY")

    if not api_key:
        logger.error("API-ключ для акций (FINNHUB_API_KEY) не найден в .env")
        return []

    result = []
    for stock in stocks:
        # Эндпоинт Finnhub для получения текущей котировки
        url = f"https://finnhub.io/api/v1/quote?symbol={stock}&token={api_key}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            # В Finnhub текущая цена лежит в поле 'c' (current price)
            price = data.get("c")

            # Если цена равна 0, значит акция не найдена или рынок закрыт
            if price and price > 0:
                result.append({"stock": stock, "price": round(float(price), 2)})
            else:
                logger.warning(f"Не удалось получить цену для {stock}: {data}")

        except requests.RequestException as e:
            logger.error(f"Ошибка API при получении цены {stock}: {e}")

    return result


import json
from datetime import datetime


def main_page_view(date_str: str, transactions: list[dict]) -> str:
    """Собирает JSON-ответ для главной страницы."""
    # Парсим дату из строки
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.error(f"Неверный формат даты: {date_str}")
        return "{}"

    # Определяем начало месяца для фильтрации
    start_of_month = datetime(target_date.year, target_date.month, 1)

    # Фильтруем транзакции
    filtered_transactions = []
    for t in transactions:
        raw_date = t.get("date")
        if not raw_date:
            continue

        if hasattr(raw_date, "to_pydatetime"):
            t_date = raw_date.to_pydatetime()
        elif isinstance(raw_date, datetime):
            t_date = raw_date
        else:
            try:
                t_date = datetime.strptime(str(raw_date)[:10], "%Y-%m-%d")
            except ValueError:
                continue

        # Проверяем, попадает ли дата в нужный диапазон (с 1 числа по целевую дату)
        if start_of_month <= t_date <= target_date:
            filtered_transactions.append(t)

    # Загружаем настройки (валюты и акции)
    settings = load_user_settings()
    currencies = settings.get("user_currencies", [])
    stocks = settings.get("user_stocks", [])

    # Собираем итоговый словарь
    result = {
        "greeting": get_greeting(target_date),
        "cards": get_card_stats(filtered_transactions),
        "top_transactions": get_top_transactions(filtered_transactions),
        "currency_rates": get_currency_rates(currencies),
        "stock_prices": get_stock_prices(stocks),
    }

    # Возвращаем JSON-строку
    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Проверка статистики карт
    data = read_transactions_excel("data/Operations Sun Oct 01 2023-Mon Nov 02 2026.xlsx")
    stats = get_card_stats(data)
    print(stats)

    # Проверка ТОП-транзакций
    top_5 = get_top_transactions(data)
    print(f"ТОП-5 ТРАНЗАКЦИЙ:" f"\n{top_5}")

    # Проверка курсов валют
    print("\n--- КУРСЫ ВАЛЮТ ---")
    currencies = ["USD", "EUR"]
    rates = get_currency_rates(currencies)
    print(rates)

    # Проверка акций
    print("\n--- АКЦИИ ---")
    stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    print(get_stock_prices(stocks))

    # Проверка главной страницы
    print("\n--- ГЛАВНАЯ СТРАНИЦА ---")
    # Берем дату из твоего файла, например 2026-11-01
    json_response = main_page_view("2026-11-01 23:59:59", data)
    print(json_response)
