import pytest
import pandas as pd
from src.utils import read_transactions_excel


def test_read_transactions_excel_success(tmp_path):
    """Тест: успешное чтение Excel-файла."""
    # Создаем временный Excel-файл
    file_path = tmp_path / "test.xlsx"
    df = pd.DataFrame([
        {
            "Имя счёта": "Test", "Номер карты": "*1234", "Дата операции": pd.Timestamp("2026-11-01"),
            "Сумма операции": -100, "Валюта операции": "RUB", "Сумма в валюте счёта": -100,
            "Валюта счёта": "RUB", "Статус": "Ок", "Категория по-умолчанию": "Супермаркеты",
            "Ваша категория": "", "MCC": 0, "Описание": "Test", "Сообщение": "",
            "Округление": 0, "Сумма операции с округлением": -100, "Бонусы (включая кэшбэк)": 1,
            "Учёт в аналитике": "Да"
        }
    ])
    df.to_excel(file_path, index=False)

    result = read_transactions_excel(str(file_path))

    assert len(result) == 1
    assert result[0]["card_number"] == "*1234"
    assert result[0]["amount"] == -100