#run drkwon_backend>python -m app.seed
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
import app.db.models as models
from app.db.events import update_updated_at_before_update

db: Session = SessionLocal()

# Example: Update a blog's content (should trigger updated_at)
blog = db.query(models.Blog).filter(models.Blog.blog_id == 1).first()
#blog.content = "New updated content again" # type: ignore
#db.commit()  # updated_at will change

# Example: Update num_views (should NOT trigger updated_at)
blog.num_views += 1 # type: ignore
db.commit()  # updated_at remains unchanged

db.close()