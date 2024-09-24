import os
import time
import hashlib
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from database import engine, SessionLocal
from models import Character
from schemas import *
from database import *

load_dotenv()

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import models 
import schemas 

PUBLIC_KEY = os.environ["PUBLIC_KEY"]
PRIVATE_KEY = os.environ["PRIVATE_KEY"]

def generate_hash(ts, private_key, public_key):
    return hashlib.md5(f"{ts}{private_key}{public_key}".encode()).hexdigest()

async def get_marvel_characters():
    ts = str(int(time.time()))
    hash_value = generate_hash(ts, PRIVATE_KEY, PUBLIC_KEY)
    url = f"https://gateway.marvel.com/v1/public/characters?ts={ts}&apikey={PUBLIC_KEY}&hash={hash_value}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

@app.get("/characters", response_model=schemas.MarvelCharacterResponse)
async def get_characters():
    characters = await get_marvel_characters()
    return schemas.MarvelCharacterResponse(**characters['data'])

@app.post("/characters/", response_model=schemas.CharacterData)  
def create_character(character: schemas.CharacterData, db: Session = Depends(get_db)):
    db_character = models.Character(**character.dict()) 
    db.add(db_character)
    db.commit()
    db.refresh(db_character)  

# Ruta para actualizar un personaje
@app.put("/characters/{character_id}", response_model=schemas.CharacterData)
def update_character(character_id: int, character: schemas.CharacterData, db: Session = Depends(get_db)):
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    db_character.name = character.name
    db_character.description = character.description
    db.commit()
    db.refresh(db_character)
    
    return db_character

# Ruta para eliminar un personaje
@app.delete("/characters/{character_id}", response_model=schemas.CharacterData)
def delete_character(character_id: int, db: Session = Depends(get_db)):
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    db.delete(db_character)
    db.commit()
    
    return db_character

@app.get("/characters/{character_id}", response_model=schemas.CharacterData)
def read_character(character_id: int, db: Session = Depends(get_db)):
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return db_character
