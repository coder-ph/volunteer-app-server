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
    serialize_rules = ('rsvps', '-created_at', '-updated_at', 'rsvps.status')
    
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

class Organization(db.Model, SerializerMixin):
    __tablename__ = 'organizations'
    serialize_rules = ('-events', )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    
    events = db.relationship('Event', back_populates='organization', cascade='all, delete-orphan', lazy='dynamic')
    
class Event(db.Model, SerializerMixin):
    __tablename__ = 'events'
    serialize_rules=('-rsvps', '-organization','-updated_at', '-created_at', 'organization.name',)
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    date=db.Column(db.String)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    created_at =  db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    rsvps = db.relationship('Rsvp', back_populates='event', lazy='dynamic', cascade='all, delete-orphan')
    organization = db.relationship('Organization', back_populates='events')
    
    def __repr__(self):
        return f'<Event: {self.title}, {self.location}, {self.description}, {self.org_id}>'
    
class Rsvp(db.Model, SerializerMixin):
    __tablename__ = 'rsvps'
    
    serialize_rules= ('-user', '-event')
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum('Attending', 'Not attending'), nullable=False) #attending or not
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    
    user = db.relationship('User', back_populates='rsvps')
    event = db.relationship('Event', back_populates='rsvps')
    
    @validates('status')
    def validate_status(self, key, value):
        status =['Attending', 'Not attending']
        if  value in status:
            return value
        else:
            raise ValueError ('status can only be attending or not attending')
        
    def __repr__(self):
        return f'<Rsvp: {self.id}, {self.status}, User: {self.user_id}, Event: {self.event_id}>'