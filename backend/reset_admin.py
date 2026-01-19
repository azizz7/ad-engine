from sqlalchemy.orm import Session
from database_config import SessionLocal, engine, Base
from models import User
from auth import get_password_hash

def reset_admin():
    db = SessionLocal()
    try:
        # Check if admin exists
        user = db.query(User).filter(User.email == "admin@example.com").first()
        
        if user:
            print("Updating existing admin user...")
            user.hashed_password = get_password_hash("admin")
        else:
            print("Creating new admin user...")
            user = User(
                email="admin@example.com", 
                hashed_password=get_password_hash("admin"),
                full_name="Admin User"
            )
            db.add(user)
        
        db.commit()
        print("✅ Admin user configured successfully.")
        print("Email: admin@example.com")
        print("Password: admin")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    reset_admin()
