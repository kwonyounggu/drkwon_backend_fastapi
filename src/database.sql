//https://chat.deepseek.com/a/chat/s/fe39a297-5b60-4818-82f9-ebe79d7aeecc
//Stores information about all users, including doctors and general users.
//Add a IsBanned field to track if a user is banned from writing blogs or comments due to inappropriate content.
CREATE TABLE Users 
(
    UserID SERIAL PRIMARY KEY,
    Email VARCHAR(100) UNIQUE NOT NULL, -- Primary identifier
    PasswordHash VARCHAR(255), -- Optional for traditional registration
    UserType ENUM('Doctor', 'General', 'Admin') NOT NULL,
    IsBanned BOOLEAN DEFAULT FALSE,
    AuthMethod ENUM('Traditional', 'Google') NOT NULL, -- Track authentication method
    GoogleID VARCHAR(100) UNIQUE, -- Unique ID from Google OAuth
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
//think it later
//(Optional) to put user_info from google with OAuth
CREATE TABLE users 
(
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- Optional for traditional registration
    user_type VARCHAR(20) CHECK (user_type IN ('Doctor', 'General', 'Admin')) NOT NULL,
    is_banned BOOLEAN DEFAULT FALSE,
    auth_method VARCHAR(20) CHECK (auth_method IN ('Traditional', 'Google')) NOT NULL,
    google_id VARCHAR(100) UNIQUE, -- Unique ID from Google OAuth
    name VARCHAR(100), -- Store user's name from Google
    picture TEXT, -- Store profile picture URL from Google
    refresh_token VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
//Stores blog posts, including their visibility and author.
//Add an IsHidden field to hide blogs with inappropriate content.
CREATE TABLE blogs 
(
    blog_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_id INT NOT NULL, -- Foreign key to users table
    visibility VARCHAR(20) CHECK (visibility IN ('Public', 'Doctors')) NOT NULL DEFAULT 'Public',
    is_hidden BOOLEAN DEFAULT FALSE, -- Hide blog if inappropriate
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE CASCADE
);

//Stores comments made by logged-in users on blogs.
//Add an IsHidden field to hide comments with inappropriate content.
CREATE TABLE comments 
(
    comment_id SERIAL PRIMARY KEY,
    blog_id INT NOT NULL, -- Foreign key to blogs table
    user_id INT NOT NULL, -- Foreign key to users table
    content TEXT NOT NULL,
    is_hidden BOOLEAN DEFAULT FALSE, -- Hide comment if inappropriate
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (blog_id) REFERENCES blogs(blog_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

//Track admin actions (e.g., banning users, hiding blogs/comments).
CREATE TABLE admin_actions 
(
    action_id SERIAL PRIMARY KEY,
    admin_id INT NOT NULL, -- Foreign key to users table
    target_user_id INT, -- User who was banned (if applicable)
    target_blog_id INT, -- Blog that was hidden (if applicable)
    target_comment_id INT, -- Comment that was hidden (if applicable)
    action_type VARCHAR(20) CHECK (action_type IN ('BanUser', 'HideBlog', 'HideComment')) NOT NULL,
    reason TEXT, -- Reason for the action
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (target_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (target_blog_id) REFERENCES blogs(blog_id) ON DELETE CASCADE,
    FOREIGN KEY (target_comment_id) REFERENCES comments(comment_id) ON DELETE CASCADE
);
CREATE TABLE login_history 
(
    login_id SERIAL PRIMARY KEY,
    user_id INT, -- Foreign key to users table
    login_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET, -- Store the IP address of the user
    user_agent TEXT, -- Store the user agent (browser/device info)
    is_success BOOLEAN NOT NULL, -- Track if the login was successful
    failure_reason TEXT, -- Reason for failed login
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

>brew install postgresql
//brew services start postgresql

//To start postgresql@14 now and restart at login:
>brew services start postgresql@14
//Or, if you don't want/need a background service you can just run:
  /usr/local/opt/postgresql@14/bin/postgres -D /usr/local/var/postgresql@14

>brew services list //verify if the service is running

>psql postgres
#CREATE USER admin WITH PASSWORD '277277';
#CREATE DATABASE eye_care;
#GRANT ALL PRIVILEGES ON DATABASE eye_care TO admin;
\q

//connect to eye_care database
psql -d eye_care -U admin
//verify the connection
eye_care>\conninfo
eye_care>\q

//Install GUI
brew install --cask pgadmin4
brew install --cask tableplus

//stop postgresql 
brew services stop postgresql@14

//uninstall
brew uninstall postgresql@14

//remove leftover data
rm -rf /usr/local/var/postgres

################################Create tables ################################
#to create tables at the first time
#in virtual path of a terminal
>python
python>from app.database import engine
python>from app.models import Base

#the following will create tables in the connected eye_care database 
Base.metadata.create_all(bind=engine)

######### solution about app module not found ######################
#see https://chat.deepseek.com/a/chat/s/9aaa4545-0218-496b-8848-7d0b8fb5ae76
3. Run as a Module
If your script is inside app/, try running it with -m:
drkwon_backend>python -m app.seed3
This treats app.seed3 as a module and correctly resolves imports.
