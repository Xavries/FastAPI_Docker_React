import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY
from app.models.cleaning import CleaningCreate, CleaningInDB  


# decorate all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio  

@pytest.fixture
def new_cleaning():
    return CleaningCreate(
        name="test cleaning",
        description="test description",
        price=0.00,
        cleaning_type="spot_clean",
    )

class TestCleaningsRoutes:
    '''
    This class will be used to test that the routes associated with the Cleanings resource exist,
    and that they behave how we expect them to.
    Each class method has two parameters - app and client. Because we created fixtures in 
    conftest.py file with the same name, Pytest makes these available to any test function.

    We're asserting that we don't get a 404 response when this request is sent, and we expect this test to pass.

    The second test sends the same request, but expects the response to not include (!=, but not it is ==) a 422 status code. 
    FastAPI will return 422 status codes whenever the POST body includes an input with an invalid shape. 
    Remember how FastAPI validates all input models using Pydantic? 
    The models we write will determine the shape of the data we expect to receive. Anything else throws a 422.
    '''
    async def test_routes_exist(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("cleanings:create-cleaning"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND
    
    async def test_invalid_input_raises_error(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("cleanings:create-cleaning"), json={})
        assert res.status_code == HTTP_422_UNPROCESSABLE_ENTITY

class TestCreateCleaning:

    async def test_valid_input_creates_cleaning(
        self, app: FastAPI, client: AsyncClient, new_cleaning: CleaningCreate
    ) -> None:
        res = await client.post(
            app.url_path_for("cleanings:create-cleaning"), json={"new_cleaning": new_cleaning.dict()}
        )
        assert res.status_code == HTTP_201_CREATED
        created_cleaning = CleaningCreate(**res.json())
        assert created_cleaning == new_cleaning

    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
            (None, 422),
            ({}, 422),
            ({"name": "test_name"}, 422),
            ({"price": 10.00}, 422),
            ({"name": "test_name", "description": "test"}, 422),
        ),
    )
    async def test_invalid_input_raises_error(
        self, app: FastAPI, client: AsyncClient, invalid_payload: dict, status_code: int
    ) -> None:
        res = await client.post(
            app.url_path_for("cleanings:create-cleaning"), json={"new_cleaning": invalid_payload}
        )
        assert res.status_code == status_code


class TestGetCleaning:
    async def test_get_cleaning_by_id(self, app: FastAPI, client: AsyncClient, test_cleaning: CleaningInDB) -> None:
        res = await client.get(app.url_path_for("cleanings:get-cleaning-by-id", id=test_cleaning.id))
        assert res.status_code == HTTP_200_OK
        cleaning = CleaningInDB(**res.json())
        assert cleaning == test_cleaning
    @pytest.mark.parametrize(
        "id, status_code",
        (
            (500, 404),
            (-1, 404),
            (None, 422),
        ),
    )
    async def test_wrong_id_returns_error(
        self, app: FastAPI, client: AsyncClient, id: int, status_code: int
    ) -> None:
        res = await client.get(app.url_path_for("cleanings:get-cleaning-by-id", id=id))
        assert res.status_code == status_code
