from datetime import datetime

class Project:
    def __init__(self, name, description, start_date, end_date):
        self.id = None
        self.name = name
        self.description = description
        
        # Преобразуем строки в datetime, если необходимо
        if isinstance(start_date, str):
            self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            self.start_date = start_date
            
        if isinstance(end_date, str):
            self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            self.end_date = end_date
            
        self.status = 'active'  # 'active', 'completed', 'on_hold'
        self.created_at = datetime.now()
        
    def update_status(self, new_status):
        valid_statuses = ['active', 'completed', 'on_hold']
        if new_status in valid_statuses:
            self.status = new_status
            return True
        return False
    
    def get_progress(self):
        # Здесь будет логика расчёта прогресса
        # Пока возвращаем 0 для примера
        # В реальной реализации нужно учитывать количество выполненных задач
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создать объект Project из словаря"""
        project = cls(
            name=data['name'],
            description=data['description'],
            start_date=data['start_date'],
            end_date=data['end_date']
        )
        project.id = data['id']
        project.status = data['status']
        project.created_at = datetime.strptime(data['created_at'], '%Y-%m-%d %H:%M:%S')
        return project
