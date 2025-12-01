import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabaseManager:
    def __init__(self, db_path: str = 'tasks.db'):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Установить соединение с базой данных"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Для доступа к столбцам по имени
        self.cursor = self.connection.cursor()
    
    def close(self):
        """Закрыть соединение с базой данных"""
        if self.connection:
            self.connection.close()
    
    def create_tables(self):
        """Создать все необходимые таблицы"""
        self.create_user_table()
        self.create_project_table()
        self.create_task_table()
    
    # ========== Методы для работы с пользователями ==========
    
    def create_user_table(self):
        """Создать таблицу пользователей"""
        query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'developer')),
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        self.cursor.execute(query)
        self.connection.commit()
    
    def add_user(self, user) -> int:
        """Добавить пользователя"""
        query = '''
        INSERT INTO users (username, email, role, registration_date)
        VALUES (?, ?, ?, ?)
        '''
        self.cursor.execute(query, (
            user.username,
            user.email,
            user.role,
            user.registration_date.strftime('%Y-%m-%d %H:%M:%S')
        ))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Получить пользователя по ID"""
        query = 'SELECT * FROM users WHERE id = ?'
        self.cursor.execute(query, (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_users(self) -> List[Dict]:
        """Получить всех пользователей"""
        query = 'SELECT * FROM users ORDER BY id'
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Обновить пользователя"""
        if not kwargs:
            return False
        
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['username', 'email', 'role']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        values.append(user_id)
        query = f'UPDATE users SET {", ".join(fields)} WHERE id = ?'
        self.cursor.execute(query, values)
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        query = 'DELETE FROM users WHERE id = ?'
        self.cursor.execute(query, (user_id,))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    # ========== Методы для работы с проектами ==========
    
    def create_project_table(self):
        """Создать таблицу проектов"""
        query = '''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'on_hold')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        self.cursor.execute(query)
        self.connection.commit()
    
    def add_project(self, project) -> int:
        """Добавить проект"""
        query = '''
        INSERT INTO projects (name, description, start_date, end_date, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(query, (
            project.name,
            project.description,
            project.start_date.strftime('%Y-%m-%d'),
            project.end_date.strftime('%Y-%m-%d'),
            project.status,
            project.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_project_by_id(self, project_id: int) -> Optional[Dict]:
        """Получить проект по ID"""
        query = 'SELECT * FROM projects WHERE id = ?'
        self.cursor.execute(query, (project_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_projects(self) -> List[Dict]:
        """Получить все проекты"""
        query = 'SELECT * FROM projects ORDER BY id'
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_project(self, project_id: int, **kwargs) -> bool:
        """Обновить проект"""
        if not kwargs:
            return False
        
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['name', 'description', 'start_date', 'end_date', 'status']:
                if key in ['start_date', 'end_date'] and hasattr(value, 'strftime'):
                    value = value.strftime('%Y-%m-%d')
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        values.append(project_id)
        query = f'UPDATE projects SET {", ".join(fields)} WHERE id = ?'
        self.cursor.execute(query, values)
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def delete_project(self, project_id: int) -> bool:
        """Удалить проект"""
        query = 'DELETE FROM projects WHERE id = ?'
        self.cursor.execute(query, (project_id,))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    # ========== Методы для работы с задачами ==========
    
    def create_task_table(self):
        """Создать таблицу задач"""
        query = '''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority INTEGER NOT NULL CHECK(priority IN (1, 2, 3)),
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed')),
            due_date TIMESTAMP NOT NULL,
            project_id INTEGER,
            assignee_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
            FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL
        )
        '''
        self.cursor.execute(query)
        self.connection.commit()
    
    def add_task(self, task) -> int:
        """Добавить задачу"""
        query = '''
        INSERT INTO tasks (title, description, priority, status, due_date, project_id, assignee_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(query, (
            task.title,
            task.description,
            task.priority,
            task.status,
            task.due_date.strftime('%Y-%m-%d %H:%M:%S'),
            task.project_id,
            task.assignee_id,
            task.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        """Получить задачу по ID"""
        query = 'SELECT * FROM tasks WHERE id = ?'
        self.cursor.execute(query, (task_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_tasks(self) -> List[Dict]:
        """Получить все задачи"""
        query = 'SELECT * FROM tasks ORDER BY due_date, priority'
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Обновить задачу"""
        if not kwargs:
            return False
        
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['title', 'description', 'priority', 'status', 'due_date', 'project_id', 'assignee_id']:
                if key == 'due_date' and hasattr(value, 'strftime'):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        values.append(task_id)
        query = f'UPDATE tasks SET {", ".join(fields)} WHERE id = ?'
        self.cursor.execute(query, values)
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def delete_task(self, task_id: int) -> bool:
        """Удалить задачу"""
        query = 'DELETE FROM tasks WHERE id = ?'
        self.cursor.execute(query, (task_id,))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def search_tasks(self, query_str: str) -> List[Dict]:
        """Поиск задач по названию/описанию"""
        query = '''
        SELECT * FROM tasks 
        WHERE title LIKE ? OR description LIKE ?
        ORDER BY due_date, priority
        '''
        search_term = f'%{query_str}%'
        self.cursor.execute(query, (search_term, search_term))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_tasks_by_project(self, project_id: int) -> List[Dict]:
        """Получить задачи проекта"""
        query = 'SELECT * FROM tasks WHERE project_id = ? ORDER BY due_date, priority'
        self.cursor.execute(query, (project_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_tasks_by_user(self, user_id: int) -> List[Dict]:
        """Получить задачи пользователя"""
        query = 'SELECT * FROM tasks WHERE assignee_id = ? ORDER BY due_date, priority'
        self.cursor.execute(query, (user_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_overdue_tasks(self) -> List[Dict]:
        """Получить просроченные задачи"""
        query = '''
        SELECT * FROM tasks 
        WHERE due_date < datetime('now') 
        AND status != 'completed'
        ORDER BY due_date, priority
        '''
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_project_progress(self, project_id: int) -> Dict[str, Any]:
        """Получить прогресс проекта"""
        query = '''
        SELECT 
            COUNT(*) as total_tasks,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks
        FROM tasks 
        WHERE project_id = ?
        '''
        self.cursor.execute(query, (project_id,))
        row = self.cursor.fetchone()
        
        if row and row['total_tasks'] > 0:
            progress = (row['completed_tasks'] / row['total_tasks']) * 100
        else:
            progress = 0
        
        return {
            'total_tasks': row['total_tasks'] if row else 0,
            'completed_tasks': row['completed_tasks'] if row else 0,
            'progress': progress
        }
