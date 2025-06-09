from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.users import Token, TokenData
from app.auth.hashing import Hash
from app.auth.jwt import create_access_token
from app.database import get_collection

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    users_collection = await get_collection("users")
    user = await users_collection.find_one({"username": form_data.username})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="username or password is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not Hash.verify(user["hashed_password"], form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="password is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["username"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.get("role", "user")  # Include the user's role in the response
    }
