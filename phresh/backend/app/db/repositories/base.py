'''
BaseRepository will be a simple class needed only to keep a reference to our database connection. 
In the future we can add functionality for common db actions.
'''

from databases import Database


class BaseRepository:
    def __init__(self, db: Database) -> None:
        self.db = db