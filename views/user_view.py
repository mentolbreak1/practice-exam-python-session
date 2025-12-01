import tkinter as tk
from tkinter import ttk, messagebox

class UserView:
    def __init__(self, parent, user_controller, task_controller):
        self.user_controller = user_controller
        self.task_controller = task_controller
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_users()
        
    def setup_ui(self):
        """Настройка интерфейса пользователей"""
        # Панель управления
        control_frame = ttk.LabelFrame(self.frame, text="Управление пользователями", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Кнопки управления
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="Добавить пользователя", command=self.show_add_user_dialog).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit_user).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_user).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить список", command=self.load_users).pack(side='left', padx=5)
        
        # Поиск
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(fill='x', pady=10)
        
        ttk.Label(search_frame, text="Поиск по имени:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side='left', padx=5)
        ttk.Button(search_frame, text="Найти", command=self.search_users).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Сбросить", command=self.load_users).pack(side='left', padx=5)
        
        # Таблица пользователей
        table_frame = ttk.LabelFrame(self.frame, text="Список пользователей", padding=10)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('ID', 'Имя пользователя', 'Email', 'Роль', 'Дата регистрации', 'Задач')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        self.tree.column('ID', width=50)
        self.tree.column('Имя пользователя', width=150)
        self.tree.column('Email', width=200)
        self.tree.column('Дата регистрации', width=150)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def load_users(self):
        """Загрузка пользователей в таблицу"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Загружаем пользователей
        users = self.user_controller.get_all_users()
        
        for user in users:
            # Получаем количество задач пользователя
            tasks = self.task_controller.get_tasks_by_user(user.id)
            task_count = len(tasks)
            
            # Добавляем в таблицу
            self.tree.insert('', 'end', values=(
                user.id,
                user.username,
                user.email,
                self.get_role_text(user.role),
                user.registration_date.strftime('%d.%m.%Y %H:%M'),
                task_count
            ))
    
    def get_role_text(self, role):
        """Получить текстовое описание роли"""
        roles = {
            'admin': 'Администратор',
            'manager': 'Менеджер',
            'developer': 'Разработчик'
        }
        return roles.get(role, 'Неизвестно')
    
    def show_add_user_dialog(self):
        """Показать диалог добавления пользователя"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Добавить пользователя")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Заголовок
        ttk.Label(dialog, text="Добавить нового пользователя", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Форма
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # Имя пользователя
        ttk.Label(form_frame, text="Имя пользователя:*").grid(row=0, column=0, sticky='w', pady=10)
        username_entry = ttk.Entry(form_frame, width=30)
        username_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Email
        ttk.Label(form_frame, text="Email:*").grid(row=1, column=0, sticky='w', pady=10)
        email_entry = ttk.Entry(form_frame, width=30)
        email_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Роль
        ttk.Label(form_frame, text="Роль:*").grid(row=2, column=0, sticky='w', pady=10)
        role_var = tk.StringVar(value="developer")
        role_combo = ttk.Combobox(form_frame, textvariable=role_var, 
                                  values=['admin', 'manager', 'developer'], 
                                  state='readonly', width=20)
        role_combo.grid(row=2, column=1, pady=10, padx=10)
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_user():
            """Сохранение пользователя"""
            username = username_entry.get().strip()
            email = email_entry.get().strip()
            role = role_var.get()
            
            # Валидация
            if not username:
                messagebox.showerror("Ошибка", "Имя пользователя обязательно!")
                return
            
            if not email:
                messagebox.showerror("Ошибка", "Email обязателен!")
                return
            
            if '@' not in email:
                messagebox.showerror("Ошибка", "Введите корректный email!")
                return
            
            # Создаем пользователя
            user = self.user_controller.add_user(
                username=username,
                email=email,
                role=role
            )
            
            if user:
                messagebox.showinfo("Успех", "Пользователь успешно добавлен!")
                self.load_users()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить пользователя!")
        
        ttk.Button(button_frame, text="Сохранить", command=save_user).pack(side='left', padx=10)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side='left', padx=10)
    
    def edit_user(self):
        """Редактирование выбранного пользователя"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для редактирования!")
            return
        
        item = self.tree.item(selected[0])
        user_id = item['values'][0]
        
        # Получаем пользователя
        user = self.user_controller.get_user(user_id)
        if not user:
            messagebox.showerror("Ошибка", "Пользователь не найден!")
            return
        
        # Создаем диалог редактирования
        dialog = tk.Toplevel(self.frame)
        dialog.title("Редактировать пользователя")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Заголовок
        ttk.Label(dialog, text=f"Редактирование пользователя #{user_id}", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Форма
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # Имя пользователя
        ttk.Label(form_frame, text="Имя пользователя:*").grid(row=0, column=0, sticky='w', pady=10)
        username_entry = ttk.Entry(form_frame, width=30)
        username_entry.insert(0, user.username)
        username_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Email
        ttk.Label(form_frame, text="Email:*").grid(row=1, column=0, sticky='w', pady=10)
        email_entry = ttk.Entry(form_frame, width=30)
        email_entry.insert(0, user.email)
        email_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Роль
        ttk.Label(form_frame, text="Роль:*").grid(row=2, column=0, sticky='w', pady=10)
        role_var = tk.StringVar(value=user.role)
        role_combo = ttk.Combobox(form_frame, textvariable=role_var, 
                                  values=['admin', 'manager', 'developer'], 
                                  state='readonly', width=20)
        role_combo.grid(row=2, column=1, pady=10, padx=10)
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_changes():
            """Сохранение изменений"""
            username = username_entry.get().strip()
            email = email_entry.get().strip()
            role = role_var.get()
            
            # Валидация
            if not username:
                messagebox.showerror("Ошибка", "Имя пользователя обязательно!")
                return
            
            if not email:
                messagebox.showerror("Ошибка", "Email обязателен!")
                return
            
            if '@' not in email:
                messagebox.showerror("Ошибка", "Введите корректный email!")
                return
            
            # Обновляем пользователя
            success = self.user_controller.update_user(
                user_id=user_id,
                username=username,
                email=email,
                role=role
            )
            
            if success:
                messagebox.showinfo("Успех", "Пользователь успешно обновлен!")
                self.load_users()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить пользователя!")
        
        ttk.Button(button_frame, text="Сохранить", command=save_changes).pack(side='left', padx=10)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side='left', padx=10)
    
    def delete_user(self):
        """Удаление выбранного пользователя"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления!")
            return
        
        item = self.tree.item(selected[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        # Проверяем, есть ли задачи у пользователя
        tasks = self.task_controller.get_tasks_by_user(user_id)
        if tasks:
            messagebox.showwarning("Предупреждение", 
                                 f"У пользователя '{username}' есть {len(tasks)} задач. "
                                 f"Сначала перераспределите или удалите задачи.")
            return
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", 
                              f"Вы уверены, что хотите удалить пользователя '{username}'?"):
            success = self.user_controller.delete_user(user_id)
            if success:
                messagebox.showinfo("Успех", "Пользователь успешно удален!")
                self.load_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя!")
    
    def search_users(self):
        """Поиск пользователей"""
        query = self.search_entry.get().strip().lower()
        if not query:
            self.load_users()
            return
        
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Ищем пользователей
        users = self.user_controller.get_all_users()
        
        for user in users:
            # Проверяем совпадение
            if (query in user.username.lower() or 
                query in user.email.lower() or
                query in user.role.lower()):
                
                # Получаем количество задач пользователя
                tasks = self.task_controller.get_tasks_by_user(user.id)
                task_count = len(tasks)
                
                # Добавляем в таблицу
                self.tree.insert('', 'end', values=(
                    user.id,
                    user.username,
                    user.email,
                    self.get_role_text(user.role),
                    user.registration_date.strftime('%d.%m.%Y %H:%M'),
                    task_count
                ))
