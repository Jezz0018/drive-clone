import asyncio
from app.db.session import SessionLocal
from sqlalchemy import text

async def check():
    async with SessionLocal() as db:
        try:
            res = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'items'"))
            columns = [r[0] for r in res.all()]
            print(f"ITEMS COLUMNS: {columns}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(check())
