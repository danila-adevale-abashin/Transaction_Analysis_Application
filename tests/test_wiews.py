from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src.wiews import get_card_stats, get_currency_rates, get_greeting, get_stock_prices, get_top_transactions


@pytest.fixture
def test_transactions():
    """Набор тестовых транзакций в виде словарей."""
    return [
        {
            "card_number": "*1234",
            "amount": -1000.0,
            "date": datetime(2026, 11, 1),
            "default_category": "Супермаркеты",
            "description": "Пятерочка",
            "bonus_and_cashback": 10.0,
        },
        {
            "card_number": "*1234",
            "amount": -500.0,
            "date": datetime(2026, 11, 2),
            "default_category": "Фастфуд",
            "description": "Макдоналдс",
            "bonus_and_cashback": 5.0,
        },
        {
            "card_number": "*5678",
            "amount": -2000.0,
            "date": datetime(2026, 11, 3),
            "default_category": "Переводы",
            "description": "Другу",
            "bonus_and_cashback": 0.0,
        },
        {
            "card_number": "*1234",
            "amount": 5000.0,
            "date": datetime(2026, 11, 4),
            "default_category": "Пополнения",
            "description": "Зарплата",
            "bonus_and_cashback": 0.0,
        },
    ]


def test_get_greeting():
    """Тест: приветствие соответствует времени суток."""
    assert get_greeting(datetime(2026, 11, 1, 8, 0)) == "Доброе утро"
    assert get_greeting(datetime(2026, 11, 1, 14, 0)) == "Добрый день"
    assert get_greeting(datetime(2026, 11, 1, 20, 0)) == "Добрый вечер"
    assert get_greeting(datetime(2026, 11, 1, 2, 0)) == "Доброй ночи"


def test_get_card_stats(test_transactions):
    """Тест: статистика по картам считается верно (только расходы)."""
    result = get_card_stats(test_transactions)

    assert len(result) == 2

    card_1234 = next(c for c in result if c["last_digits"] == "1234")
    assert card_1234["total_spent"] == 1500.0
    assert card_1234["cashback"] == 15.0


def test_get_top_transactions(test_transactions):
    """Тест: топ-транзакции берут только расходы и сортируют по убыванию."""
    result = get_top_transactions(test_transactions, limit=2)

    assert len(result) == 2
    assert result[0]["amount"] == 2000.0
    assert result[0]["category"] == "Переводы"
    assert result[0]["date"] == "03.11.2026"


@patch("src.wiews.os.getenv")
@patch("src.wiews.requests.get")
def test_get_currency_rates(mock_get, mock_getenv):
    """Тест: курсы валют (с мок API)."""
    mock_getenv.return_value = "fake_api_key"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": 90.5}
    mock_get.return_value = mock_response

    result = get_currency_rates(["USD"])

    assert len(result) == 1
    assert result[0]["currency"] == "USD"
    assert result[0]["rate"] == 90.5
    mock_get.assert_called_once()


@patch("src.wiews.os.getenv")
@patch("src.wiews.requests.get")
def test_get_stock_prices(mock_get, mock_getenv):
    """Тест: цены на акции (с мок API Finnhub)."""
    mock_getenv.return_value = "fake_api_key"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"c": 150.12}
    mock_get.return_value = mock_response

    result = get_stock_prices(["AAPL"])

    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.12
    mock_get.assert_called_once()
