from datetime import datetime
from src.utils import read_transactions_excel

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
        result.append({
            "last_digits": last_digits,
            "total_spent": round(data["spent"], 2),
            "cashback": round(data["cashback"], 2)
        })

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

        result.append({
            "date": formatted_date,
            "amount": round(abs(t.get("amount", 0)), 2),
            "category": t.get("default_category", ""),
            "description": t.get("description", "")
        })

    return result


if __name__ == "__main__":
    # Проверка статистики карт
    data = read_transactions_excel("data/Operations Sun Oct 01 2023-Mon Nov 02 2026.xlsx")
    stats = get_card_stats(data)
    print(stats)

    # Проверка ТОП-транзакций
    top_5 = get_top_transactions(data)
    print(f"ТОП-5 ТРАНЗАКЦИЙ:"
          f"\n{top_5}")