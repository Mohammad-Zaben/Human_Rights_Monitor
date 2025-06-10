import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv( "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "HRM")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "2612d2f66bfe9a9c4a0ed25be92a29f7") 
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
