import asyncio
import sys
import logging

logging.basicConfig(level=logging.INFO)

from app.core.db import engine
from sqlmodel import Session
from app.services.ingestion.ingestion_service import run_ingestion

async def main():
    try:
        with Session(engine) as session:
            result = await run_ingestion(session=session)
            print(f"SUCCESS: {result}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
