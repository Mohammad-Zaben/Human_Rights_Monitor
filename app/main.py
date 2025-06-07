from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.database import Database
from app.routes import users, auth ,cases, evidence, victim_witness

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="HRM API",
    description="Human Resource Management API",
    version="0.1.0"
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await Database.connect_to_mongodb()
    logger.info("the application has started and connected to the database")

@app.on_event("shutdown")
async def shutdown_db_client():
    await Database.close_mongodb_connection()
    logger.info("the database is shutdown")

@app.get("/")
async def root():
    return {"message": "welcome in the landing page, to sho the documantation , please visit /docs or /redoc"}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(cases.router)
app.include_router(victim_witness.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)