from typing import List, Dict, Any, Optional
from models.user import User
from database.database_manager import DatabaseManager

class UserController:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def add_user(self, username: str, email: str, role: str) -> Optional[User]:
        """Добавить пользователя"""
        try:
            # Валидация роли
            if role not in ['admin', 'manager', 'developer']:
                raise ValueError("Role must be 'admin', 'manager', or 'developer'")
            
            # Создаем объект пользователя
            user = User(
                username=username,
                email=email,
                role=role
            )
            
            # Добавляем в базу данных
            user_id = self.db_manager.add_user(user)
            user.id = user_id
            
            return user
            
        except Exception as e:
            print(f"Error adding user: {e}")
            return None
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Получить пользователя"""
        try:
            user_data = self.db_manager.get_user_by_id(user_id)
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_all_users(self) -> List[User]:
        """Получить всех пользователей"""
        try:
            users_data = self.db_manager.get_all_users()
            return [User.from_dict(data) for data in users_data]
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Обновить пользователя"""
        try:
            # Проверяем существование пользователя
            user = self.get_user(user_id)
            if not user:
                return False
            
            # Валидация данных
            if 'role' in kwargs and kwargs['role'] not in ['admin', 'manager', 'developer']:
                raise ValueError("Invalid role")
            
            # Обновляем в объекте
            user.update_info(
                username=kwargs.get('username'),
                email=kwargs.get('email'),
                role=kwargs.get('role')
            )
            
            # Обновляем в базе данных
            return self.db_manager.update_user(user_id, **kwargs)
            
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        try:
            return self.db_manager.delete_user(user_id)
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def get_user_tasks(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить задачи пользователя"""
        try:
            # Получаем пользователя
            user = self.get_user(user_id)
            if not user:
                return []
            
            # Получаем задачи пользователя
            from controllers.task_controller import TaskController
            task_controller = TaskController(self.db_manager)
            tasks = task_controller.get_tasks_by_user(user_id)
            
            # Формируем результат
            result = []
            for task in tasks:
                task_dict = task.to_dict()
                
                # Получаем информацию о проекте
                project_data = self.db_manager.get_project_by_id(task.project_id)
                if project_data:
                    task_dict['project_name'] = project_data['name']
                
                result.append(task_dict)
            
            return result
            
        except Exception as e:
            print(f"Error getting user tasks: {e}")
            return []
