import pytest
import tempfile
import os
import sys
from datetime import datetime, timedelta

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.database_manager import DatabaseManager
from models.task import Task
from models.project import Project
from models.user import User

class TestDatabaseManager:
    """Тесты для DatabaseManager"""
    
    @pytest.fixture
    def db_manager(self):
        """Фикстура для создания временной базы данных"""
        # Создаем временный файл базы данных
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_path = temp_db.name
        temp_db.close()
        
        # Создаем менеджер базы данных
        manager = DatabaseManager(db_path)
        yield manager
        
        # Закрываем соединение и удаляем файл
        manager.close()
        os.unlink(db_path)
    
    def test_connection(self, db_manager):
        """Тест подключения к базе данных"""
        assert db_manager.connection is not None
        assert db_manager.cursor is not None
        
        # Проверяем, что можем выполнить запрос
        db_manager.cursor.execute("SELECT 1")
        result = db_manager.cursor.fetchone()
        assert result[0] == 1
    
    def test_create_tables(self, db_manager):
        """Тест создания таблиц"""
        # Таблицы создаются в конструкторе
        # Проверяем их существование
        db_manager.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in db_manager.cursor.fetchall()]
        
        assert 'users' in tables
        assert 'projects' in tables
        assert 'tasks' in tables
    
    def test_user_crud(self, db_manager):
        """Тест CRUD операций для пользователей"""
        # Создание пользователя
        user = User("testuser", "test@example.com", "developer")
        user_id = db_manager.add_user(user)
        
        assert user_id is not None
        assert isinstance(user_id, int)
        
        # Чтение пользователя
        user_data = db_manager.get_user_by_id(user_id)
        assert user_data is not None
        assert user_data['username'] == "testuser"
        assert user_data['email'] == "test@example.com"
        assert user_data['role'] == "developer"
        
        # Получение всех пользователей
        all_users = db_manager.get_all_users()
        assert len(all_users) == 1
        assert all_users[0]['username'] == "testuser"
        
        # Обновление пользователя
        update_success = db_manager.update_user(user_id, username="updateduser", email="updated@example.com")
        assert update_success == True
        
        updated_user = db_manager.get_user_by_id(user_id)
        assert updated_user['username'] == "updateduser"
        assert updated_user['email'] == "updated@example.com"
        
        # Удаление пользователя
        delete_success = db_manager.delete_user(user_id)
        assert delete_success == True
        
        deleted_user = db_manager.get_user_by_id(user_id)
        assert deleted_user is None
        
        # Проверяем, что пользователей нет
        all_users = db_manager.get_all_users()
        assert len(all_users) == 0
    
    def test_project_crud(self, db_manager):
        """Тест CRUD операций для проектов"""
        # Создание проекта
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        project = Project("Test Project", "Test Description", start_date, end_date)
        project_id = db_manager.add_project(project)
        
        assert project_id is not None
        assert isinstance(project_id, int)
        
        # Чтение проекта
        project_data = db_manager.get_project_by_id(project_id)
        assert project_data is not None
        assert project_data['name'] == "Test Project"
        assert project_data['description'] == "Test Description"
        assert project_data['status'] == "active"
        
        # Получение всех проектов
        all_projects = db_manager.get_all_projects()
        assert len(all_projects) == 1
        assert all_projects[0]['name'] == "Test Project"
        
        # Обновление проекта
        new_end_date = end_date + timedelta(days=10)
        update_success = db_manager.update_project(
            project_id, 
            name="Updated Project",
            status="completed",
            end_date=new_end_date
        )
        assert update_success == True
        
        updated_project = db_manager.get_project_by_id(project_id)
        assert updated_project['name'] == "Updated Project"
        assert updated_project['status'] == "completed"
        
        # Удаление проекта
        delete_success = db_manager.delete_project(project_id)
        assert delete_success == True
        
        deleted_project = db_manager.get_project_by_id(project_id)
        assert deleted_project is None
        
        # Проверяем, что проектов нет
        all_projects = db_manager.get_all_projects()
        assert len(all_projects) == 0
    
    def test_task_crud(self, db_manager):
        """Тест CRUD операций для задач"""
        # Сначала создаем пользователя и проект
        user = User("taskuser", "task@example.com", "developer")
        user_id = db_manager.add_user(user)
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        project = Project("Task Project", "Description", start_date, end_date)
        project_id = db_manager.add_project(project)
        
        # Создание задачи
        due_date = datetime.now() + timedelta(days=7)
        task = Task(
            title="Test Task",
            description="Task Description",
            priority=1,
            due_date=due_date,
            project_id=project_id,
            assignee_id=user_id
        )
        task_id = db_manager.add_task(task)
        
        assert task_id is not None
        assert isinstance(task_id, int)
        
        # Чтение задачи
        task_data = db_manager.get_task_by_id(task_id)
        assert task_data is not None
        assert task_data['title'] == "Test Task"
        assert task_data['description'] == "Task Description"
        assert task_data['priority'] == 1
        assert task_data['status'] == "pending"
        assert task_data['project_id'] == project_id
        assert task_data['assignee_id'] == user_id
        
        # Получение всех задач
        all_tasks = db_manager.get_all_tasks()
        assert len(all_tasks) == 1
        assert all_tasks[0]['title'] == "Test Task"
        
        # Обновление задачи
        update_success = db_manager.update_task(
            task_id,
            title="Updated Task",
            status="in_progress",
            priority=2
        )
        assert update_success == True
        
        updated_task = db_manager.get_task_by_id(task_id)
        assert updated_task['title'] == "Updated Task"
        assert updated_task['status'] == "in_progress"
        assert updated_task['priority'] == 2
        
        # Удаление задачи
        delete_success = db_manager.delete_task(task_id)
        assert delete_success == True
        
        deleted_task = db_manager.get_task_by_id(task_id)
        assert deleted_task is None
        
        # Проверяем, что задач нет
        all_tasks = db_manager.get_all_tasks()
        assert len(all_tasks) == 0
    
    def test_search_tasks(self, db_manager):
        """Тест поиска задач"""
        # Создаем тестовые данные
        user = User("testuser", "test@example.com", "developer")
        user_id = db_manager.add_user(user)
        
        project = Project("Test Project", "Description", datetime.now(), datetime.now())
        project_id = db_manager.add_project(project)
        
        # Создаем задачи с разными названиями
        task1 = Task("Database Task", "Search test", 1, datetime.now(), project_id, user_id)
        task2 = Task("Another Task", "Database test", 2, datetime.now(), project_id, user_id)
        task3 = Task("Test Three", "Description", 3, datetime.now(), project_id, user_id)
        
        db_manager.add_task(task1)
        db_manager.add_task(task2)
        db_manager.add_task(task3)
        
        # Поиск по названию
        results = db_manager.search_tasks("Database")
        assert len(results) == 1
        assert results[0]['title'] == "Database Task"
        
        # Поиск по описанию
        results = db_manager.search_tasks("Search")
        assert len(results) == 1
        assert results[0]['description'] == "Search test"
        
        # Поиск, который находит несколько задач
        results = db_manager.search_tasks("Task")
        assert len(results) == 2
        titles = [r['title'] for r in results]
        assert "Database Task" in titles
        assert "Another Task" in titles
        
        # Поиск без результатов
        results = db_manager.search_tasks("Nonexistent")
        assert len(results) == 0
    
    def test_get_tasks_by_project(self, db_manager):
        """Тест получения задач по проекту"""
        # Создаем тестовые данные
        user = User("testuser", "test@example.com", "developer")
        user_id = db_manager.add_user(user)
        
        project1 = Project("Project 1", "Description", datetime.now(), datetime.now())
        project2 = Project("Project 2", "Description", datetime.now(), datetime.now())
        
        project1_id = db_manager.add_project(project1)
        project2_id = db_manager.add_project(project2)
        
        # Создаем задачи для разных проектов
        task1 = Task("Task 1", "Desc", 1, datetime.now(), project1_id, user_id)
        task2 = Task("Task 2", "Desc", 2, datetime.now(), project1_id, user_id)
        task3 = Task("Task 3", "Desc", 3, datetime.now(), project2_id, user_id)
        
        db_manager.add_task(task1)
        db_manager.add_task(task2)
        db_manager.add_task(task3)
        
        # Получаем задачи для проекта 1
        project1_tasks = db_manager.get_tasks_by_project(project1_id)
        assert len(project1_tasks) == 2
        assert all(task['project_id'] == project1_id for task in project1_tasks)
        
        # Получаем задачи для проекта 2
        project2_tasks = db_manager.get_tasks_by_project(project2_id)
        assert len(project2_tasks) == 1
        assert project2_tasks[0]['project_id'] == project2_id
        
        # Проект без задач
        empty_project = Project("Empty", "Desc", datetime.now(), datetime.now())
        empty_project_id = db_manager.add_project(empty_project)
        empty_tasks = db_manager.get_tasks_by_project(empty_project_id)
        assert len(empty_tasks) == 0
    
    def test_get_tasks_by_user(self, db_manager):
        """Тест получения задач по пользователю"""
        # Создаем тестовых пользователей
        user1 = User("user1", "user1@example.com", "developer")
        user2 = User("user2", "user2@example.com", "developer")
        
        user1_id = db_manager.add_user(user1)
        user2_id = db_manager.add_user(user2)
        
        project = Project("Test Project", "Description", datetime.now(), datetime.now())
        project_id = db_manager.add_project(project)
        
        # Создаем задачи для разных пользователей
        task1 = Task("Task 1", "Desc", 1, datetime.now(), project_id, user1_id)
        task2 = Task("Task 2", "Desc", 2, datetime.now(), project_id, user1_id)
        task3 = Task("Task 3", "Desc", 3, datetime.now(), project_id, user2_id)
        
        db_manager.add_task(task1)
        db_manager.add_task(task2)
        db_manager.add_task(task3)
        
        # Получаем задачи для user1
        user1_tasks = db_manager.get_tasks_by_user(user1_id)
        assert len(user1_tasks) == 2
        assert all(task['assignee_id'] == user1_id for task in user1_tasks)
        
        # Получаем задачи для user2
        user2_tasks = db_manager.get_tasks_by_user(user2_id)
        assert len(user2_tasks) == 1
        assert user2_tasks[0]['assignee_id'] == user2_id
        
        # Пользователь без задач
        user3 = User("user3", "user3@example.com", "developer")
        user3_id = db_manager.add_user(user3)
        user3_tasks = db_manager.get_tasks_by_user(user3_id)
        assert len(user3_tasks) == 0
    
    def test_get_overdue_tasks(self, db_manager):
        """Тест получения просроченных задач"""
        user = User("testuser", "test@example.com", "developer")
        user_id = db_manager.add_user(user)
        
        project = Project("Test Project", "Description", datetime.now(), datetime.now())
        project_id = db_manager.add_project(project)
        
        # Создаем задачи с разными сроками
        # Просроченная задача
        past_date = datetime.now() - timedelta(days=1)
        task1 = Task("Overdue Task", "Desc", 1, past_date, project_id, user_id)
        
        # Непросроченная задача
        future_date = datetime.now() + timedelta(days=1)
        task2 = Task("Not Overdue", "Desc", 2, future_date, project_id, user_id)
        
        # Просроченная, но завершенная задача
        task3 = Task("Completed Overdue", "Desc", 3, past_date, project_id, user_id)
        task3.status = "completed"
        
        task1_id = db_manager.add_task(task1)
        task2_id = db_manager.add_task(task2)
        task3_id = db_manager.add_task(task3)
        
        # Получаем просроченные задачи
        overdue_tasks = db_manager.get_overdue_tasks()
        
        # Должна быть только одна просроченная незавершенная задача
        assert len(overdue_tasks) == 1
        assert overdue_tasks[0]['title'] == "Overdue Task"
        
        # Помечаем задачу как завершенную
        db_manager.update_task(task1_id, status="completed")
        
        # Теперь просроченных задач не должно быть
        overdue_tasks = db_manager.get_overdue_tasks()
        assert len(overdue_tasks) == 0
    
    def test_get_project_progress(self, db_manager):
        """Тест получения прогресса проекта"""
        user = User("testuser", "test@example.com", "developer")
        user_id = db_manager.add_user(user)
        
        project = Project("Test Project", "Description", datetime.now(), datetime.now())
        project_id = db_manager.add_project(project)
        
        # Проект без задач
        progress1 = db_manager.get_project_progress(project_id)
        assert progress1['total_tasks'] == 0
        assert progress1['completed_tasks'] == 0
        assert progress1['progress'] == 0
        
        # Добавляем задачи
        task1 = Task("Task 1", "Desc", 1, datetime.now(), project_id, user_id)
        task2 = Task("Task 2", "Desc", 2, datetime.now(), project_id, user_id)
        task3 = Task("Task 3", "Desc", 3, datetime.now(), project_id, user_id)
        
        task1_id = db_manager.add_task(task1)
        task2_id = db_manager.add_task(task2)
        task3_id = db_manager.add_task(task3)
        
        # Ни одна задача не завершена
        progress2 = db_manager.get_project_progress(project_id)
        assert progress2['total_tasks'] == 3
        assert progress2['completed_tasks'] == 0
        assert progress2['progress'] == 0.0
        
        # Завершаем 2 задачи
        db_manager.update_task(task1_id, status="completed")
        db_manager.update_task(task2_id, status="completed")
        
        # 2 из 3 задач завершены (66.67%)
        progress3 = db_manager.get_project_progress(project_id)
        assert progress3['total_tasks'] == 3
        assert progress3['completed_tasks'] == 2
        assert abs(progress3['progress'] - 66.67) < 0.01
        
        # Завершаем все задачи
        db_manager.update_task(task3_id, status="completed")
        
        # Все задачи завершены (100%)
        progress4 = db_manager.get_project_progress(project_id)
        assert progress4['total_tasks'] == 3
        assert progress4['completed_tasks'] == 3
        assert progress4['progress'] == 100.0
    
    def test_update_invalid_id(self, db_manager):
        """Тест обновления несуществующей записи"""
        # Пытаемся обновить несуществующего пользователя
        success = db_manager.update_user(999, username="nonexistent")
        assert success == False
        
        # Пытаемся обновить несуществующий проект
        success = db_manager.update_project(999, name="nonexistent")
        assert success == False
        
        # Пытаемся обновить несуществующую задачу
        success = db_manager.update_task(999, title="nonexistent")
        assert success == False
    
    def test_delete_invalid_id(self, db_manager):
        """Тест удаления несуществующей записи"""
        # Пытаемся удалить несуществующего пользователя
        success = db_manager.delete_user(999)
        assert success == False
        
        # Пытаемся удалить несуществующий проект
        success = db_manager.delete_project(999)
        assert success == False
        
        # Пытаемся удалить несуществующую задачу
        success = db_manager.delete_task(999)
        assert success == False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
