import pytest
from datetime import datetime, timedelta
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.task import Task
from models.project import Project
from models.user import User

class TestTask:
    """Тесты для класса Task"""
    
    def test_task_creation(self):
        """Тест создания задачи"""
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=1,
            due_date=datetime.now() + timedelta(days=1),
            project_id=1,
            assignee_id=1
        )
        
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.priority == 1
        assert task.status == "pending"
        assert task.project_id == 1
        assert task.assignee_id == 1
        assert task.id is None
        assert isinstance(task.created_at, datetime)
    
    def test_task_creation_with_string_date(self):
        """Тест создания задачи со строковой датой"""
        due_date_str = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=2,
            due_date=due_date_str,
            project_id=1,
            assignee_id=1
        )
        
        assert isinstance(task.due_date, datetime)
        assert task.priority == 2
    
    def test_update_status_valid(self):
        """Тест обновления статуса с валидными значениями"""
        task = Task("Test", "Desc", 1, datetime.now(), 1, 1)
        
        assert task.update_status("in_progress") == True
        assert task.status == "in_progress"
        
        assert task.update_status("completed") == True
        assert task.status == "completed"
        
        assert task.update_status("pending") == True
        assert task.status == "pending"
    
    def test_update_status_invalid(self):
        """Тест обновления статуса с невалидными значениями"""
        task = Task("Test", "Desc", 1, datetime.now(), 1, 1)
        
        assert task.update_status("invalid_status") == False
        assert task.status == "pending"  # Статус не должен измениться
        
        assert task.update_status("") == False
        assert task.update_status(None) == False
    
    def test_is_overdue(self):
        """Тест проверки просрочки задачи"""
        # Просроченная задача
        past_date = datetime.now() - timedelta(days=1)
        task1 = Task("Overdue", "Desc", 1, past_date, 1, 1)
        task1.status = "pending"
        assert task1.is_overdue() == True
        
        # Не просроченная задача
        future_date = datetime.now() + timedelta(days=1)
        task2 = Task("Not Overdue", "Desc", 1, future_date, 1, 1)
        task2.status = "pending"
        assert task2.is_overdue() == False
        
        # Завершенная задача не считается просроченной
        task3 = Task("Completed", "Desc", 1, past_date, 1, 1)
        task3.status = "completed"
        assert task3.is_overdue() == False
    
    def test_to_dict(self):
        """Тест преобразования задачи в словарь"""
        due_date = datetime.now() + timedelta(days=1)
        task = Task("Test", "Desc", 3, due_date, 2, 3)
        task.id = 1
        task.status = "in_progress"
        
        task_dict = task.to_dict()
        
        assert task_dict['id'] == 1
        assert task_dict['title'] == "Test"
        assert task_dict['description'] == "Desc"
        assert task_dict['priority'] == 3
        assert task_dict['status'] == "in_progress"
        assert task_dict['project_id'] == 2
        assert task_dict['assignee_id'] == 3
        assert 'due_date' in task_dict
        assert 'created_at' in task_dict
    
    def test_from_dict(self):
        """Тест создания задачи из словаря"""
        data = {
            'id': 5,
            'title': 'From Dict',
            'description': 'Description',
            'priority': 2,
            'status': 'completed',
            'due_date': '2024-01-01 12:00:00',
            'project_id': 3,
            'assignee_id': 4,
            'created_at': '2023-12-01 10:00:00'
        }
        
        task = Task.from_dict(data)
        
        assert task.id == 5
        assert task.title == "From Dict"
        assert task.status == "completed"
        assert task.project_id == 3
        assert task.assignee_id == 4
        assert isinstance(task.due_date, datetime)
        assert isinstance(task.created_at, datetime)
    
    def test_priority_validation(self):
        """Тест на некорректный приоритет (должен обрабатываться в контроллере)"""
        # Это тест проверяет, что задача принимает любой приоритет
        # Валидация должна быть в контроллере
        task = Task("Test", "Desc", 999, datetime.now(), 1, 1)
        assert task.priority == 999

