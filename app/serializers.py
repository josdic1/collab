from app.extensions import ma
from app.models import User, Document

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('_password_hash',)

class DocumentSchema(ma.SQLAlchemyAutoSchema):
    uploaded_by = ma.Nested(UserSchema, only=('id', 'name', 'email'))
    users = ma.Nested(UserSchema, many=True, only=('id', 'name', 'email'))
    
    class Meta:
        model = Document
        load_instance = True
        include_fk = True

# Schema instances
user_schema = UserSchema()
users_schema = UserSchema(many=True)
document_schema = DocumentSchema()
documents_schema = DocumentSchema(many=True)