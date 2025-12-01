import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

class TaskView:
    def __init__(self, parent, task_controller, project_controller, user_controller):
        self.task_controller = task_controller
        self.project_controller = project_controller
        self.user_controller = user_controller
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_tasks()
        self.load_projects()
        self.load_users()
        
    def setup_ui(self):
        """Настройка интерфейса задач"""
        # Панель управления
        control_frame = ttk.LabelFrame(self.frame, text="Управление задачами", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Кнопки управления
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="Добавить задачу", command=self.show_add_task_dialog,
                  style="Accent.TButton").pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit_task).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_task).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить список", command=self.load_tasks).pack(side='left', padx=5)
        
        # Создаем стиль для акцентной кнопки
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#0078d4")
        
        # Поиск
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(fill='x', pady=10)
        
        ttk.Label(search_frame, text="Поиск:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side='left', padx=5)
        ttk.Button(search_frame, text="Найти", command=self.search_tasks).pack(side='left', padx=5)
        
        # Фильтры
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(fill='x')
        
        ttk.Label(filter_frame, text="Статус:").pack(side='left', padx=5)
        self.status_filter = ttk.Combobox(filter_frame, values=['Все', 'pending', 'in_progress', 'completed'], 
                                         width=15, state='readonly')
        self.status_filter.set('Все')
        self.status_filter.pack(side='left', padx=5)
        
        ttk.Label(filter_frame, text="Приоритет:").pack(side='left', padx=5)
        self.priority_filter = ttk.Combobox(filter_frame, values=['Все', '1', '2', '3'], 
                                           width=10, state='readonly')
        self.priority_filter.set('Все')
        self.priority_filter.pack(side='left', padx=5)
        
        ttk.Button(filter_frame, text="Фильтровать", command=self.filter_tasks).pack(side='left', padx=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters).pack(side='left', padx=5)
        
        # Таблица задач
        table_frame = ttk.LabelFrame(self.frame, text="Список задач", padding=10)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('ID', 'Название', 'Приоритет', 'Статус', 'Срок', 'Проект', 'Исполнитель')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        column_widths = {
            'ID': 50,
            'Название': 200,
            'Приоритет': 80,
            'Статус': 100,
            'Срок': 120,
            'Проект': 150,
            'Исполнитель': 150
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Настраиваем тэги для цветового кодирования
        self.tree.tag_configure('high', background='#ffcccc')  # Красный для высокого приоритета
        self.tree.tag_configure('medium', background='#ffffcc')  # Желтый для среднего
        self.tree.tag_configure('low', background='#ccffcc')  # Зеленый для низкого
        self.tree.tag_configure('overdue', foreground='red')  # Красный текст для просроченных
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def load_tasks(self):
        """Загрузка задач в таблицу"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Загружаем задачи
        tasks = self.task_controller.get_all_tasks()
        
        for task in tasks:
            # Получаем название проекта
            project_name = "Без проекта"
            if task.project_id:
                project = self.project_controller.get_project(task.project_id)
                if project:
                    project_name = project.name
            
            # Получаем имя исполнителя
            assignee_name = "Не назначен"
            if task.assignee_id:
                user = self.user_controller.get_user(task.assignee_id)
                if user:
                    assignee_name = user.username
            
            # Определяем теги для цветового кодирования
            tags = []
            if task.priority == 1:
                tags.append('high')
            elif task.priority == 2:
                tags.append('medium')
            elif task.priority == 3:
                tags.append('low')
            
            # Помечаем просроченные задачи
            if task.is_overdue():
                tags.append('overdue')
            
            # Добавляем в таблицу
            self.tree.insert('', 'end', values=(
                task.id,
                task.title,
                self.get_priority_text(task.priority),
                self.get_status_text(task.status),
                task.due_date.strftime('%d.%m.%Y %H:%M'),
                project_name,
                assignee_name
            ), tags=tags)
    
    def load_projects(self):
        """Загрузка списка проектов"""
        self.projects = self.project_controller.get_all_projects()
    
    def load_users(self):
        """Загрузка списка пользователей"""
        self.users = self.user_controller.get_all_users()
    
    def get_priority_text(self, priority):
        """Получить текстовое описание приоритета"""
        priorities = {1: 'Высокий', 2: 'Средний', 3: 'Низкий'}
        return priorities.get(priority, 'Неизвестно')
    
    def get_status_text(self, status):
        """Получить текстовое описание статуса"""
        statuses = {
            'pending': 'Ожидает',
            'in_progress': 'В работе',
            'completed': 'Завершена'
        }
        return statuses.get(status, 'Неизвестно')
    
    def show_add_task_dialog(self):
        """Показать диалог добавления задачи"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Добавить задачу")
        dialog.geometry("500x550")
        dialog.resizable(False, False)
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Заголовок
        ttk.Label(dialog, text="Добавить новую задачу", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Форма
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        row = 0
        
        # Название
        ttk.Label(form_frame, text="Название:*").grid(row=row, column=0, sticky='w', pady=5)
        title_entry = ttk.Entry(form_frame, width=40)
        title_entry.grid(row=row, column=1, pady=5, padx=10)
        row += 1
        
        # Описание
        ttk.Label(form_frame, text="Описание:").grid(row=row, column=0, sticky='w', pady=5)
        description_text = tk.Text(form_frame, width=30, height=5)
        description_text.grid(row=row, column=1, pady=5, padx=10)
        row += 1
        
        # Приоритет
        ttk.Label(form_frame, text="Приоритет:*").grid(row=row, column=0, sticky='w', pady=5)
        priority_var = tk.StringVar(value="2")
        priority_combo = ttk.Combobox(form_frame, textvariable=priority_var, 
                                      values=['1 - Высокий', '2 - Средний', '3 - Низкий'], 
                                      state='readonly', width=20)
        priority_combo.grid(row=row, column=1, pady=5, padx=10)
        row += 1
        
        # Срок выполнения
        ttk.Label(form_frame, text="Срок выполнения:*").grid(row=row, column=0, sticky='w', pady=5)
        due_date_entry = DateEntry(form_frame, width=20, date_pattern='yyyy-mm-dd')
        due_date_entry.grid(row=row, column=1, pady=5, padx=10)
        row += 1
        
        # Проект
        ttk.Label(form_frame, text="Проект:").grid(row=row, column=0, sticky='w', pady=5)
        project_var = tk.StringVar()
        project_names = ['Без проекта'] + [p.name for p in self.projects]
        project_combo = ttk.Combobox(form_frame, textvariable=project_var, 
                                     values=project_names, state='readonly', width=20)
        project_combo.grid(row=row, column=1, pady=5, padx=10)
        row += 1
        
        # Исполнитель
        ttk.Label(form_frame, text="Исполнитель:").grid(row=row, column=0, sticky='w', pady=5)
        user_var = tk.StringVar()
        user_names = ['Не назначен'] + [u.username for u in self.users]
        user_combo = ttk.Combobox(form_frame, textvariable=user_var, 
                                  values=user_names, state='readonly', width=20)
        user_combo.grid(row=row, column=1, pady=5, padx=10)
        row += 1
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_task():
            """Сохранение задачи"""
            title = title_entry.get().strip()
            description = description_text.get("1.0", tk.END).strip()
            priority = int(priority_var.get().split(' ')[0])
            due_date = due_date_entry.get_date()
            
            # Получаем ID проекта
            project_id = None
            selected_project = project_var.get()
            if selected_project != 'Без проекта':
                for project in self.projects:
                    if project.name == selected_project:
                        project_id = project.id
                        break
            
            # Получаем ID исполнителя
            assignee_id = None
            selected_user = user_var.get()
            if selected_user != 'Не назначен':
                for user in self.users:
                    if user.username == selected_user:
                        assignee_id = user.id
                        break
            
            # Валидация
            if not title:
                messagebox.showerror("Ошибка", "Название задачи обязательно!")
                return
            
            # Создаем задачу
            task = self.task_controller.add_task(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                project_id=project_id,
                assignee_id=assignee_id
            )
            
            if task:
                messagebox.showinfo("Успех", "Задача успешно добавлена!")
                self.load_tasks()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить задачу!")
        
        ttk.Button(button_frame, text="Сохранить", command=save_task, 
                  style="Accent.TButton").pack(side='left', padx=10)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side='left', padx=10)
    
    def edit_task(self):
        """Редактирование выбранной задачи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите задачу для редактирования!")
            return
        
        item = self.tree.item(selected[0])
        task_id = item['values'][0]
        
        # Получаем задачу
        task = self.task_controller.get_task(task_id)
        if not task:
            messagebox.showerror("Ошибка", "Задача не найдена!")
            return
        
        # Создаем диалог редактирования
        dialog = tk.Toplevel(self.frame)
        dialog.title("Редактировать задачу")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Заголовок
        ttk.Label(dialog, text=f"Редактирование задачи #{task_id}", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Форма
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        row = 0
        
        # Название
        ttk.Label(form_frame, text="Название:*").grid(row=row, column=0, sticky='w', pady=5)
        title_entry = ttk.Entry(form_frame, width=40)
        title_entry.insert(0, task.title)
        title_entry.grid(row=row, column=1, pady=5, padx=10)
        row += 1
        
        # Описание
        ttk.Label(form_frame, text="Описание:").grid(row=row, column=0, sticky='w', pady=5)
        description_text = tk.Text(form_frame, width=30, height=5)
        description_text.insert("1.0", task.description)
        description_text.grid(row=row, column=1, pady=5, padx=10)
        row += 1
        
        # Приоритет
        ttk.Label(form_frame, text="Приоритет:*").grid(row=row, column=0, sticky='w', pady=5)
        priority_var = tk.StringVar(value=str(task.priority))
        priority_combo = ttk.Combobox(form_frame, textvariable=priority_var, 
                                      values=['1', '2', '3'], state='readonly', width=20)
        priority_combo.grid(row=row, column=1, pady=5, padx=10)
        row += 1
        
        # Статус
        ttk.Label(form_frame, text="Статус:*").grid(row=row, column=0, sticky='w', pady=5)
        status_var = tk.StringVar(value=task.status)
        status_combo = ttk.Combobox(form_frame, textvariable=status_var, 
                                    values=['pending', 'in_progress', 'completed'], 
                                    state='readonly', width=20)
        status_combo.grid(row=row, column=1, pady=5, padx=10)
        row += 1
        
        # Срок выполнения
        ttk.Label(form_frame, text="Срок выполнения:*").grid(row=row, column=0, sticky='w', pady=5)
        due_date_entry = DateEntry(form_frame, width=20, date_pattern='yyyy-mm-dd')
        due_date_entry.set_date(task.due_date)
        due_date_entry.grid(row=row, column=1, pady=5, padx=10)
        row += 1
        
        # Проект (только для информации)
        ttk.Label(form_frame, text="Проект:").grid(row=row, column=0, sticky='w', pady=5)
        project_name = "Без проекта"
        if task.project_id:
            project = self.project_controller.get_project(task.project_id)
            if project:
                project_name = project.name
        ttk.Label(form_frame, text=project_name).grid(row=row, column=1, sticky='w', pady=5, padx=10)
        row += 1
        
        # Исполнитель (только для информации)
        ttk.Label(form_frame, text="Исполнитель:").grid(row=row, column=0, sticky='w', pady=5)
        assignee_name = "Не назначен"
        if task.assignee_id:
            user = self.user_controller.get_user(task.assignee_id)
            if user:
                assignee_name = user.username
        ttk.Label(form_frame, text=assignee_name).grid(row=row, column=1, sticky='w', pady=5, padx=10)
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_changes():
            """Сохранение изменений"""
            title = title_entry.get().strip()
            description = description_text.get("1.0", tk.END).strip()
            priority = int(priority_var.get())
            status = status_var.get()
            due_date = due_date_entry.get_date()
            
            # Валидация
            if not title:
                messagebox.showerror("Ошибка", "Название задачи обязательно!")
                return
            
            # Обновляем задачу
            success = self.task_controller.update_task(
                task_id=task_id,
                title=title,
                description=description,
                priority=priority,
                status=status,
                due_date=due_date
            )
            
            if success:
                messagebox.showinfo("Успех", "Задача успешно обновлена!")
                self.load_tasks()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить задачу!")
        
        ttk.Button(button_frame, text="Сохранить", command=save_changes,
                  style="Accent.TButton").pack(side='left', padx=10)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side='left', padx=10)
    
    def delete_task(self):
        """Удаление выбранной задачи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления!")
            return
        
        item = self.tree.item(selected[0])
        task_id = item['values'][0]
        task_title = item['values'][1]
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", 
                              f"Вы уверены, что хотите удалить задачу '{task_title}'?"):
            success = self.task_controller.delete_task(task_id)
            if success:
                messagebox.showinfo("Успех", "Задача успешно удалена!")
                self.load_tasks()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить задачу!")
    
    def search_tasks(self):
        """Поиск задач"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Предупреждение", "Введите текст для поиска!")
            return
        
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Ищем задачи
        tasks = self.task_controller.search_tasks(query)
        
        for task in tasks:
            # Получаем название проекта
            project_name = "Без проекта"
            if task.project_id:
                project = self.project_controller.get_project(task.project_id)
                if project:
                    project_name = project.name
            
            # Получаем имя исполнителя
            assignee_name = "Не назначен"
            if task.assignee_id:
                user = self.user_controller.get_user(task.assignee_id)
                if user:
                    assignee_name = user.username
            
            # Определяем теги для цветового кодирования
            tags = []
            if task.priority == 1:
                tags.append('high')
            elif task.priority == 2:
                tags.append('medium')
            elif task.priority == 3:
                tags.append('low')
            
            # Помечаем просроченные задачи
            if task.is_overdue():
                tags.append('overdue')
            
            # Добавляем в таблицу
            self.tree.insert('', 'end', values=(
                task.id,
                task.title,
                self.get_priority_text(task.priority),
                self.get_status_text(task.status),
                task.due_date.strftime('%d.%m.%Y %H:%M'),
                project_name,
                assignee_name
            ), tags=tags)
    
    def filter_tasks(self):
        """Фильтрация задач"""
        status_filter = self.status_filter.get()
        priority_filter = self.priority_filter.get()
        
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получаем все задачи
        tasks = self.task_controller.get_all_tasks()
        
        for task in tasks:
            # Применяем фильтры
            if status_filter != 'Все' and task.status != status_filter:
                continue
            
            if priority_filter != 'Все' and str(task.priority) != priority_filter:
                continue
            
            # Получаем название проекта
            project_name = "Без проекта"
            if task.project_id:
                project = self.project_controller.get_project(task.project_id)
                if project:
                    project_name = project.name
            
            # Получаем имя исполнителя
            assignee_name = "Не назначен"
            if task.assignee_id:
                user = self.user_controller.get_user(task.assignee_id)
                if user:
                    assignee_name = user.username
            
            # Определяем теги для цветового кодирования
            tags = []
            if task.priority == 1:
                tags.append('high')
            elif task.priority == 2:
                tags.append('medium')
            elif task.priority == 3:
                tags.append('low')
            
            # Помечаем просроченные задачи
            if task.is_overdue():
                tags.append('overdue')
            
            # Добавляем в таблицу
            self.tree.insert('', 'end', values=(
                task.id,
                task.title,
                self.get_priority_text(task.priority),
                self.get_status_text(task.status),
                task.due_date.strftime('%d.%m.%Y %H:%M'),
                project_name,
                assignee_name
            ), tags=tags)
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.status_filter.set('Все')
        self.priority_filter.set('Все')
        self.search_entry.delete(0, tk.END)
        self.load_tasks()