class TestProject:
    """Тесты для класса Project"""
    
    def test_project_creation(self):
        """Тест создания проекта"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=start_date,
            end_date=end_date
        )
        
        assert project.name == "Test Project"
        assert project.description == "Test Description"
        assert project.status == "active"
        assert project.id is None
        assert isinstance(project.start_date, datetime)
        assert isinstance(project.end_date, datetime)
        assert isinstance(project.created_at, datetime)
    
    def test_project_creation_with_string_dates(self):
        """Тест создания проекта со строковыми датами"""
        start_str = "2024-01-01"
        end_str = "2024-01-31"
        
        project = Project(
            name="Test Project",
            description="Test Description",
            start_date=start_str,
            end_date=end_str
        )
        
        assert isinstance(project.start_date, datetime)
        assert isinstance(project.end_date, datetime)
        assert project.start_date.strftime('%Y-%m-%d') == start_str
        assert project.end_date.strftime('%Y-%m-%d') == end_str
    
    def test_update_status(self):
        """Тест обновления статуса проекта"""
        project = Project("Test", "Desc", datetime.now(), datetime.now())
        
        assert project.update_status("completed") == True
        assert project.status == "completed"
        
        assert project.update_status("on_hold") == True
        assert project.status == "on_hold"
        
        assert project.update_status("active") == True
        assert project.status == "active"
        
        assert project.update_status("invalid") == False
        assert project.status == "active"  # Не должен измениться
    
    def test_get_progress(self):
        """Тест получения прогресса проекта"""
        project = Project("Test", "Desc", datetime.now(), datetime.now())
        
        # Метод должен возвращать число
        progress = project.get_progress()
        assert isinstance(progress, (int, float))
        assert 0 <= progress <= 100
    
    def test_to_dict(self):
        """Тест преобразования проекта в словарь"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        project = Project("Test", "Desc", start_date, end_date)
        project.id = 1
        project.status = "active"
        
        project_dict = project.to_dict()
        
        assert project_dict['id'] == 1
        assert project_dict['name'] == "Test"
        assert project_dict['description'] == "Desc"
        assert project_dict['status'] == "active"
        assert 'start_date' in project_dict
        assert 'end_date' in project_dict
        assert 'created_at' in project_dict
    
    def test_from_dict(self):
        """Тест создания проекта из словаря"""
        data = {
            'id': 10,
            'name': 'From Dict Project',
            'description': 'Project Description',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'status': 'on_hold',
            'created_at': '2023-12-01 10:00:00'
        }
        
        project = Project.from_dict(data)
        
        assert project.id == 10
        assert project.name == "From Dict Project"
        assert project.description == "Project Description"
        assert project.status == "on_hold"
        assert isinstance(project.start_date, datetime)
        assert isinstance(project.end_date, datetime)
        assert isinstance(project.created_at, datetime)

class TestUser:
    """Тесты для класса User"""
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        user = User(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "developer"
        assert user.id is None
        assert isinstance(user.registration_date, datetime)
    
    def test_update_info(self):
        """Тест обновления информации пользователя"""
        user = User("olduser", "old@example.com", "developer")
        
        # Обновление имени
        user.update_info(username="newuser")
        assert user.username == "newuser"
        assert user.email == "old@example.com"
        assert user.role == "developer"
        
        # Обновление email
        user.update_info(email="new@example.com")
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.role == "developer"
        
        # Обновление роли
        user.update_info(role="manager")
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.role == "manager"
        
        # Обновление всех полей
        user.update_info(username="admin", email="admin@example.com", role="admin")
        assert user.username == "admin"
        assert user.email == "admin@example.com"
        assert user.role == "admin"
    
    def test_update_info_invalid_role(self):
        """Тест обновления с невалидной ролью"""
        user = User("test", "test@example.com", "developer")
        
        # Невалидная роль не должна обновляться
        user.update_info(role="invalid_role")
        assert user.role == "developer"  # Не изменилась
        
        user.update_info(role="admin")
        assert user.role == "admin"  # Валидная роль изменилась
    
    def test_update_info_partial(self):
        """Тест частичного обновления информации"""
        user = User("test", "test@example.com", "developer")
        
        # Обновление только одного поля
        user.update_info(username="updated")
        assert user.username == "updated"
        assert user.email == "test@example.com"
        assert user.role == "developer"
        
        user.update_info(email="updated@example.com")
        assert user.username == "updated"
        assert user.email == "updated@example.com"
        assert user.role == "developer"
    
    def test_to_dict(self):
        """Тест преобразования пользователя в словарь"""
        user = User("testuser", "test@example.com", "admin")
        user.id = 1
        
        user_dict = user.to_dict()
        
        assert user_dict['id'] == 1
        assert user_dict['username'] == "testuser"
        assert user_dict['email'] == "test@example.com"
        assert user_dict['role'] == "admin"
        assert 'registration_date' in user_dict
    
    def test_from_dict(self):
        """Тест создания пользователя из словаря"""
        data = {
            'id': 20,
            'username': 'dictuser',
            'email': 'dict@example.com',
            'role': 'manager',
            'registration_date': '2023-11-01 09:00:00'
        }
        
        user = User.from_dict(data)
        
        assert user.id == 20
        assert user.username == "dictuser"
        assert user.email == "dict@example.com"
        assert user.role == "manager"
        assert isinstance(user.registration_date, datetime)
    
    def test_roles_validation(self):
        """Тест валидации ролей"""
        # Создание с валидными ролями
        user1 = User("admin", "admin@example.com", "admin")
        user2 = User("manager", "manager@example.com", "manager")
        user3 = User("dev", "dev@example.com", "developer")
        
        assert user1.role == "admin"
        assert user2.role == "manager"
        assert user3.role == "developer"
        
        # Роль сохраняется как есть, валидация в контроллере
        user4 = User("invalid", "invalid@example.com", "invalid_role")
        assert user4.role == "invalid_role"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
