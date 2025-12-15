from flask import request, jsonify, session, send_file
from app.extensions import db
from app.models import User, Document
from app.serializers import user_schema, document_schema, documents_schema
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timezone

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_routes(app):
    
    # ============ AUTH ROUTES ============
    @app.route('/api/signup', methods=['POST'])
    def signup():
        """Create new user"""
        data = request.get_json()
        
        if User.query.filter_by(email=data.get('email')).first():
            return {'error': 'Email already exists'}, 400
        
        user = User(
            name=data['name'],
            email=data['email'],
            password=data['password']
        )
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        return user_schema.dump(user), 201
    
    @app.route('/api/login', methods=['POST'])
    def login():
        """Authenticate user"""
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email')).first()
        
        if user and user.authenticate(data.get('password')):
            session['user_id'] = user.id
            return user_schema.dump(user), 200
        
        return {'error': 'Invalid credentials'}, 401
    
    @app.route('/api/logout', methods=['POST'])
    def logout():
        """End session"""
        session.pop('user_id', None)
        return {'message': 'Logged out'}, 200
    
    @app.route('/api/check_session', methods=['GET'])
    def check_session():
        """Verify session"""
        user_id = session.get('user_id')
        if not user_id:
            return {'logged_in': False}, 401
        
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        
        return {
            'logged_in': True,
            'user': user_schema.dump(user)
        }, 200
    
    # ============ DOCUMENT ROUTES ============
    @app.route('/api/documents', methods=['GET'])
    def get_documents():
        """Get all documents for logged-in user"""
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not logged in'}, 401
        
        user = User.query.get(user_id)
        documents = user.documents  # All documents shared with this user
        
        return documents_schema.dump(documents), 200
    
    @app.route('/api/documents', methods=['POST'])
    def upload_document():
        """Upload a new document"""
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not logged in'}, 401
        
        # Check if file is in request
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No file selected'}, 400
        
        if not allowed_file(file.filename):
            return {'error': 'File type not allowed'}, 400
        
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description', '')
        
        if not title:
            return {'error': 'Title is required'}, 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Ensure uploads directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        file.save(file_path)
        
        # Get file metadata
        file_size = os.path.getsize(file_path)
        file_type = file.content_type or 'application/octet-stream'
        
        # Create document record
        document = Document(
            title=title,
            description=description,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            uploaded_by_id=user_id
        )
        
        # Share with current user
        user = User.query.get(user_id)
        document.users.append(user)
        
        db.session.add(document)
        db.session.commit()
        
        return document_schema.dump(document), 201
    
    @app.route('/api/documents/<int:doc_id>', methods=['GET'])
    def get_document(doc_id):
        """Get single document"""
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not logged in'}, 401
        
        document = Document.query.get_or_404(doc_id)
        
        # Check if user has access
        user = User.query.get(user_id)
        if user not in document.users:
            return {'error': 'Unauthorized'}, 403
        
        return document_schema.dump(document), 200
    
    @app.route('/api/documents/<int:doc_id>/download', methods=['GET'])
    def download_document(doc_id):
        """Download document file"""
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not logged in'}, 401
        
        document = Document.query.get_or_404(doc_id)
        
        # Check if user has access
        user = User.query.get(user_id)
        if user not in document.users:
            return {'error': 'Unauthorized'}, 403
        
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.filename
        )
    
    @app.route('/api/documents/<int:doc_id>', methods=['PATCH'])
    def update_document(doc_id):
        """Update document metadata"""
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not logged in'}, 401
        
        document = Document.query.get_or_404(doc_id)
        
        # Check if user has access
        user = User.query.get(user_id)
        if user not in document.users:
            return {'error': 'Unauthorized'}, 403
        
        data = request.get_json()
        
        if 'title' in data:
            document.title = data['title']
        if 'description' in data:
            document.description = data['description']
        
        document.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return document_schema.dump(document), 200
    
    @app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
    def delete_document(doc_id):
        """Delete document"""
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not logged in'}, 401
        
        document = Document.query.get_or_404(doc_id)
        
        # Only uploader can delete
        if document.uploaded_by_id != user_id:
            return {'error': 'Unauthorized'}, 403
        
        # Delete file from filesystem
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        db.session.delete(document)
        db.session.commit()
        
        return {'message': 'Deleted'}, 200
    
    @app.route('/api/documents/<int:doc_id>/url', methods=['GET'])
    def get_document_url(doc_id):
        """Get shareable URL for document"""
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Not logged in'}, 401
        
        document = Document.query.get_or_404(doc_id)
        
        # Check if user has access
        user = User.query.get(user_id)
        if user not in document.users:
            return {'error': 'Unauthorized'}, 403
        
        # Generate URL (adjust based on your domain)
        url = f"{request.host_url}api/documents/{doc_id}/download"
        
        return {'url': url}, 200