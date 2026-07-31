from app.db.session import SessionLocal
from app.models.memory import Memory

db = SessionLocal()

try:
    deleted = db.query(Memory).delete()
    db.commit()
    print(f"Deleted {deleted} memories.")
finally:
    db.close()