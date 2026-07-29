# test_db_write.py
from database import SessionLocal, Session, Conversation

def test_save():
    # 1. Open a manual database session
    db = SessionLocal()
    try:
        print("Testing database write...")

        # 2. Create the parent Session row FIRST
        new_session = Session()
        db.add(new_session)
        db.commit()  # <-- CRITICAL! This saves the session and generates its ID.
        db.refresh(new_session)
        
        print(f"Successfully created Chat Session with ID: {new_session.id}")

        # 3. Create and save the Conversation row
        new_message = Conversation(
            session_id=new_session.id,
            role="user",
            message="Hello, is this working?"
        )
        db.add(new_message)
        db.commit()  # <-- CRITICAL! Saves the message.
        
        print("Successfully saved conversation message!")

        # 4. Verify we can read it back
        saved_messages = db.query(Conversation).filter(Conversation.session_id == new_session.id).all()
        print(f"Retrieved from Database: '{saved_messages[0].message}' (Role: {saved_messages[0].role})")

    except Exception as e:
        db.rollback() # Rollback if something broke
        print(f"❌ Error saving to database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_save()