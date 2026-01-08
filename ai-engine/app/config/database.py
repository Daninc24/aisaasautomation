import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

# Global database client
db_client = None
database = None

async def connect_db():
    """Connect to MongoDB database"""
    global db_client, database
    
    try:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/automateiq")
        
        # Create MongoDB client
        db_client = AsyncIOMotorClient(
            mongodb_uri,
            maxPoolSize=10,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=45000,
        )
        
        # Test connection
        await db_client.admin.command('ping')
        
        # Get database name from URI or use default
        db_name = mongodb_uri.split('/')[-1].split('?')[0] if '/' in mongodb_uri else 'automateiq'
        database = db_client[db_name]
        
        logger.info(f"📦 Connected to MongoDB: {db_name}")
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

async def get_database():
    """Get database instance"""
    global database
    if database is None:
        await connect_db()
    return database

async def close_db():
    """Close database connection"""
    global db_client
    if db_client:
        db_client.close()
        logger.info("📦 MongoDB connection closed")

# Collections
async def get_documents_collection():
    """Get documents collection"""
    db = await get_database()
    return db.documents

async def get_chat_sessions_collection():
    """Get chat sessions collection"""
    db = await get_database()
    return db.chat_sessions

async def get_inventory_collection():
    """Get inventory collection"""
    db = await get_database()
    return db.inventory

async def get_content_collection():
    """Get content collection"""
    db = await get_database()
    return db.content