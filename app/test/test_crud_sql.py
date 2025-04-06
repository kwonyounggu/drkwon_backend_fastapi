from schemas import UserCreate, BlogCreate, CommentCreate, AdminActionRequest, LoginHistoryResponse
import app.crud_sql as crud_sql
# Insert user
crud_sql.insert_user(UserCreate(email="test@example.com", user_type="General", name="Test User", picture=None))

# Update user
crud_sql.update_user(1, UserCreate(name="Updated Name", picture="http://example.com/avatar.jpg"))

# Delete user
crud_sql.delete_user(1)

# Insert blog
crud_sql.insert_blog(BlogCreate(title="My First Blog", content="Hello, world!", visibility="Public", author_id=1))

# Update blog
crud_sql.update_blog(1, BlogCreate(title="Updated Blog Title", content="Updated content", visibility="DoctorsOnly"))

# Delete blog
crud_sql.delete_blog(1)

# Fetch users with filters
crud_sql.fetch_users({"user_type": "Doctor"})

# Fetch blogs with author names
crud_sql.fetch_blogs_with_authors()

# Insert comment
crud_sql.insert_comment(CommentCreate(blog_id=1, user_id=2, content="This is a comment!", is_hidden=False))

# Update comment
crud_sql.update_comment(1, CommentCreate(content="Updated comment!", is_hidden=False))

# Delete comment
crud_sql.delete_comment(1)

# Insert admin action
crud_sql.insert_admin_action(AdminActionRequest(admin_id=1, target_user_id=2, action_type="BanUser", reason="Spam account"))

# Insert login history
crud_sql.insert_login_history(LoginHistoryResponse(user_id=1, ip_address="192.168.1.1", user_agent="Chrome", is_success=True, failure_reason=None))