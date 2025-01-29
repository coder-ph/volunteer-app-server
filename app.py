
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response, session
from flask_restful import Api, Resource
from models import Organization, User, Event, Rsvp, db
from flask_cors import CORS
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///app.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)
CORS(app)

@app.route('/')
def index():
    return '<h2>Volunteer Application</h2>'

class Users(Resource):
    def get(self):
        users = User.query.all()
        if len(users) < 1:
            return {'message': 'no users available'}, 200
        user =[usr.to_dict() for usr in users]
        
        response = make_response(
            user,
            200
        )
        return response
    
    def post(self):
        data = request.get_json()
        required_fields = ['username', 'email', 'role']
        missing_data =[field for field in required_fields if field not in data or not data[field]]
        if missing_data:
            return make_response({'error': f'invalid payload {",".join(missing_data)}'}, 400)
        
        username = data.get('username')
        email = data.get('email')
        role = data.get('role') 
        valid_roles = ['organization', 'volunteer']
        if role not in valid_roles:
            return make_response({'error':f'Invalid role {role}'}, 400)           
        
        try:
            user = db.session.query(User).filter(User.email == email).first()
            if user:
                return make_response({'error': 'User already exist'}, 400)
            new_user = User(username=username, email=email, role=role)
            db.session.add(new_user)
            db.session.commit()
            return make_response({'message':'User added successfully'}, 201)
        except Exception as e:
            db.session.rollback()
            return make_response({'error': f'{str(e)}'})

class UsersDetail(Resource) :  
    def get(self, id):
        user = User.query.get(id)
        if not user:
            return make_response({'error':'user does not found'}, 404)
        return user.to_dict(), 200
    
    def delete(self, id):
        user = db.session.query(User).get(id)
        if not user:
            return make_response({"error":'User not found'}, 404)
        db.session.delete(user)
        db.session.commit()
        return make_response({'message': 'User deleted successfully'}, 200)

class Organizations(Resource):
    def get(self):
        try:
            organizations = db.session.query(Organization).all()
            if not len(organizations):
                return make_response(
                    {'message': 'No organizations to view'},
                    200
                )
        except Exception as e :
            return make_response({'error': str(e)}, 500)
        
        organization = [org.to_dict() for org in organizations]
        return make_response(
            organization,
            200
        )
        
class OrganizationDetails(Resource):
    def get(self, id):
        organization = db.session.query(Organization).get(id)
        if not organization:
            return make_response(
                {'message': 'Organization not found'},
                404
            )
        return make_response(
            organization.to_dict(),
            200
        )
class Events(Resource):
    def get(self):
        events = Event.query.options(joinedload(Event.organization)).all()
        if not len(events):
            return make_response(
                [],
                200
            )
        event = [evnt.to_dict() for evnt in events]
        return make_response(
            event,
            200)
        
    def post(self):
        data = request.get_json()
        required_fields = ['title', 'location', 'description', 'org_id']
        missing_fields =[fields for fields in required_fields if fields not in data or not data[fields]]
        if missing_fields:
            return make_response(
                {'error': 'invalid payload'}, 
                400
            )
            
        title = data.get('title')
        location = data.get('location')
        description = data.get('description')
        org_id = data.get('org_id')
        
        new_event = Event(title=title, location=location, description=description, org_id=org_id)
        db.session.add(new_event)
        db.session.commit()
        
        return make_response(
            new_event.to_dict(), 
            201
        )
class Eventdetail(Resource):
    def get(self, id):
        event = db.session.query(Event).get(id)
        if not event:
            return make_response(
                {'message': 'event not found'},
                404
            )
        return make_response(
            event,
            200
        ) 
        
    def post(self, id):
        event = db.session.query(Event).get(id)
        if not event:
            return make_response(
                {'message': 'event not found'},
                404
            )
        data = request.get_json()
        for key, value in data.items():
            try:
                if hasattr(event, key):
                    setattr(event, key, value)
                else:
                    return make_response(
                        {'message': f'invalid attribute: {key}'},
                        400
                    )
                     
            except Exception as e:
                db.session.rollback()
                return make_response(
                    {'error': f'{str(e)}'}
                )
                
        db.session.commit()
        return make_response(
            {'message': 'Event updated successfully'},
            200
        )
             
    def delete(self, id):
        event = db.session.query(Event).get(id)
        if not event:
            return make_response(
                {'message': 'event not found'},
                200
            )
        db.session.delete(event)
        db.session.commit()
        
        return make_response(
            {'message': 'event deleted successfully'},
            200
        )
api.add_resource(Users, '/users')
api.add_resource(UsersDetail, '/users/<int:id>')
api.add_resource(Organizations, '/organizations')
api.add_resource(OrganizationDetails, '/organizations/<int:id>')
api.add_resource(Events, '/events')
api.add_resource(Eventdetail, '/events/<int:id>')
       
            
if __name__ == '__main__':
    app.run(port=5555, debug=True)