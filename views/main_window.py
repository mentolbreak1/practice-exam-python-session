# Главное окно приложения согласно README.md
import tkinter as tk
from tkinter import ttk, messagebox
from views.task_view import TaskView
from views.project_view import ProjectView
from views.user_view import UserView
from database.database_manager import DatabaseManager
from controllers.task_controller import TaskController
from controllers.project_controller import ProjectController
from controllers.user_controller import UserController

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Система управления задачами")
        self.root.geometry("1200x700")
        
        # Инициализация базы данных и контроллеров
        self.db_manager = DatabaseManager()
        self.task_controller = TaskController(self.db_manager)
        self.project_controller = ProjectController(self.db_manager)
        self.user_controller = UserController(self.db_manager)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        # Создаем меню
        self.create_menu()
        
        # Создаем панель вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создаем вкладки
        self.task_view = TaskView(self.notebook, self.task_controller, 
                                  self.project_controller, self.user_controller)
        self.project_view = ProjectView(self.notebook, self.project_controller, 
                                        self.task_controller)
        self.user_view = UserView(self.notebook, self.user_controller, 
                                  self.task_controller)
        
        # Добавляем вкладки
        self.notebook.add(self.task_view.frame, text="Задачи")
        self.notebook.add(self.project_view.frame, text="Проекты")
        self.notebook.add(self.user_view.frame, text="Пользователи")
        
    def create_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        
    def show_about(self):
        """Показать информацию о программе"""
        messagebox.showinfo("О программе", 
                           "Система управления задачами\nВерсия 1.0\n\nРеализована с использованием:\n"
                           "- Python 3.8+\n- SQLite\n- Tkinter\n\nАрхитектура: MVC")
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()
    
    def __del__(self):
        """Деструктор - закрываем соединение с БД"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
