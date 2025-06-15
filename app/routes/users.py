from fastapi import APIRouter, Depends, HTTPException, status
from app.models.users import UserCreate, UserInDB, Token, TokenData, UserBase
from app.auth.hashing import Hash
from app.auth.jwt import create_access_token
from app.auth.oauth import get_current_user
from app.database import get_collection
from bson import ObjectId
from typing import List, Dict, Any

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
 
    users_collection = await get_collection("users")
    
    existing_user = await users_collection.find_one({
        "$or": [
            {"username": user.username},
            {"email": user.email}
        ]
    })
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "the username or email already exists"
        )
    
    user_data = user.model_dump()
    hashed_password = Hash.bcrypt(user.password)
    
    user_data.pop("password")
    user_data["hashed_password"] = hashed_password
    
    result = await users_collection.insert_one(user_data)
    
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    
    created_user["id"] = str(created_user["_id"])
    del created_user["_id"]
    del created_user["hashed_password"]
    
    return created_user


@router.get("/me", response_model=UserBase)
async def get_current_user_info(current_user = Depends(get_current_user)):

    users_collection = await get_collection("users")
    user = await users_collection.find_one({"username": current_user.username})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["id"] = str(user["_id"])
    del user["_id"]
    del user["hashed_password"]
    
    return user


@router.get("/total_lawyers",response_model=int, summary="Get total number of lawyers")
async def get_total_lawyers_number(current_user:str= Depends(get_current_user)):
    users_collection = await get_collection("users")
    
    # Count the total number of lawyers
    total_lawyers = await users_collection.count_documents({"role": "lawyer"})
    
    return total_lawyers

@router.get("/total_organizations",response_model=int, summary="Get total number of organizations")
async def get_total_organizations_number(current_user:str= Depends(get_current_user)):
    users_collection = await get_collection("users")
    
    # Count the total number of organizations
    total_organizations = await users_collection.count_documents({"role": "organization"})
    
    return total_organizations


@router.get("/lawyer", response_model=List[UserBase],summary="Get all lawyers")
async def get_lawyers(current_user = Depends(get_current_user)) -> List[UserBase]:
    users_collection = await get_collection("users")
    
    lawyers = []
    async for user in users_collection.find({"role": "lawyer"}):
        user["id"] = str(user["_id"])
        del user["_id"]
        del user["hashed_password"]
        lawyers.append(UserBase(**user))
    
    return lawyers


@router.get("/organizations", response_model=List[UserBase],summary="Get all organizations")
async def get_lawyers(current_user = Depends(get_current_user)) -> List[UserBase]:
    users_collection = await get_collection("users")
    
    lawyers = []
    async for user in users_collection.find({"role": "organization"}):
        user["id"] = str(user["_id"])
        del user["_id"]
        del user["hashed_password"]
        lawyers.append(UserBase(**user))
    
    return lawyers