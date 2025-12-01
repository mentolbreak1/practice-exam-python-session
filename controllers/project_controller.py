from typing import List, Dict, Any, Optional
from models.project import Project
from database.database_manager import DatabaseManager

class ProjectController:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def add_project(self, name: str, description: str, start_date, end_date) -> Optional[Project]:
        """Добавить проект"""
        try:
            # Валидация дат
            if start_date >= end_date:
                raise ValueError("Start date must be before end date")
            
            # Создаем объект проекта
            project = Project(
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date
            )
            
            # Добавляем в базу данных
            project_id = self.db_manager.add_project(project)
            project.id = project_id
            
            return project
            
        except Exception as e:
            print(f"Error adding project: {e}")
            return None
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Получить проект"""
        try:
            project_data = self.db_manager.get_project_by_id(project_id)
            if project_data:
                return Project.from_dict(project_data)
            return None
        except Exception as e:
            print(f"Error getting project: {e}")
            return None
    
    def get_all_projects(self) -> List[Project]:
        """Получить все проекты"""
        try:
            projects_data = self.db_manager.get_all_projects()
            return [Project.from_dict(data) for data in projects_data]
        except Exception as e:
            print(f"Error getting all projects: {e}")
            return []
    
    def update_project(self, project_id: int, **kwargs) -> bool:
        """Обновить проект"""
        try:
            # Проверяем существование проекта
            project = self.get_project(project_id)
            if not project:
                return False
            
            # Валидация данных
            if 'status' in kwargs and kwargs['status'] not in ['active', 'completed', 'on_hold']:
                raise ValueError("Invalid status")
            
            # Валидация дат
            if 'start_date' in kwargs and 'end_date' in kwargs:
                if kwargs['start_date'] >= kwargs['end_date']:
                    raise ValueError("Start date must be before end date")
            
            # Обновляем в базе данных
            return self.db_manager.update_project(project_id, **kwargs)
            
        except Exception as e:
            print(f"Error updating project: {e}")
            return False
    
    def delete_project(self, project_id: int) -> bool:
        """Удалить проект"""
        try:
            return self.db_manager.delete_project(project_id)
        except Exception as e:
            print(f"Error deleting project: {e}")
            return False
    
    def update_project_status(self, project_id: int, new_status: str) -> bool:
        """Обновить статус проекта"""
        try:
            # Получаем проект
            project = self.get_project(project_id)
            if not project:
                return False
            
            # Обновляем статус в объекте
            if project.update_status(new_status):
                # Обновляем в базе данных
                return self.db_manager.update_project(project_id, status=new_status)
            return False
            
        except Exception as e:
            print(f"Error updating project status: {e}")
            return False
    
    def get_project_progress(self, project_id: int) -> Dict[str, Any]:
        """Получить прогресс проекта"""
        try:
            progress_data = self.db_manager.get_project_progress(project_id)
            
            # Получаем информацию о проекте
            project = self.get_project(project_id)
            if project:
                progress_data['project'] = project.to_dict()
            
            return progress_data
            
        except Exception as e:
            print(f"Error getting project progress: {e}")
            return {'total_tasks': 0, 'completed_tasks': 0, 'progress': 0}
