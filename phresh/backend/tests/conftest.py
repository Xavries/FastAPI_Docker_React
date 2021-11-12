import warnings
import os
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from databases import Database
import alembic
from alembic.config import Config
from app.models.cleaning import CleaningCreate, CleaningInDB
from app.db.repositories.cleanings import CleaningsRepository

# Apply migrations at beginning and end of testing session
@pytest.fixture(scope="session")
def apply_migrations():
    '''
    We begin by defining our apply_migrations fixture that will handle migrating our database. 
    We set the scope to session so that the db persists for the duration of the testing session. 
    Though it's not a requirement, this will speed up 
    tests significantly since we don't apply and rollback our migrations for each test.
    The fixture sets the TESTING environment variable to "1", so that we can migrate 
    the testing database instead of our standard db. We'll get to that part in a minute. 
    Then it grabs our alembic migration config and runs all our migrations before yielding to allow 
    all tests to be executed. At the end we rollback our migrations and call it a day.
    '''
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    os.environ["TESTING"] = "1"
    config = Config("alembic.ini")
    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


'''
Our app and db fixtures are standard. We instantiate a new FastAPI app and grab a reference to 
the database connection in case we need it. In our client fixture, we're couping LifespanManager and
AsyncClient to provide clean testing client that can send requests to our running FastAPI application.
'''
# Create a new application for testing
@pytest.fixture
def app(apply_migrations: None) -> FastAPI:
    from app.api.server import get_application
    return  get_application()

# Grab a reference to our database when needed
@pytest.fixture
def db(app: FastAPI) -> Database:
    return app.state._db


# Make requests in our tests
@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"}
        ) as client:
            yield client


@pytest.fixture
async def test_cleaning(db: Database) -> CleaningInDB:
    cleaning_repo = CleaningsRepository(db)
    new_cleaning = CleaningCreate(
        name="fake cleaning name",
        description="fake cleaning description",
        price=9.99,
        cleaning_type="spot_clean",
    )
    return await cleaning_repo.create_cleaning(new_cleaning=new_cleaning)
