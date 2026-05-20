import asyncio
from app.db.session import SessionLocal
from sqlalchemy import text

async def check():
    async with SessionLocal() as db:
        try:
            res = await db.execute(text("SELECT id, name, is_trashed, owner_id FROM items"))
            items = res.all()
            print(f"ITEMS STATUS: {items}")
            
            res = await db.execute(text("SELECT id, email FROM users"))
            users = res.all()
            print(f"USERS: {users}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(check())
