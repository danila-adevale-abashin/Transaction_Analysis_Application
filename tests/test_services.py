import pytest
from datetime import datetime
from src.services import investment_bank


@pytest.fixture
def test_transactions():
    """Набор тестовых транзакций."""
    return [
        {"date": datetime(2026, 11, 1, 12, 0), "amount": -1712.0},
        {"date": datetime(2026, 11, 2, 12, 0), "amount": -100.0},
        {"date": datetime(2026, 11, 3, 12, 0), "amount": 5000.0},
        {"date": datetime(2026, 10, 1, 12, 0), "amount": -500.0},
    ]


def test_investment_bank_limit_50(test_transactions):
    """Тест: считает сумму для Инвесткопилки с лимитом 50."""
    result = investment_bank("2026-11", test_transactions, 50)
    assert result == 38.0


def test_investment_bank_limit_100(test_transactions):
    """Тест: считает сумму для Инвесткопилки с лимитом 100."""
    result = investment_bank("2026-11", test_transactions, 100)
    assert result == 88.0


def test_investment_bank_wrong_month(test_transactions):
    """Тест: транзакции за другой месяц игнорируются."""
    result = investment_bank("2026-10", test_transactions, 50)
    assert result == 0.0


def test_investment_bank_zero_limit(test_transactions):
    """Тест: защита от нулевого или отрицательного лимита."""
    result = investment_bank("2026-11", test_transactions, 0)
    assert result == 0.0