# https://chatgpt.com/c/67c10871-b490-800a-aa43-cb9aea0bda69
import logging
import re
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from database import SessionLocal

# Configure logging
logging.basicConfig(filename='database.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Email validation
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

def run_query(query, params=None):
    db = SessionLocal()
    try:
        result = db.execute(text(query), params)
        db.commit()
        logging.info("Query executed successfully: %s", query)
        return result.fetchall()
    except IntegrityError:
        db.rollback()
        logging.error("Integrity Error: Possible duplicate entry.")
        return {"status": "error", "message": "Duplicate entry"}
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Database Error: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        db.rollback()
        logging.error(f"Unexpected Error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# Insert user
def insert_user(user_data):
    if not is_valid_email(user_data.email):
        logging.warning(f"Invalid email format: {user_data.email}")
        return {"status": "error", "message": "Invalid email format"}

    query = """
    INSERT INTO users (email, user_type, name, picture)
    VALUES (:email, :user_type, :name, :picture)
    RETURNING user_id
    """
    params = user_data.model_dump()
    result = run_query(query, params)
    return handle_result(result, "User added")

# Update user
def update_user(user_id, update_data):
    query = "UPDATE users SET name = :name, picture = :picture WHERE user_id = :user_id"
    params = {**update_data.model_dump(), "user_id": user_id}
    result = run_query(query, params)
    return handle_result(result, "User updated")

# Delete user
def delete_user(user_id):
    query = "DELETE FROM users WHERE user_id = :user_id"
    result = run_query(query, {"user_id": user_id})
    return handle_result(result, "User deleted")

# Insert blog
def insert_blog(blog_data):
    query = """
    INSERT INTO blogs (title, content, visibility, author_id)
    VALUES (:title, :content, :visibility, :author_id)
    RETURNING blog_id
    """
    params = blog_data.model_dump()
    result = run_query(query, params)
    return handle_result(result, "Blog added")

# Update blog
def update_blog(blog_id, update_data):
    query = "UPDATE blogs SET title = :title, content = :content, visibility = :visibility WHERE blog_id = :blog_id"
    params = {**update_data.model_dump(), "blog_id": blog_id}
    result = run_query(query, params)
    return handle_result(result, "Blog updated")

# Delete blog
def delete_blog(blog_id):
    query = "DELETE FROM blogs WHERE blog_id = :blog_id"
    result = run_query(query, {"blog_id": blog_id})
    return handle_result(result, "Blog deleted")

# Fetch users with filters
def fetch_users(filters=None):
    query = "SELECT user_id, email, user_type, name, picture FROM users"
    if filters:
        conditions = [f"{key} = :{key}" for key in filters.keys()]
        query += " WHERE " + " AND ".join(conditions)
    result = run_query(query, filters)
    return handle_fetch_result(result)

# Fetch blogs with author details
def fetch_blogs_with_authors():
    query = """
    SELECT blogs.blog_id, blogs.title, blogs.content, blogs.visibility, users.name AS author_name
    FROM blogs
    JOIN users ON blogs.author_id = users.user_id
    """
    result = run_query(query)
    return handle_fetch_result(result)

# Handle query results
def handle_result(result, success_message):
    if result and isinstance(result, list):
        logging.info(success_message)
        return {"status": "success", "message": success_message}
    return result

# Handle fetch results
def handle_fetch_result(result):
    if result and isinstance(result, list):
        return {"status": "success", "data": result}
    return {"status": "error", "message": "No records found"}

# 📩 **CRUD for Comments**

def insert_comment(comment_data):
    query = """
    INSERT INTO comments (blog_id, user_id, content, is_hidden)
    VALUES (:blog_id, :user_id, :content, :is_hidden)
    RETURNING comment_id
    """
    params = comment_data.model_dump()
    result = run_query(query, params)
    return handle_result(result, "Comment added")


def update_comment(comment_id, update_data):
    query = "UPDATE comments SET content = :content, is_hidden = :is_hidden WHERE comment_id = :comment_id"
    params = {**update_data.model_dump(), "comment_id": comment_id}
    result = run_query(query, params)
    return handle_result(result, "Comment updated")


def delete_comment(comment_id):
    query = "DELETE FROM comments WHERE comment_id = :comment_id"
    result = run_query(query, {"comment_id": comment_id})
    return handle_result(result, "Comment deleted")


# 🔧 **CRUD for Admin Actions**

def insert_admin_action(action_data):
    query = """
    INSERT INTO admin_actions (admin_id, target_user_id, target_blog_id, target_comment_id, action_type, reason)
    VALUES (:admin_id, :target_user_id, :target_blog_id, :target_comment_id, :action_type, :reason)
    RETURNING action_id
    """
    params = action_data.model_dump()
    result = run_query(query, params)
    return handle_result(result, "Admin action recorded")


def update_admin_action(action_id, update_data):
    query = "UPDATE admin_actions SET reason = :reason WHERE action_id = :action_id"
    params = {**update_data.model_dump(), "action_id": action_id}
    result = run_query(query, params)
    return handle_result(result, "Admin action updated")


def delete_admin_action(action_id):
    query = "DELETE FROM admin_actions WHERE action_id = :action_id"
    result = run_query(query, {"action_id": action_id})
    return handle_result(result, "Admin action deleted")


# 🕵️ **CRUD for Login History**

def insert_login_history(login_data):
    query = """
    INSERT INTO login_history (user_id, login_timestamp, ip_address, user_agent, is_success, failure_reason)
    VALUES (:user_id, :login_timestamp, :ip_address, :user_agent, :is_success, :failure_reason)
    RETURNING login_id
    """
    params = login_data.model_dump()
    result = run_query(query, params)
    return handle_result(result, "Login history recorded")


def delete_login_history(login_id):
    query = "DELETE FROM login_history WHERE login_id = :login_id"
    result = run_query(query, {"login_id": login_id})
    return handle_result(result, "Login history deleted")

# how to call
#insert_user("testuser@example.com", "General")
#update_user_name(1, "Updated Name")
#delete_user(1)
#fetch_users()
"""
insert_user("validuser@example.com", "General", name="Test User", picture="http://example.com/pic.jpg")
insert_user("invalid-email", "General")

users_to_add = [
    {"email": "batch1@example.com", "user_type": "Doctor", "name": "Dr. John Doe"},
    {"email": "invalid-batch-email", "user_type": "General"},
    {"email": "batch2@example.com", "user_type": "Admin", "picture": "http://example.com/avatar.png"}
]

insert_multiple_users(users_to_add)
fetch_users()
"""