# https://www.perplexity.ai/search/about-fastapi-blog-table-updat-ABVufJPeQTGE__SMemTIxQ

# events.py
from app.db.models import Blog
from sqlalchemy import event, func  # Import func here
from sqlalchemy.orm import Session, object_session  # Use object_session instead of Session

@event.listens_for(Blog, 'before_update')
def update_updated_at_before_update(mapper, connection, target):
    # Use object_session() to get the session for the target object
    session = object_session(target)
    
    if session and session.is_modified(target, include_collections=False):
        # Use SQLAlchemy's inspect() to check for changes
        from sqlalchemy import inspect
        insp = inspect(target)
        
        # Define fields that should trigger updated_at
        trigger_fields = {'content', 'title', 'tags'}
        
        # Check if any trigger fields have changed
        if any(insp.attrs[field].history.has_changes() for field in trigger_fields):
            target.updated_at = func.now()  # Use func.now() for timestamp
