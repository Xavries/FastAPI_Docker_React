from typing import Callable, Type
from databases import Database
from fastapi import Depends
from starlette.requests import Request
from app.db.repositories.base import BaseRepository

def get_database(request: Request) -> Database:
    return request.app.state._db

def get_repository(Repo_type: Type[BaseRepository]) -> Callable:
    '''
    In the get_repository function, we declare a single Repo_type parameter and return another function
     called get_repo. The get_repo has its own dependency - db - declared as a single parameter. 
     This is known in FastAPI as a sub-dependency and depends on the get_database function, 
     which grabs a reference to our database connection that we established in our app's startup event handler.

    The Request object comes directly from the starlette framework, and FastAPI handles passing that along for us. 

    We then pass that database reference to our CleaningsRepository and let the repo interface with 
    the postgres db as needed.
    '''
    def get_repo(db: Database = Depends(get_database)) -> Type[BaseRepository]:
        return Repo_type(db)
    return get_repo

