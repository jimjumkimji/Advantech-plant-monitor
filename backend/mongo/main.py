import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sample_mflix")

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

    @classmethod
    async def connect_to_mongo(cls):
        """Connect to MongoDB Atlas"""
        try:
            if not MONGODB_URL:
                raise ValueError("MONGODB_URL environment variable is not set")
            
            cls.client = AsyncIOMotorClient(MONGODB_URL)
            cls.database = cls.client[DATABASE_NAME]
            
            # Test connection
            await cls.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB Atlas!")
            
            return cls.database
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during MongoDB connection: {e}")
            raise

    @classmethod
    async def close_mongo_connection(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("✅ MongoDB connection closed.")

    @classmethod
    async def get_database(cls):
        """Get database instance"""
        if cls.database is None:
            await cls.connect_to_mongo()
        return cls.database

    @classmethod
    async def get_collection(cls, collection_name: str):
        """Get specific collection"""
        database = await cls.get_database()
        return database[collection_name]

    @classmethod
    async def check_connection(cls):
        """Check if connection is alive"""
        try:
            if cls.client:
                await cls.client.admin.command('ping')
                return True
            return False
        except Exception:
            return False

# Create global instance
mongodb = MongoDB()