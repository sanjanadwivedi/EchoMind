from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model

    def create(self, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, obj_id):
        result = self.db.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalar_one_or_none()

    def get_all(self):
        result = self.db.execute(select(self.model))
        return result.scalars().all()

    def delete(self, obj_id):
        obj = self.get_by_id(obj_id)

        if obj is None:
            return False

        self.db.delete(obj)
        self.db.commit()
        return True