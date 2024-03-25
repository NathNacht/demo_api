from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import os

# Set port to the env variable PORT to make it easy to choose the port on the server
# If the Port env variable is not set, use port 8000
PORT = os.environ.get("PORT", 8000)
app = FastAPI(port=PORT)


# @app.get("/")
# async def root():
#     """Route that return 'Alive!' if the server runs."""
#     return {"Status": "Alive!"}


# @app.get("/hello")
# async def say_hello(user: str = "Anonymous"):
#     """Route that will return 'hello {user}'."""
#     return {"Message": f"Hello {user}!"}

user_db = {
    'user1': {'username': 'user1', 'date_joined': '2020-01-01', 'location': 'location1', 'age': 20},
    'user2': {'username': 'user2', 'date_joined': '2020-02-01', 'location': 'location2', 'age': 21},
    'user3': {'username': 'user3', 'date_joined': '2020-03-01', 'location': 'location3', 'age': 22}    
}

class User(BaseModel):
    # data validation
    username: str = Field(min_length=3, max_length=20)
    date_joined: date 
    location: Optional[str] = None
    # optional age field, but if it is filled it must be between 5 and 130
    age: int = Field(None, gt=5, lt=130)  

class UserUpdate(User):
    # making date_joined optional
    date_joined: Optional[date] = None
    age: int = Field(None, gt=5, lt=200)

def ensure_user_exists(username: str):
    if username not in user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User {username} not found')


app = FastAPI()

@app.get('/users')
def get_users_query(limit: int = 20):
    # with limit as a core parameter
    # set to 2 by default (to make the limit parameter optional)
    user_list = list(user_db.values())
    return user_list[:limit]

@app.get('/users/{username}')
#path parameter is always mandatory
def get_users_path(username: str):
    ensure_user_exists(username)
    return user_db[username]


@app.post('/users')
def create_user(user: User):
    username = user.username
    if username in user_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'Can not create user. User {username} already exists')
    # if above is executed, then below is never executed
    user_db[username] = user.dict()
    return {'message': f'Successfully created user: {username}'}

@app.delete('/users/{username}')
def delete_user(username: str):
    ensure_user_exists(username)
    del user_db[username]
    return {'message': f'Successfully deleted user: {username}'}

@app.put('/users/')
def update_user(user: User):
    # update all fields (if not all fields are filled then they will be set to None)
    ensure_user_exists(user.username)
    username = user.username
    user_db[username] = user.dict()
    return {'message': f'Successfully updated user: {username}'}

@app.patch('/users/')
def partial_update_user(user: UserUpdate):
    # update only the fields that are not None
    ensure_user_exists(user.username)
    username = user.username
    user_db[username].update(user.dict(exclude_unset=True))
    return {'message': f'Successfully updated user: {username}'}