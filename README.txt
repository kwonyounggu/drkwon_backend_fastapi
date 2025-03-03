1. create myproject
2. cd myproject
3. python3 -m venv .venv
4. source .venv/bin/activate
5. deactivate //be out of virtual environment
6. pip3 install fastapi uvicorn
//0.0.0.0: Allows external access to the server.
//8000: Port FastAPI runs on 
7. uvicorn main:app --host 0.0.0.0 --port 8000 //run fastapi framework, Keep the terminal open
8. screen uvicorn main:app --host 0.0.0.0 --port 8000 //run it in the background with screen, (Press CTRL + A + D to detach from the screen.)
9. packages to be installed
   pip3 install python-jose google-auth requests 
   pip install python-dotenv httpx
   pip3 install passlib or bcrypt for hash passwords before storing them in database
   pip install SQLAlchemy psycopg2

   pip install fastapi uvicorn python-dotenv httpx python-jose google-auth requests passlib SQLAlchemy psycopg2 email-validator
10. user_info
   {'sub': '111690490420336860549', 'name': 'Younggu Kwon', 'given_name': 'Younggu', 'family_name': 'Kwon', 'picture': 'https://lh3.googleusercontent.com/a/ACg8ocJVD85XO3ajf-ehCz7XrdBJ9OhPUnU7gkyL-Z-hwzNzb-cwGw=s96-c', 'email': 'kwon.younggu@gmail.com', 'email_verified': True}

11. # Run your API:
# uvicorn app.main:app --reload
curl -X 'POST' 'http://localhost:8000/users/' \
 -H 'Content-Type: application/json' \
 -d '{"email": "test@example.com", "user_type": "General", "auth_method": "Traditional"}'

#to create tables at the first time
#in virtual path of a terminal
>python
python>from app.database import engine
python>from app.models import Base

#the following will create tables in the connected eye_care database 
Base.metadata.create_all(bind=engine)