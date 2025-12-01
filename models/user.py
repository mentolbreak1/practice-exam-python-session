from datetime import datetime

class User:
    def __init__(self, username, email, role):
        self.id = None
        self.username = username
        self.email = email
        self.role = role  # 'admin', 'manager', 'developer'
        self.registration_date = datetime.now()
        
    def update_info(self, username=None, email=None, role=None):
        if username:
            self.username = username
        if email:
            self.email = email
        if role and role in ['admin', 'manager', 'developer']:
            self.role = role
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'registration_date': self.registration_date.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создать объект User из словаря"""
        user = cls(
            username=data['username'],
            email=data['email'],
            role=data['role']
        )
        user.id = data['id']
        user.registration_date = datetime.strptime(data['registration_date'], '%Y-%m-%d %H:%M:%S')
        return user
