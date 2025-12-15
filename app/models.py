from app.extensions import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timezone
from app.extensions import db, bcrypt, ma

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    
    documents = db.relationship('Document', secondary='cheats', backref=db.backref('users', lazy=True))
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)
    
    def __repr__(self):
        return f'<User {self.name}>'
    
class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    users = db.relationship('User', secondary='cheats', backref=db.backref('documents', lazy=True))