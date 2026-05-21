import asyncio
from app.db.session import SessionLocal
from sqlalchemy import text

async def fix():
    async with SessionLocal() as db:
        try:
            print("Updating existing items to set is_pinned = false where it is null...")
            await db.execute(text("UPDATE items SET is_pinned = false WHERE is_pinned IS NULL"))
            await db.commit()
            print("DONE.")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(fix())
