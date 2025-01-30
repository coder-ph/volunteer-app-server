from random import randint, choice as rc
from faker import Faker
from app import app
from models import Organization, User, Event, Rsvp, db

fake = Faker()
with app.app_context():
    
    Organization.query.delete()
    Rsvp.query.delete()
    Event.query.delete()
    User.query.delete()
    
    organizations = []
    for _ in range(20):  
        org = Organization(
            name=fake.company(),
            description=fake.catch_phrase(),
            location=fake.city()
        )
        organizations.append(org)
        db.session.add(org)
    
    # Seed users
    users = []
    for _ in range(20):  
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            role=rc(['organization', 'volunteer'])  
        )
        users.append(user)
        db.session.add(user)
    
    # Seed events
    events = []
    
    for _ in range(20):  
        event = Event(
            title=fake.catch_phrase(),
            location=fake.city(),
            description=fake.text(max_nb_chars=200),
            date = fake.date(),
            org_id=rc(range(5)) 
        )
        events.append(event)
        db.session.add(event)
    
    # Seed RSVPs
    for _ in range(20):  
        rsvp = Rsvp(
            status=rc(['Attending', 'Not attending']),  
            user_id=rc(range(10)),  
            event_id=rc(range(10))  
        )
        db.session.add(rsvp)
    
    # Commit changes to the database
    db.session.commit()
    print("Database seeded successfully!")