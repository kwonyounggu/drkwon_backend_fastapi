from sqlalchemy.orm import Session
from app.database import SessionLocal
import app.models as models
from faker import Faker

fake = Faker()

db: Session = SessionLocal()

# Seed users
for _ in range(10):
    user = models.User(
        email=fake.email(),
        password_hash=fake.password(length=12),
        user_type=fake.random_element(elements=("general", "doctor", "admin")),
        auth_method=fake.random_element(elements=("traditional", "google")),
        name=fake.name(),
        picture=fake.image_url()
    )
    db.add(user)

# Seed blogs
for author_id in range(1, 6):
    for _ in range(3):
        blog = models.Blog(
            title=fake.sentence(nb_words=6),
            content=fake.paragraph(nb_sentences=10),
            author_id=author_id,
            visibility=fake.random_element(elements=("public", "doctor"))
        )
        db.add(blog)

# Commit data to the database
db.commit()

db.close()