import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User('bob', 'bob@mail.com', 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command(help="Get user by username")
def get_user(username:str):
     with get_session() as db: 
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)

@cli.command(help="Get all users that match")
def get_all_users():
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)


@cli.command(help="Change email by username")
def change_email(username: str, new_email:str):
     with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command(help="Create new user")
def create_user(username: str, email:str, password: str):
    with get_session() as db: 
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError as e:
            db.rollback() 
            print("Username or email already taken!") 
        else:
            print(newuser)

@cli.command(help="Delete user by username")
def delete_user(username: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')

@cli.command(help = "Search for user by partial match by username or email")
def search_user(quary: str = typer.Argument(..., help="Partial search for username or email")):
    with get_session() as db:
        user = db.exec(select(User).where(User.username.contins(quary) | User.email.contains(quary))).all() 
        if not user:
            print(f'No users found with {quary} in username or email')
        else:
            for user in user: 
                print(user)

@cli.command(help="List users with pagination that matches limit and offset")
def list_users(limit: int = 10, offset: int = 0):
    with get_session() as db:
        total_users = len(db.exec(select(User)).all())
        users = db.exec(select(User).offset(offset).limit(limit)).all()
        if not users:
            print("No users found")
        else:
            for user in users:
                print(user)
    

if __name__ == "__main__":
    cli()