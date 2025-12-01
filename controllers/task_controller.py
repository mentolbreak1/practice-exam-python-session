from datetime import datetime
from typing import List, Dict, Any, Optional
from models.task import Task
from database.database_manager import DatabaseManager

class TaskController:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def add_task(self, title: str, description: str, priority: int, due_date, 
                 project_id: int, assignee_id: int) -> Optional[Task]:
        """Добавить задачу"""
        try:
            # Валидация приоритета
            if priority not in [1, 2, 3]:
                raise ValueError("Priority must be 1, 2, or 3")
            
            # Создаем объект задачи
            task = Task(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                project_id=project_id,
                assignee_id=assignee_id
            )
            
            # Добавляем в базу данных
            task_id = self.db_manager.add_task(task)
            task.id = task_id
            
            return task
            
        except Exception as e:
            print(f"Error adding task: {e}")
            return None
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Получить задачу"""
        try:
            task_data = self.db_manager.get_task_by_id(task_id)
            if task_data:
                return Task.from_dict(task_data)
            return None
        except Exception as e:
            print(f"Error getting task: {e}")
            return None
    
    def get_all_tasks(self) -> List[Task]:
        """Получить все задачи"""
        try:
            tasks_data = self.db_manager.get_all_tasks()
            return [Task.from_dict(data) for data in tasks_data]
        except Exception as e:
            print(f"Error getting all tasks: {e}")
            return []
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Обновить задачу"""
        try:
            # Проверяем существование задачи
            task = self.get_task(task_id)
            if not task:
                return False
            
            # Валидация данных
            if 'priority' in kwargs and kwargs['priority'] not in [1, 2, 3]:
                raise ValueError("Priority must be 1, 2, or 3")
            
            if 'status' in kwargs and kwargs['status'] not in ['pending', 'in_progress', 'completed']:
                raise ValueError("Invalid status")
            
            # Обновляем в базе данных
            return self.db_manager.update_task(task_id, **kwargs)
            
        except Exception as e:
            print(f"Error updating task: {e}")
            return False
    
    def delete_task(self, task_id: int) -> bool:
        """Удалить задачу"""
        try:
            return self.db_manager.delete_task(task_id)
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    
    def search_tasks(self, query: str) -> List[Task]:
        """Поиск задач"""
        try:
            tasks_data = self.db_manager.search_tasks(query)
            return [Task.from_dict(data) for data in tasks_data]
        except Exception as e:
            print(f"Error searching tasks: {e}")
            return []
    
    def update_task_status(self, task_id: int, new_status: str) -> bool:
        """Обновить статус задачи"""
        try:
            # Получаем задачу
            task = self.get_task(task_id)
            if not task:
                return False
            
            # Обновляем статус в объекте
            if task.update_status(new_status):
                # Обновляем в базе данных
                return self.db_manager.update_task(task_id, status=new_status)
            return False
            
        except Exception as e:
            print(f"Error updating task status: {e}")
            return False
    
    def get_overdue_tasks(self) -> List[Task]:
        """Получить просроченные задачи"""
        try:
            tasks_data = self.db_manager.get_overdue_tasks()
            return [Task.from_dict(data) for data in tasks_data]
        except Exception as e:
            print(f"Error getting overdue tasks: {e}")
            return []
    
    def get_tasks_by_project(self, project_id: int) -> List[Task]:
        """Получить задачи проекта"""
        try:
            tasks_data = self.db_manager.get_tasks_by_project(project_id)
            return [Task.from_dict(data) for data in tasks_data]
        except Exception as e:
            print(f"Error getting tasks by project: {e}")
            return []
    
    def get_tasks_by_user(self, user_id: int) -> List[Task]:
        """Получить задачи пользователя"""
        try:
            tasks_data = self.db_manager.get_tasks_by_user(user_id)
            return [Task.from_dict(data) for data in tasks_data]
        except Exception as e:
            print(f"Error getting tasks by user: {e}")
            return []
