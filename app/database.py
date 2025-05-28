from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from app.config import MONGO_URI, DATABASE_NAME
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None
    @classmethod
    async def connect_to_mongodb(cls):
       
        try:
            cls.client = AsyncIOMotorClient(MONGO_URI)
            cls.db = cls.client[DATABASE_NAME]
            
            # التحقق من حالة الاتصال
            await cls.client.admin.command('ping')
            
            logger.info(f"sucssesfuly connections with database {DATABASE_NAME}")
            return cls.db
            
        except ConnectionFailure:
            logger.error("the connection with MongoDB faild")
            raise
    
    @classmethod
    async def close_mongodb_connection(cls):

        if cls.client is not None:
            cls.client.close()
            logger.info("تم إغلاق الاتصال بقاعدة البيانات")
            cls.client = None
            cls.db = None


async def get_collection(collection_name):
   
    if Database.db is None:
        await Database.connect_to_mongodb()
    
    return Database.db[collection_name]
