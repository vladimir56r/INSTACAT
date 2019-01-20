import sqlite3

CONN = sqlite3.connect('data.db')
CURSOR = CONN.cursor()
COMMIT_COUNT = 5

create_tables_sql = ['''
    create table if not exists posts
    (id INTEGER PRIMARY KEY AUTOINCREMENT not null,
     filename text,
     description text,
     posted bool
    );''',
    '''
    create table if not exists users
    (id INTEGER PRIMARY KEY AUTOINCREMENT not null,
     name text,
     uid text
    );
    '''
   ]
   
for sql_op in create_tables_sql:
    CURSOR.execute(sql_op)

def set_posted(id, posted=True):
    UPDATE_IS_POSTED_PHOTO_BY_ID = 'update posts set posted = :posted where id = :id'
    ans = CURSOR.execute(UPDATE_IS_POSTED_PHOTO_BY_ID, {"posted":posted, "id":id})
    return ans

def add_post(photo_filename, description):
    if check_exists_post(photo_filename, description):
        return False
    INSERT_NEW_POST = 'insert into posts(filename, description, posted) values(:photo_filename, :description, 0)'
    ans = CURSOR.execute(INSERT_NEW_POST, {"photo_filename": photo_filename, "description": description})
    return True

def check_exists_post(photo_filename, description):
    SELECT_BY_POST_DATA = 'select id from posts where filename == :filename and description == :description'
    ans = CURSOR.execute(SELECT_BY_POST_DATA, {"filename":photo_filename, "description":description}).fetchone()
    exists = ans is not None
    return exists

def get_random_posts(k=None):
    SELECT_NOT_USED_POSTS = 'select id,filename,description  from posts ORDER BY RANDOM()'
    SELECT_NOT_USED_POSTS_WITH_LIMIT = 'select id,filename,description from posts ORDER BY RANDOM() limit {}'
    if k:
        query = SELECT_NOT_USED_POSTS_WITH_LIMIT.format(k)
    else:
        query = SELECT_NOT_USED_POSTS
    return CURSOR.execute(query).fetchall()

def get_not_posted_posts(k=None):
    SELECT_NOT_USED_POSTS = 'select id,filename,description from posts where posted == 0 ORDER BY RANDOM()'
    SELECT_NOT_USED_POSTS_WITH_LIMIT = 'select id,filename,description from posts where posted == 0 ORDER BY RANDOM() limit {}'
    if k:
        query = SELECT_NOT_USED_POSTS_WITH_LIMIT.format(k)
    else:
        query = SELECT_NOT_USED_POSTS
    return CURSOR.execute(query).fetchall()

def add_user(name, uid):
    if check_exists_user(name, uid):
        return False
    ADD_NEW_USER = 'insert into users(name, uid) values(:name, :uid)'
    ans = CURSOR.execute(ADD_NEW_USER, {"name": name, "uid": uid})
    return True

def check_exists_user(name, uid):
    CHECK_USER = 'select id from users where name == :name and uid == :uid'
    ans = CURSOR.execute(CHECK_USER, {"name":name, "uid":uid}).fetchone()
    exists = ans is not None
    return exists
    
def select_users(k=None):
    SELECT_NOT_USED_POSTS = 'select * from users ORDER BY RANDOM()'
    SELECT_NOT_USED_POSTS_WITH_LIMIT = 'select * from users ORDER BY RANDOM() limit {}'
    if k:
        query = SELECT_NOT_USED_POSTS_WITH_LIMIT.format(k)
    else:
        query = SELECT_NOT_USED_POSTS
    return CURSOR.execute(query).fetchall()
    
def commit():
    CONN.commit()

def rollback():
    CONN.rollback()