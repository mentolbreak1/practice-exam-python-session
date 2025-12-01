import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.main_window import MainWindow

def main():
    """Главная функция приложения"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
