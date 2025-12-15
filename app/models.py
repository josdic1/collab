from app.extensions import db, bcrypt
from datetime import datetime, timezone

# Junction table for many-to-many relationship
user_documents = db.Table('user_documents',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('document_id', db.Integer, db.ForeignKey('documents.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    
    # Relationship to documents (many-to-many)
    documents = db.relationship('Document', secondary=user_documents, back_populates='users')
    
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
    
    # File metadata (server-added)
    filename = db.Column(db.String(255), nullable=False)  # Original filename
    file_path = db.Column(db.String(500), nullable=False)  # Storage path
    file_type = db.Column(db.String(100), nullable=False)  # MIME type
    file_size = db.Column(db.Integer, nullable=False)      # Size in bytes
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Uploader
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_by = db.relationship('User', foreign_keys=[uploaded_by_id], backref='uploaded_documents')
    
    # Relationship to users who can access (many-to-many)
    users = db.relationship('User', secondary=user_documents, back_populates='documents')
    
    def __repr__(self):
        return f'<Document {self.title}>'