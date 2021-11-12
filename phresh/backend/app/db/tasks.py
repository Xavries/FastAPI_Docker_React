from fastapi import FastAPI
from databases import Database
from app.core.config import DATABASE_URL
import logging, os
'''
In the connect_to_db function we're using the databases package to establish a connection to 
our postgresql db with the database url string we configured in our core/config.py file. 
If we have an environment variable corresponding to the suffix we want placed at the end of the url, 
we concatenate it (Example: turn postgres into postgres_test). If os.environ has no DB_SUFFIX, 
then we default to an empty string. 
This helps us use the testing database for our testing session, and our regular database otherwise.
'''

logger = logging.getLogger(__name__)

async def connect_to_db(app: FastAPI) -> None:
    DB_URL = f"{DATABASE_URL}_test" if os.environ.get("TESTING") else DATABASE_URL
    database = Database(DATABASE_URL, min_size=2, max_size=10)  # these can be configured in config as well
    
    try:
        await database.connect()
        app.state._db = database
    except Exception as e:
        logger.warn("--- DB CONNECTION ERROR ---")
        logger.warn(e)
        logger.warn("--- DB CONNECTION ERROR ---")

async def close_db_connection(app: FastAPI) -> None:
    try:
        await app.state._db.disconnect()
    except Exception as e:
        logger.warn("--- DB DISCONNECT ERROR ---")
        logger.warn(e)
        logger.warn("--- DB DISCONNECT ERROR ---")