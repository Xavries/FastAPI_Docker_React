'''
Now we're getting somewhere. We're importing our BaseRepository and a few models 
associated with the Cleaning resource. We've also written our first SQL query, 
complete with the :query_arg style that the databases package expects. 
One of the benefits of using the Repository pattern is that we get the flexibility of pure SQL, 
with the clean interface of an ORM.
'''

from app.db.repositories.base import BaseRepository
from app.models.cleaning import CleaningCreate, CleaningUpdate, CleaningInDB

CREATE_CLEANING_QUERY = """
    INSERT INTO cleanings (name, description, price, cleaning_type)
    VALUES (:name, :description, :price, :cleaning_type)
    RETURNING id, name, description, price, cleaning_type;
"""

class CleaningsRepository(BaseRepository):
    """"
    All database actions associated with the Cleaning resource.
    The CleaningsRepository inherits from our BaseRepository and 
    defines a single method meant to insert a new cleaning into our postgres database. 
    Notice how our create_cleaning method expects a new_cleaning argument that is type annotated 
    using the CleaningCreate model. 
    We first call the .dict() method on our model to convert it to a dictionary. 
    """
    async def create_cleaning(self, *, new_cleaning: CleaningCreate) -> CleaningInDB:
        query_values = new_cleaning.dict() # example: {"name": "Clean My House", "cleaning_type": "full_clean", "price": 29.99, "description": None}
        cleaning = await self.db.fetch_one(query=CREATE_CLEANING_QUERY, values=query_values)
        
        return CleaningInDB(**cleaning)