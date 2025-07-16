import asyncio
from app.core.database import drop_tables, create_tables

async def reset_database():
    print("Dropping all tables...")
    await drop_tables()
    print("Creating new tables...")
    await create_tables()
    print("Database reset completed!")

if __name__ == "__main__":
    asyncio.run(reset_database())