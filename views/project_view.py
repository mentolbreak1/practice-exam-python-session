import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

class ProjectView:
    def __init__(self, parent, project_controller, task_controller):
        self.project_controller = project_controller
        self.task_controller = task_controller
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_projects()
        
    def setup_ui(self):
        """Настройка интерфейса проектов"""
        # Панель управления
        control_frame = ttk.LabelFrame(self.frame, text="Управление проектами", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Кнопки управления
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="Добавить проект", command=self.show_add_project_dialog).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit_project).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_project).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить список", command=self.load_projects).pack(side='left', padx=5)
        
        # Статистика
        stats_frame = ttk.Frame(control_frame)
        stats_frame.pack(fill='x', pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="Всего проектов: 0 | Активных: 0 | Завершенных: 0")
        self.stats_label.pack()
        
        # Таблица проектов
        table_frame = ttk.LabelFrame(self.frame, text="Список проектов", padding=10)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('ID', 'Название', 'Статус', 'Начало', 'Окончание', 'Прогресс', 'Задач')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column('Название', width=200)
        self.tree.column('ID', width=50)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def load_projects(self):
        """Загрузка проектов в таблицу"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Загружаем проекты
        projects = self.project_controller.get_all_projects()
        
        active_count = 0
        completed_count = 0
        
        for project in projects:
            # Получаем статистику проекта
            progress_data = self.project_controller.get_project_progress(project.id)
            progress = progress_data['progress']
            task_count = progress_data['total_tasks']
            
            # Подсчитываем статусы
            if project.status == 'active':
                active_count += 1
            elif project.status == 'completed':
                completed_count += 1
            
            # Добавляем в таблицу
            self.tree.insert('', 'end', values=(
                project.id,
                project.name,
                self.get_status_text(project.status),
                project.start_date.strftime('%d.%m.%Y'),
                project.end_date.strftime('%d.%m.%Y'),
                f"{progress:.1f}%",
                task_count
            ))
        
        # Обновляем статистику
        self.stats_label.config(text=f"Всего проектов: {len(projects)} | Активных: {active_count} | Завершенных: {completed_count}")
    
    def get_status_text(self, status):
        """Получить текстовое описание статуса"""
        statuses = {
            'active': 'Активный',
            'completed': 'Завершен',
            'on_hold': 'На паузе'
        }
        return statuses.get(status, 'Неизвестно')
    
    def show_add_project_dialog(self):
        """Показать диалог добавления проекта"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Добавить проект")
        dialog.geometry("500x450")
        dialog.resizable(False, False)
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Заголовок
        ttk.Label(dialog, text="Добавить новый проект", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Форма
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # Название
        ttk.Label(form_frame, text="Название:*").grid(row=0, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.grid(row=0, column=1, pady=5, padx=10)
        
        # Описание
        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, sticky='w', pady=5)
        description_text = tk.Text(form_frame, width=30, height=5)
        description_text.grid(row=1, column=1, pady=5, padx=10)
        
        # Дата начала
        ttk.Label(form_frame, text="Дата начала:*").grid(row=2, column=0, sticky='w', pady=5)
        start_date_entry = DateEntry(form_frame, width=20, date_pattern='yyyy-mm-dd')
        start_date_entry.grid(row=2, column=1, pady=5, padx=10)
        
        # Дата окончания
        ttk.Label(form_frame, text="Дата окончания:*").grid(row=3, column=0, sticky='w', pady=5)
        end_date_entry = DateEntry(form_frame, width=20, date_pattern='yyyy-mm-dd')
        end_date_entry.grid(row=3, column=1, pady=5, padx=10)
        
        # Статус
        ttk.Label(form_frame, text="Статус:*").grid(row=4, column=0, sticky='w', pady=5)
        status_var = tk.StringVar(value="active")
        status_combo = ttk.Combobox(form_frame, textvariable=status_var, 
                                    values=['active', 'on_hold'], 
                                    state='readonly', width=20)
        status_combo.grid(row=4, column=1, pady=5, padx=10)
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_project():
            """Сохранение проекта"""
            name = name_entry.get().strip()
            description = description_text.get("1.0", tk.END).strip()
            start_date = start_date_entry.get_date()
            end_date = end_date_entry.get_date()
            status = status_var.get()
            
            # Валидация
            if not name:
                messagebox.showerror("Ошибка", "Название проекта обязательно!")
                return
            
            if start_date >= end_date:
                messagebox.showerror("Ошибка", "Дата начала должна быть раньше даты окончания!")
                return
            
            # Создаем проект
            project = self.project_controller.add_project(
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date
            )
            
            if project:
                # Обновляем статус, если нужно
                if status != 'active':
                    self.project_controller.update_project_status(project.id, status)
                
                messagebox.showinfo("Успех", "Проект успешно добавлен!")
                self.load_projects()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить проект!")
        
        ttk.Button(button_frame, text="Сохранить", command=save_project).pack(side='left', padx=10)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side='left', padx=10)
    
    def edit_project(self):
        """Редактирование выбранного проекта"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите проект для редактирования!")
            return
        
        item = self.tree.item(selected[0])
        project_id = item['values'][0]
        
        # Получаем проект
        project = self.project_controller.get_project(project_id)
        if not project:
            messagebox.showerror("Ошибка", "Проект не найдена!")
            return
        
        # Создаем диалог редактирования
        dialog = tk.Toplevel(self.frame)
        dialog.title("Редактировать проект")
        dialog.geometry("500x500")
        dialog.resizable(False, False)
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Заголовок
        ttk.Label(dialog, text=f"Редактирование проекта #{project_id}", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Форма
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # Название
        ttk.Label(form_frame, text="Название:*").grid(row=0, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.insert(0, project.name)
        name_entry.grid(row=0, column=1, pady=5, padx=10)
        
        # Описание
        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, sticky='w', pady=5)
        description_text = tk.Text(form_frame, width=30, height=5)
        description_text.insert("1.0", project.description)
        description_text.grid(row=1, column=1, pady=5, padx=10)
        
        # Дата начала
        ttk.Label(form_frame, text="Дата начала:*").grid(row=2, column=0, sticky='w', pady=5)
        start_date_entry = DateEntry(form_frame, width=20, date_pattern='yyyy-mm-dd')
        start_date_entry.set_date(project.start_date)
        start_date_entry.grid(row=2, column=1, pady=5, padx=10)
        
        # Дата окончания
        ttk.Label(form_frame, text="Дата окончания:*").grid(row=3, column=0, sticky='w', pady=5)
        end_date_entry = DateEntry(form_frame, width=20, date_pattern='yyyy-mm-dd')
        end_date_entry.set_date(project.end_date)
        end_date_entry.grid(row=3, column=1, pady=5, padx=10)
        
        # Статус
        ttk.Label(form_frame, text="Статус:*").grid(row=4, column=0, sticky='w', pady=5)
        status_var = tk.StringVar(value=project.status)
        status_combo = ttk.Combobox(form_frame, textvariable=status_var, 
                                    values=['active', 'completed', 'on_hold'], 
                                    state='readonly', width=20)
        status_combo.grid(row=4, column=1, pady=5, padx=10)
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_changes():
            """Сохранение изменений"""
            name = name_entry.get().strip()
            description = description_text.get("1.0", tk.END).strip()
            start_date = start_date_entry.get_date()
            end_date = end_date_entry.get_date()
            status = status_var.get()
            
            # Валидация
            if not name:
                messagebox.showerror("Ошибка", "Название проекта обязательно!")
                return
            
            if start_date >= end_date:
                messagebox.showerror("Ошибка", "Дата начала должна быть раньше даты окончания!")
                return
            
            # Обновляем проект
            success = self.project_controller.update_project(
                project_id=project_id,
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                status=status
            )
            
            if success:
                messagebox.showinfo("Успех", "Проект успешно обновлен!")
                self.load_projects()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить проект!")
        
        ttk.Button(button_frame, text="Сохранить", command=save_changes).pack(side='left', padx=10)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side='left', padx=10)
    
    def delete_project(self):
        """Удаление выбранного проекта"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите проект для удаления!")
            return
        
        item = self.tree.item(selected[0])
        project_id = item['values'][0]
        project_name = item['values'][1]
        
        # Проверяем, есть ли задачи в проекте
        tasks = self.task_controller.get_tasks_by_project(project_id)
        if tasks:
            if not messagebox.askyesno("Подтверждение", 
                                      f"В проекте '{project_name}' есть {len(tasks)} задач. "
                                      f"Они также будут удалены. Продолжить?"):
                return
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", 
                              f"Вы уверены, что хотите удалить проект '{project_name}'?"):
            success = self.project_controller.delete_project(project_id)
            if success:
                messagebox.showinfo("Успех", "Проект успешно удален!")
                self.load_projects()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить проект!")
