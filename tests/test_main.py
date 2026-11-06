import pytest
from unittest.mock import patch, Mock
from src.main import main


@patch('builtins.print')
def test_main_exit(mock_print, monkeypatch):
    """Тест: выход из программы (пункт 0)."""
    # Имитируем ввод "0" (выход)
    monkeypatch.setattr('builtins.input', lambda _: '0')
    # Имитируем существование файла
    with patch('src.main.os.path.exists', return_value=True):
        # Имитируем чтение транзакций
        with patch('src.main.read_transactions_excel', return_value=[{"test": 1}]):
            main()
            mock_print.assert_any_call("До свидания!")


@patch('builtins.print')
def test_main_page_json(mock_print, monkeypatch):
    """Тест: выбор пункта 1 (Главная страница)."""
    # Имитируем ввод: "1" (Главная), дата, потом "0" (Выход)
    inputs = iter(['1', '2026-11-01 12:00:00', '0'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    with patch('src.main.os.path.exists', return_value=True):
        with patch('src.main.read_transactions_excel', return_value=[{"test": 1}]):
            with patch('src.main.main_page_view', return_value='{"greeting": "test"}'):
                main()
                # Проверяем, что вывелся JSON
                mock_print.assert_any_call('{"greeting": "test"}')