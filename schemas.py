from pydantic import BaseModel
from typing import List, Optional

class CharacterData(BaseModel):
    id: int
    name: str
    description: str
    # Puedes agregar más campos según la documentación de la API de Marvel.

class MarvelCharacterResponse(BaseModel):
    offset: int
    limit: int
    total: int
    count: int
    results: List[CharacterData]
