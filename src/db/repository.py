from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.schema import Base


ModelT = TypeVar("ModelT", bound=Base)


class Repository(Generic[ModelT]):
    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        self.session.flush()
        return instance

    def get(self, instance_id: int) -> ModelT | None:
        return self.session.get(self.model, instance_id)

    def list_all(self) -> Sequence[ModelT]:
        return self.session.scalars(select(self.model)).all()

    def delete(self, instance: ModelT) -> None:
        self.session.delete(instance)
