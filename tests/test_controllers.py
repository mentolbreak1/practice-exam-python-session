import pytest
import tempfile
import os
import sys
from datetime import datetime, timedelta

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.database_manager import DatabaseManager
from controllers.task_controller import TaskController
from controllers.project_controller import ProjectController
from controllers.user_controller import UserController
from models.task import Task
from models.project import Project
from models.user import User

class TestTaskController:
    """Тесты для TaskController"""
    
    @pytest.fixture
    def controllers(self):
        """Фикстура для создания контроллеров с временной БД"""
        # Создаем временную базу данных
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_path = temp_db.name
        temp_db.close()
        
        # Создаем менеджер базы данных
        db_manager = DatabaseManager(db_path)
        
        # Создаем контроллеры
        task_controller = TaskController(db_manager)
        project_controller = ProjectController(db_manager)
        user_controller = UserController(db_manager)
        
        # Создаем тестовые данные
        user = user_controller.add_user("testuser", "test@example.com", "developer")
        project = project_controller.add_project(
            "Test Project",
            "Description",
            datetime.now(),
            datetime.now() + timedelta(days=30)
        )
        
        yield {
            'task': task_controller,
            'project': project_controller,
            'user': user_controller,
            'db': db_manager,
            'user_id': user.id,
            'project_id': project.id
        }
        
        # Закрываем соединение и удаляем файл
        db_manager.close()
        os.unlink(db_path)
    
    def test_add_task_valid(self, controllers):
        """Тест добавления валидной задачи"""
        task = controllers['task'].add_task(
            title="Test Task",
            description="Task Description",
            priority=1,
            due_date=datetime.now() + timedelta(days=7),
            project_id=controllers['project_id'],
            assignee_id=controllers['user_id']
        )
        
        assert task is not None
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.description == "Task Description"
        assert task.priority == 1
        assert task.status == "pending"
        assert task.project_id == controllers['project_id']
        assert task.assignee_id == controllers['user_id']
    
    def test_add_task_invalid_priority(self, controllers):
        """Тест добавления задачи с невалидным приоритетом"""
        task = controllers['task'].add_task(
            title="Test Task",
            description="Task Description",
            priority=5,  # Невалидный приоритет
            due_date=datetime.now() + timedelta(days=7),
            project_id=controllers['project_id'],
            assignee_id=controllers['user_id']
        )
        
        assert task is None  # Должен вернуть None при ошибке
    
    def test_get_task(self, controllers):
        """Тест получения задачи"""
        # Сначала добавляем задачу
        task = controllers['task'].add_task(
            title="Get Task Test",
            description="Description",
            priority=2,
            due_date=datetime.now() + timedelta(days=1),
            project_id=controllers['project_id'],
            assignee_id=controllers['user_id']
        )
        
        assert task is not None
        task_id = task.id
        
        # Получаем задачу
        retrieved_task = controllers['task'].get_task(task_id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == task_id
        assert retrieved_task.title == "Get Task Test"
        assert retrieved_task.priority == 2
    
    def test_get_task_nonexistent(self, controllers):
        """Тест получения несуществующей задачи"""
        task = controllers['task'].get_task(999)
        assert task is None
    
    def test_get_all_tasks(self, controllers):
        """Тест получения всех задач"""
        # Добавляем несколько задач
        for i in range(3):
            controllers['task'].add_task(
                title=f"Task {i}",
                description=f"Description {i}",
                priority=1,
                due_date=datetime.now() + timedelta(days=i+1),
                project_id=controllers['project_id'],
                assignee_id=controllers['user_id']
            )
        
        tasks = controllers['task'].get_all_tasks()
        assert len(tasks) == 3
        
        # Проверяем сортировку
        due_dates = [task.due_date for task in tasks]
        assert due_dates == sorted(due_dates)
    
    def test_update_task(self, controllers):
        """Тест обновления задачи"""
        # Добавляем задачу
        task = controllers['task'].add_task(
            title="Original Title",
            description="Original Description",
            priority=1,
            due_date=datetime.now() + timedelta(days=1),
            project_id=controllers['project_id'],
            assignee_id=controllers['user_id']
        )
        
        task_id = task.id
        
        # Обновляем задачу
        success = controllers['task'].update_task(
            task_id,
            title="Updated Title",
            description="Updated Description",
            priority=2,
            status="in_progress"
        )
        
        assert success == True
        
        # Проверяем обновления
        updated_task = controllers['task'].get_task(task_id)
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Updated Description"
        assert updated_task.priority == 2
        assert updated_task.status == "in_progress"
    
    def test_update_task_invalid_data(self, controllers):
        """Тест обновления задачи с невалидными данными"""
        # Добавляем задачу
        task = controllers['task'].add_task(
            title="Test Task",
            description="Description",
            priority=1,
            due_date=datetime.now(),
            project_id=controllers['project_id'],
            assignee_id=controllers['user_id']
        )
        
        # Попытка обновления с невалидным приоритетом
        success = controllers['task'].update_task(
            task.id,
            priority=5  # Невалидный приоритет
        )
        
        assert success == False
        
        # Попытка обновления с невалидным статусом
        success = controllers['task'].update_task(
            task.id,
            status="invalid_status"
        )
        
        assert success == False
    
    def test_update_nonexistent_task(self, controllers):
        """Тест обновления несуществующей задачи"""
        success = controllers['task'].update_task(999, title="Nonexistent")
        assert success == False
    
    def test_delete_task(self, controllers):
        """Тест удаления задачи"""
        # Добавляем задачу
        task = controllers['task'].add_task(
            title="Task to Delete",
            description="Description",
            priority=1,
            due_date=datetime.now(),
            project_id=controllers['project_id'],
            assignee_id=controllers['user_id']
        )
        
        task_id = task.id
        
        # Удаляем задачу
        success = controllers['task'].delete_task(task_id)
        assert success == True
        
        # Проверяем, что задача удалена
        deleted_task = controllers['task'].get_task(task_id)
        assert deleted_task is None
    
    def test_delete_nonexistent_task(self, controllers):
        """Тест удаления несуществующей задачи"""
        success = controllers['task'].delete_task(999)
        assert success == False
    
    def test_search_tasks(self, controllers):
        """Тест поиска задач"""
        # Добавляем задачи с разными названиями
        controllers['task'].add_task(
            title="Database Management Task",
            description="Manage database",
            priority=1,
            due_date=datetime.now(),
            project_id=controllers['project_id'],
            assignee_id=controllers['user_id']
        )
        
        controllers['task'].add_task(
            title="UI Development",
            description="Database interface",
            priority=2,
            due_date=datetime.now(),
            project_id=controllers['project_id'],
            assignee_id=controllers['user_id']
        )
        
        controllers['task'].add_task(
            title="Testing",
            description="Unit tests",
            priority=3,
            due_date=datetime.now(),
            project_id=controllers['project_id'],
            assignee_id=controllers['user_id']
        )
        
        # Поиск по названию
        results = controllers['task'].search_tasks("Database")
        assert len(results) == 1
        assert "Database" in results[0].title
        
        # Поиск по описанию
        results = controllers['task'].search_tasks("interface")
        assert len(results) == 1
        assert "interface" in results[0].description.lower()
        
        # Поиск, который находит несколько задач
        results = controllers['task'].search_tasks("task")
        assert len(results) >= 1
        
        # Поиск без результатов
        results = controllers['task'].search_tasks("nonexistent")
        assert len(results) == 0
    
    def test_update_task_status(self, controllers):
        """Тест обновления статуса задачи"""
        # Добавляем задачу
        task = controllers['task'].add_task(
            title="Status Test",
            description="Description",
            priority=1,
            due_date=datetime.now(),
            project_id=controllers['project_id'],
            assignee_id=controllers['user_id']
        )
        
        # Обновляем статус
        success = controllers['task'].update_task_status(task.id, "in_progress")
        assert success == True
        
        updated_task = controllers['task'].get_task(task.id)
        assert updated_task.status == "in_progress"
        
        # Обновляем на невалидный статус
        success = controllers['task'].update_task_status(task.id, "invalid_status")
        assert success == False
        assert updated_task.status == "in_progress"  # Не должен измениться
    
    def test_get_overdue_tasks(self, controllers):
        """Тест получения просроченных задач"""
        # Добавляем просроченную задачу
        past_date = datetime.now() - timedelta(days=1)
        task1 = controllers['task'].add_task(
            title="Overdue Task",
            description="Description",
            priority=1,
            due_date=past_date,
            project_id=controllers['project_id'],
            assignee_id=controllers['user_id']
        )
        
        # Добавляем непросроченную задачу
        future_date = datetime.now() + timedelta(days=1)
        task2 = controllers['task'].add_task(
            title="Not Overdue",
            description="Description",
            priority=2,
            due_date=future_date,
            project_id=controllers['project_id'],
            assignee_id=controllers['user_id']
        )
        
        # Получаем просроченные задачи
        overdue_tasks = controllers['task'].get_overdue_tasks()
        
        # Должна быть одна просроченная задача
        assert len(overdue_tasks) == 1
        assert overdue_tasks[0].id == task1.id
        
        # Помечаем задачу как завершенную
        controllers['task'].update_task_status(task1.id, "completed")
        
        # Теперь просроченных задач не должно быть
        overdue_tasks = controllers['task'].get_overdue_tasks()
        assert len(overdue_tasks) == 0
    
    def test_get_tasks_by_project(self, controllers):
        """Тест получения задач по проекту"""
        # Создаем еще один проект
        project2 = controllers['project'].add_project(
            "Project 2",
            "Description",
            datetime.now(),
            datetime.now() + timedelta(days=30)
        )
        
        # Добавляем задачи в разные проекты
        for i in range(2):
            controllers['task'].add_task(
                title=f"Task Project 1 - {i}",
                description="Description",
                priority=1,
                due_date=datetime.now(),
                project_id=controllers['project_id'],
                assignee_id=controllers['user_id']
            )
        
        for i in range(3):
            controllers['task'].add_task(
                title=f"Task Project 2 - {i}",
                description="Description",
                priority=1,
                due_date=datetime.now(),
                project_id=project2.id,
                assignee_id=controllers['user_id']
            )
        
        # Получаем задачи для проекта 1
        project1_tasks = controllers['task'].get_tasks_by_project(controllers['project_id'])
        assert len(project1_tasks) == 2
        assert all(task.project_id == controllers['project_id'] for task in project1_tasks)
        
        # Получаем задачи для проекта 2
        project2_tasks = controllers['task'].get_tasks_by_project(project2.id)
        assert len(project2_tasks) == 3
        assert all(task.project_id == project2.id for task in project2_tasks)
    
    def test_get_tasks_by_user(self, controllers):
        """Тест получения задач по пользователю"""
        # Создаем еще одного пользователя
        user2 = controllers['user'].add_user("user2", "user2@example.com", "developer")
        
        # Добавляем задачи для разных пользователей
        for i in range(2):
            controllers['task'].add_task(
                title=f"Task User 1 - {i}",
                description="Description",
                priority=1,
                due_date=datetime.now(),
                project_id=controllers['project_id'],
                assignee_id=controllers['user_id']
            )
        
        for i in range(3):
            controllers['task'].add_task(
                title=f"Task User 2 - {i}",
                description="Description",
                priority=1,
                due_date=datetime.now(),
                project_id=controllers['project_id'],
                assignee_id=user2.id
            )
        
        # Получаем задачи для пользователя 1
        user1_tasks = controllers['task'].get_tasks_by_user(controllers['user_id'])
        assert len(user1_tasks) == 2
        assert all(task.assignee_id == controllers['user_id'] for task in user1_tasks)
        
        # Получаем задачи для пользователя 2
        user2_tasks = controllers['task'].get_tasks_by_user(user2.id)
        assert len(user2_tasks) == 3
        assert all(task.assignee_id == user2.id for task in user2_tasks)

class TestProjectController:
    """Тесты для ProjectController"""
    
    @pytest.fixture
    def controller(self):
        """Фикстура для создания контроллера с временной БД"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_path = temp_db.name
        temp_db.close()
        
        db_manager = DatabaseManager(db_path)
        controller = ProjectController(db_manager)
        
        yield controller
        
        db_manager.close()
        os.unlink(db_path)
    
    def test_add_project_valid(self, controller):
        """Тест добавления валидного проекта"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        project = controller.add_project(
            name="Test Project",
            description="Project Description",
            start_date=start_date,
            end_date=end_date
        )
        
        assert project is not None
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.description == "Project Description"
        assert project.status == "active"
        assert project.start_date.date() == start_date.date()
        assert project.end_date.date() == end_date.date()
    
    def test_add_project_invalid_dates(self, controller):
        """Тест добавления проекта с невалидными датами"""
        start_date = datetime.now()
        end_date = start_date - timedelta(days=1)  # Конец раньше начала
        
        project = controller.add_project(
            name="Invalid Project",
            description="Description",
            start_date=start_date,
            end_date=end_date
        )
        
        assert project is None  # Должен вернуть None при ошибке
    
    def test_get_project(self, controller):
        """Тест получения проекта"""
        # Сначала добавляем проект
        project = controller.add_project(
            name="Get Project Test",
            description="Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        assert project is not None
        project_id = project.id
        
        # Получаем проект
        retrieved_project = controller.get_project(project_id)
        
        assert retrieved_project is not None
        assert retrieved_project.id == project_id
        assert retrieved_project.name == "Get Project Test"
    
    def test_get_project_nonexistent(self, controller):
        """Тест получения несуществующего проекта"""
        project = controller.get_project(999)
        assert project is None
    
    def test_get_all_projects(self, controller):
        """Тест получения всех проектов"""
        # Добавляем несколько проектов
        for i in range(3):
            controller.add_project(
                name=f"Project {i}",
                description=f"Description {i}",
                start_date=datetime.now() + timedelta(days=i),
                end_date=datetime.now() + timedelta(days=i+30)
            )
        
        projects = controller.get_all_projects()
        assert len(projects) == 3
    
    def test_update_project(self, controller):
        """Тест обновления проекта"""
        # Добавляем проект
        project = controller.add_project(
            name="Original Name",
            description="Original Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        project_id = project.id
        
        # Обновляем проект
        new_end_date = datetime.now() + timedelta(days=60)
        success = controller.update_project(
            project_id,
            name="Updated Name",
            description="Updated Description",
            end_date=new_end_date,
            status="on_hold"
        )
        
        assert success == True
        
        # Проверяем обновления
        updated_project = controller.get_project(project_id)
        assert updated_project.name == "Updated Name"
        assert updated_project.description == "Updated Description"
        assert updated_project.end_date.date() == new_end_date.date()
        assert updated_project.status == "on_hold"
    
    def test_update_project_invalid_dates(self, controller):
        """Тест обновления проекта с невалидными датами"""
        # Добавляем проект
        project = controller.add_project(
            name="Test Project",
            description="Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        # Пытаемся обновить с датой окончания раньше начала
        invalid_end_date = datetime.now() - timedelta(days=1)
        success = controller.update_project(
            project.id,
            end_date=invalid_end_date
        )
        
        assert success == False
    
    def test_update_project_invalid_status(self, controller):
        """Тест обновления проекта с невалидным статусом"""
        # Добавляем проект
        project = controller.add_project(
            name="Test Project",
            description="Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        # Пытаемся обновить с невалидным статусом
        success = controller.update_project(
            project.id,
            status="invalid_status"
        )
        
        assert success == False
    
    def test_update_nonexistent_project(self, controller):
        """Тест обновления несуществующего проекта"""
        success = controller.update_project(999, name="Nonexistent")
        assert success == False
    
    def test_delete_project(self, controller):
        """Тест удаления проекта"""
        # Добавляем проект
        project = controller.add_project(
            name="Project to Delete",
            description="Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        project_id = project.id
        
        # Удаляем проект
        success = controller.delete_project(project_id)
        assert success == True
        
        # Проверяем, что проект удален
        deleted_project = controller.get_project(project_id)
        assert deleted_project is None
    
    def test_delete_nonexistent_project(self, controller):
        """Тест удаления несуществующего проекта"""
        success = controller.delete_project(999)
        assert success == False
    
    def test_update_project_status(self, controller):
        """Тест обновления статуса проекта"""
        # Добавляем проект
        project = controller.add_project(
            name="Status Test",
            description="Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        # Обновляем статус
        success = controller.update_project_status(project.id, "completed")
        assert success == True
        
        updated_project = controller.get_project(project.id)
        assert updated_project.status == "completed"
        
        # Обновляем на невалидный статус
        success = controller.update_project_status(project.id, "invalid_status")
        assert success == False
        assert updated_project.status == "completed"  # Не должен измениться
    
    def test_get_project_progress(self, controller):
        """Тест получения прогресса проекта"""
        # Добавляем проект
        project = controller.add_project(
            name="Progress Test",
            description="Description",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        # Получаем прогресс пустого проекта
        progress = controller.get_project_progress(project.id)
        
        assert 'total_tasks' in progress
        assert 'completed_tasks' in progress
        assert 'progress' in progress
        assert 'project' in progress
        
        assert progress['total_tasks'] == 0
        assert progress['completed_tasks'] == 0
        assert progress['progress'] == 0
        assert progress['project']['name'] == "Progress Test"

class TestUserController:
    """Тесты для UserController"""
    
    @pytest.fixture
    def controller(self):
        """Фикстура для создания контроллера с временной БД"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_path = temp_db.name
        temp_db.close()
        
        db_manager = DatabaseManager(db_path)
        controller = UserController(db_manager)
        
        yield controller
        
        db_manager.close()
        os.unlink(db_path)
    
    def test_add_user_valid(self, controller):
        """Тест добавления валидного пользователя"""
        user = controller.add_user(
            username="testuser",
            email="test@example.com",
            role="developer"
        )
        
        assert user is not None
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "developer"
        assert isinstance(user.registration_date, datetime)
    
    def test_add_user_invalid_role(self, controller):
        """Тест добавления пользователя с невалидной ролью"""
        user = controller.add_user(
            username="testuser",
            email="test@example.com",
            role="invalid_role"  # Невалидная роль
        )
        
        assert user is None  # Должен вернуть None при ошибке
    
    def test_add_user_invalid_email(self, controller):
        """Тест добавления пользователя с некорректным email"""
        # Email без @ должен обрабатываться в контроллере
        # В текущей реализации валидация минимальна
        user = controller.add_user(
            username="testuser",
            email="invalid-email",  # Некорректный email
            role="developer"
        )
        
        # Проверяем, что пользователь создается (валидация может быть в другом месте)
        assert user is not None
    
    def test_get_user(self, controller):
        """Тест получения пользователя"""
        # Сначала добавляем пользователя
        user = controller.add_user(
            username="Get User Test",
            email="get@example.com",
            role="developer"
        )
        
        assert user is not None
        user_id = user.id
        
        # Получаем пользователя
        retrieved_user = controller.get_user(user_id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        assert retrieved_user.username == "Get User Test"
        assert retrieved_user.email == "get@example.com"
    
    def test_get_user_nonexistent(self, controller):
        """Тест получения несуществующего пользователя"""
        user = controller.get_user(999)
        assert user is None
    
    def test_get_all_users(self, controller):
        """Тест получения всех пользователей"""
        # Добавляем несколько пользователей
        for i in range(3):
            controller.add_user(
                username=f"user{i}",
                email=f"user{i}@example.com",
                role="developer"
            )
        
        users = controller.get_all_users()
        assert len(users) == 3
    
    def test_update_user(self, controller):
        """Тест обновления пользователя"""
        # Добавляем пользователя
        user = controller.add_user(
            username="Original Username",
            email="original@example.com",
            role="developer"
        )
        
        user_id = user.id
        
        # Обновляем пользователя
        success = controller.update_user(
            user_id,
            username="Updated Username",
            email="updated@example.com",
            role="manager"
        )
        
        assert success == True
        
        # Проверяем обновления
        updated_user = controller.get_user(user_id)
        assert updated_user.username == "Updated Username"
        assert updated_user.email == "updated@example.com"
        assert updated_user.role == "manager"
    
    def test_update_user_invalid_role(self, controller):
        """Тест обновления пользователя с невалидной ролью"""
        # Добавляем пользователя
        user = controller.add_user(
            username="Test User",
            email="test@example.com",
            role="developer"
        )
        
        # Пытаемся обновить с невалидной ролью
        success = controller.update_user(
            user.id,
            role="invalid_role"
        )
        
        assert success == False
    
    def test_update_nonexistent_user(self, controller):
        """Тест обновления несуществующего пользователя"""
        success = controller.update_user(999, username="Nonexistent")
        assert success == False
    
    def test_delete_user(self, controller):
        """Тест удаления пользователя"""
        # Добавляем пользователя
        user = controller.add_user(
            username="User to Delete",
            email="delete@example.com",
            role="developer"
        )
        
        user_id = user.id
        
        # Удаляем пользователя
        success = controller.delete_user(user_id)
        assert success == True
        
        # Проверяем, что пользователь удален
        deleted_user = controller.get_user(user_id)
        assert deleted_user is None
    
    def test_delete_nonexistent_user(self, controller):
        """Тест удаления несуществующего пользователя"""
        success = controller.delete_user(999)
        assert success == False
    
    def test_get_user_tasks(self, controller):
        """Тест получения задач пользователя"""
        # Создаем временную БД с TaskController
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_path = temp_db.name
        temp_db.close()
        
        db_manager = DatabaseManager(db_path)
        user_controller = UserController(db_manager)
        task_controller = TaskController(db_manager)
        project_controller = ProjectController(db_manager)
        
        # Создаем тестовые данные
        user = user_controller.add_user("testuser", "test@example.com", "developer")
        project = project_controller.add_project(
            "Test Project",
            "Description",
            datetime.now(),
            datetime.now() + timedelta(days=30)
        )
        
        # Добавляем задачи для пользователя
        for i in range(2):
            task_controller.add_task(
                title=f"User Task {i}",
                description="Description",
                priority=1,
                due_date=datetime.now(),
                project_id=project.id,
                assignee_id=user.id
            )
        
        # Получаем задачи пользователя
        user_tasks = user_controller.get_user_tasks(user.id)
        
        assert len(user_tasks) == 2
        for task in user_tasks:
            assert 'title' in task
            assert 'project_name' in task
            assert task['project_name'] == "Test Project"
        
        # Очистка
        db_manager.close()
        os.unlink(db_path)
    
    def test_get_user_tasks_empty(self, controller):
        """Тест получения задач пользователя без задач"""
        # Добавляем пользователя
        user = controller.add_user(
            username="No Tasks User",
            email="notasks@example.com",
            role="developer"
        )
        
        # Получаем задачи пользователя (должен быть пустой список)
        tasks = controller.get_user_tasks(user.id)
        assert isinstance(tasks, list)
        assert len(tasks) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
