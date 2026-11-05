import logging
import math
from typing import List, Dict, Any
from src.utils import read_transactions_excel

logger = logging.getLogger(__name__)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Считает сумму для инвесткопилки через округление трат."""
    if limit <= 0:
        logger.error("Лимит округления должен быть больше нуля")
        return 0.0

        # Функция-фильтр: оставляет только траты за нужный месяц

    def is_target_transaction(t: dict) -> bool:
        amount = t.get("amount", 0)
        t_date = t.get("date")

        # Проверяем, что это трата
        if amount >= 0 or not t_date:
            return False

        # Приводим дату к нужному формату и сравниваем
        if hasattr(t_date, "strftime"):
            date_str = t_date.strftime("%Y-%m")
        else:
            date_str = str(t_date)[:7]  # на случай, если дата пришла строкой '2026-11-01'

        return date_str == month

        # Функция расчета отложенной суммы для одной транзакции

    def calculate_rounding(t: dict) -> float:
        amount = abs(t["amount"])
        rounded_amount = math.ceil(amount / limit) * limit
        return rounded_amount - amount

        # Фильтруем, применяем расчет и суммируем (функциональный подход)

    filtered_transactions = filter(is_target_transaction, transactions)
    total_saved = sum(map(calculate_rounding, filtered_transactions))

    return round(total_saved, 2)


if __name__ == "__main__":

    print("--- ИНВЕСТКОПИЛКА ---")
    data = read_transactions_excel("data/Operations Sun Oct 01 2023-Mon Nov 02 2026.xlsx")

    # Проверяем за октябрь 2026 года, шаг округления 50 рублей
    saved_50 = investment_bank("2024-07", data, 50)
    print(f"С лимитом 50 руб. удалось бы отложить: {saved_50} руб.")

    # Проверяем с шагом в 100 рублей
    saved_100 = investment_bank("2024-07", data, 100)
    print(f"С лимитом 100 руб. удалось бы отложить: {saved_100} руб.")