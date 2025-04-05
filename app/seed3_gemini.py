from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database import SessionLocal
import app.models as models
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

def generate_fake_data():
    db: Session = SessionLocal()

    # Helper function for creating users
    def create_user():
        return models.User(
            email=fake.email(),
            password_hash=fake.password(length=12),
            user_type=fake.random_element(elements=("general", "od", "md", "admin"))[:20],
            auth_method=fake.random_element(elements=("traditional", "google"))[:20],
            name=fake.name(),
            picture=fake.image_url(),
            phone_number=fake.phone_number()[:20],
            address=fake.address(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
            last_login=fake.date_time_this_year(),
            profile_picture=fake.image_url(),
            bio=fake.text(max_nb_chars=200),
            social_media_links={
                "facebook": fake.url(),
                "twitter": fake.url(),
                "linkedin": fake.url(),
            },
            preferences={"theme": fake.random_element(elements=("light", "dark")), "notifications": fake.boolean()},
            verification_status=fake.random_element(elements=("pending", "verified", "rejected")),
            language=fake.random_element(elements=("en", "es", "fr")),
            timezone=fake.timezone(),
            location=fake.city(),
            deleted_at=None if random.random() > 0.1 else fake.date_time_this_year(), # 10% chance of being soft-deleted
        )

    # Helper function for creating blogs
    # See https://gemini.google.com/gem/coding-partner/d6794c28c9739883
    # will show you how to get keywords, excerpt
    def create_blog(author_id):
        return models.Blog(
            title=fake.sentence(nb_words=6),
            content=fake.paragraph(nb_sentences=10),
            author_id=author_id,
            visibility=fake.random_element(elements=("public", "doctor")),
            tags=[fake.word() for _ in range(random.randint(1, 5))],
            cover_image=fake.image_url(),
            excerpt=fake.text(max_nb_chars=100),
            estimated_reading_time=random.randint(1, 15),
            scheduled_publication_date=fake.future_datetime(),
            category=fake.word(),
            meta_title=fake.sentence(nb_words=8),
            meta_description=fake.paragraph(nb_sentences=2),
            keywords=", ".join(fake.words(nb=5)),
            slug=fake.slug(),
            allow_comments=fake.boolean(),
            original_source=fake.url() if random.random() < 0.2 else None,  # 20% chance of having an original source
            language=fake.random_element(elements=("en", "es", "fr")),
            deleted_at=None if random.random() > 0.1 else fake.date_time_this_year(), # 10% chance of being soft-deleted
        )

    # Helper function for creating comments
    def create_comment(blog_id, user_id):
        return models.Comment(
            blog_id=blog_id,
            user_id=user_id,
            content=fake.paragraph(nb_sentences=3),
            parent_comment_id=None if random.random() > 0.3 else random.randint(1, 50),  # 30% chance of being a reply
            rating=random.randint(1, 5) if random.random() < 0.5 else None, # 50% chance of having a rating
            edited_at=fake.date_time_this_year() if random.random() < 0.2 else None, # 20% chance of being edited
            likes=random.randint(0, 100),
            dislikes=random.randint(0, 50),
            report_count=random.randint(0, 10),
            deleted_at=None if random.random() > 0.1 else fake.date_time_this_year(), # 10% chance of being soft-deleted
        )

    def create_admin_action(admin_id, target_user_id=None, target_blog_id=None, target_comment_id=None):
      target_type = random.choice([ "user", "blog", "comment", None])
      if target_type == "user":
          target_user_id = random.choice(user_ids)
      elif target_type == "blog":
          target_blog_id = random.choice(blog_ids)
      elif target_type == "comment":
          target_comment_id = random.choice(comment_ids)
      return models.AdminAction(
            admin_id=admin_id,
            target_user_id=target_user_id,
            target_blog_id=target_blog_id,
            target_comment_id=target_comment_id,
            action_type=fake.random_element(elements=("ban", "hide", "delete", "update", "other")),
            reason=fake.text(max_nb_chars=200),
            ip_address=fake.ipv4(),
            user_agent=fake.user_agent(),
            action_details={"details": fake.paragraph(nb_sentences=2)},
            affected_resource_type= target_type,
            previous_state={"state": fake.paragraph(nb_sentences=1)}

        )

    def create_login_history(user_id):
        return models.LoginHistory(
            user_id=user_id,
            login_timestamp=fake.date_time_this_year(),
            ip_address=fake.ipv4(),
            user_agent=fake.user_agent(),
            is_success=fake.boolean(),
            failure_reason=fake.text(max_nb_chars=50) if not fake.boolean() else None,
            device_id=fake.uuid4(),
            location=fake.country(),
            two_factor_auth_used=fake.boolean(),
            os=fake.random_element(elements=("Windows", "macOS", "Linux")),
            browser=fake.random_element(elements=("Chrome", "Firefox", "Safari")),
        )

    # Seed users
    users = [create_user() for _ in range(10)]
    db.add_all(users)
    db.commit()
    user_ids = [user.user_id for user in users] # get the user ids

    # Seed blogs
    blogs = [create_blog(author_id) for author_id in user_ids[:5] for _ in range(3)]  # Limit authors to first 5 users
    db.add_all(blogs)
    db.commit()
    blog_ids = [blog.blog_id for blog in blogs] # get blog ids

    # Seed comments
    comments = [create_comment(random.choice(blog_ids), random.choice(user_ids)) for _ in range(50)]
    db.add_all(comments)
    db.commit()
    comment_ids = [comment.comment_id for comment in comments]

     # Seed admin actions
    admin_actions = [create_admin_action(random.choice(user_ids[:3])) for _ in range(20)] # limit to first 3 users
    db.add_all(admin_actions)
    db.commit()

    # Seed login history
    login_histories = [create_login_history(user_id) for user_id in user_ids for _ in range(random.randint(1, 3))]  # Each user logs in 1-3 times
    db.add_all(login_histories)
    db.commit()

    db.close()

if __name__ == "__main__":
    generate_fake_data()
    print("Fake data generated successfully!")
