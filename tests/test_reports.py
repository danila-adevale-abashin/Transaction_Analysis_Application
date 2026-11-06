import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.reports import report_decorator, spending_by_category


@pytest.fixture
def sample_dataframe():
    """Создает тестовый DataFrame с транзакциями."""
    return pd.DataFrame([
        # Трата в нужной категории, в пределах 90 дней
        {"date": datetime(2026, 11, 1), "amount": -1000.0, "default_category": "Супермаркеты"},
        # Трата в нужной категории, но слишком старая (более 90 дней назад)
        {"date": datetime(2026, 6, 1), "amount": -500.0, "default_category": "Супермаркеты"},
        # Трата в другой категории
        {"date": datetime(2026, 11, 2), "amount": -200.0, "default_category": "Фастфуд"},
        # Пополнение (положительная сумма)
        {"date": datetime(2026, 11, 3), "amount": 5000.0, "default_category": "Супермаркеты"}
    ])


def test_report_decorator(tmp_path):
    """Тест: декоратор сохраняет результат функции в файл."""
    # Создаем временный файл, который удалится после теста
    file_path = tmp_path / "test_report.csv"

    # Оборачиваем простую функцию нашим декоратором
    @report_decorator(str(file_path))
    def dummy_report():
        return pd.DataFrame([{"test_column": 123}])

    # Вызываем функцию
    result = dummy_report()

    # Проверяем, что файл создался
    assert file_path.exists()

    # Проверяем, что в файле действительно записаны данные
    df_from_file = pd.read_csv(file_path)
    assert "test_column" in df_from_file.columns
    assert df_from_file["test_column"][0] == 123


def test_spending_by_category(sample_dataframe, tmp_path):
    """Тест: фильтрация по категории и последним 90 дням."""
    file_path = tmp_path / "category_report.csv"

    decorated_func = report_decorator(str(file_path))(spending_by_category)

    result_df = decorated_func(sample_dataframe, "Супермаркеты", "2026-11-02")

    assert len(result_df) == 1
    assert result_df.iloc[0]["amount"] == -1000.0
    assert result_df.iloc[0]["default_category"] == "Супермаркеты"