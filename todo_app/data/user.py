from flask_login import UserMixin, current_user
from functools import wraps

ROLES = {
    'reader': 'reader',
    'writer': 'writer'    
}

class User(UserMixin):
    def __init__(self, user_id, username,email, role=ROLES['reader']):
        self.id = user_id
        self.username = username
        self.email = email
        self.role = role     
        
    def is_writer(self):        
        return self.role == ROLES['writer']
    
    def is_reader(self):
        return self.role == ROLES['reader']


def requires_roles(*roles):    
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if type(current_user).__name__!='LocalProxy':
                if current_user.role not in roles:
                    # Redirect the user to an unauthorized notice!
                    return "You are not authorized to access this page"
            return f(*args, **kwargs)
        return wrapped
    return wrapper

    