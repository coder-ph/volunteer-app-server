from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy import Enum 
from datetime import datetime

metadata=MetaData()
db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    role = db.Column(db.Enum('organization', 'volunteer'), nullable=False) #organization or volunteer
    created_at =  db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    rsvps = db.relationship('Rsvp', back_populates='user', cascade ='all, delete-orphan', lazy='dynamic')
    
    @validates('role')
    def validate_role(self, key, value):
        roles = ['organization', 'volunteer']
        if value in roles:
            return value
        else:
            raise ValueError ('A user can either be organization or volunteer')
    
    @validates('username')
    def validate_username(self, key, value):
        if not isinstance(value, str):
            raise ValueError ('username must be a string')
        return value
    
    @validates('email')
    def validate_email(self, key, value):
        if '@' not in value:
            raise ValueError ('Invalid email adress')
        return value
    def __repr__(self):
        return f'<User: {self.id}, {self.username}, {self.email}>'
