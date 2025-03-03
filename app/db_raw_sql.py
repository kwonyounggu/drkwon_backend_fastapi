# https://chatgpt.com/c/67c10871-b490-800a-aa43-cb9aea0bda69
from sqlalchemy import text
from database import SessionLocal

def run_query(query, params=None):
    db = SessionLocal()
    try:
        result = db.execute(text(query), params)
        db.commit()
        return result.fetchall()
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

# Insert example
def insert_user(email, user_type):
    query = "INSERT INTO users (email, user_type) VALUES (:email, :user_type)"
    run_query(query, {"email": email, "user_type": user_type})

# Update example
def update_user_name(user_id, new_name):
    query = "UPDATE users SET name = :name WHERE user_id = :id"
    run_query(query, {"name": new_name, "id": user_id})

# Delete example
def delete_user(user_id):
    query = "DELETE FROM users WHERE user_id = :id"
    run_query(query, {"id": user_id})

# how to call
#insert_user("testuser@example.com", "General")
#update_user_name(1, "Updated Name")
#delete_user(1)