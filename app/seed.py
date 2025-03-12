#run drkwon_backend>python -m app.seed
from sqlalchemy.orm import Session
from app.database import SessionLocal
import app.models as models

db: Session = SessionLocal()

# Seed users
test_user = models.User(
    email="test33@example.com",
    password_hash="$2b$12$somethinghashed",
    user_type="General",
    auth_method="Traditional",
    name="Test User",
    picture="https://example.com/pic.png"
)

db.add(test_user)

test_blog = models.Blog(
    title="Hello World 3py3 ",
    content="This is a test blog 3!",
    author_id=1
)

db.add(test_blog)

db.commit()

db.close()