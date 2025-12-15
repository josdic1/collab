#!/usr/bin/env python3
from app import create_app
from app.extensions import db
from app.models import User

def seed():
    app = create_app()
    with app.app_context():
        print("🌱 Seeding database...")
        
        # Clear existing
        User.query.delete()
        db.session.commit()
        
        # Create 2 users
        user1 = User(
            name="josh",
            email="josh@josh.com",
            password="1111"
        )
        
        user1 = User(
            name="partner",
            email="partner@partner.com",
            password="1111"
        )
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        print("✅ Seeded 2 users!")

if __name__ == "__main__":
    seed()