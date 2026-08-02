from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from app.models.member import Member


class MemberRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _alive(self):
        return self._db.query(Member).filter(Member.deleted_at.is_(None))

    def get_by_id(self, member_id: int, *, with_trashed: bool = False) -> Member:
        if with_trashed:
            member = self._db.get(Member, member_id)
        else:
            member = self._alive().filter(Member.id == member_id).first()
        if member is None:
            raise NoResultFound()
        return member

    def get_by_email(self, email: str) -> Member | None:
        return self._alive().filter(Member.email == email).first()

    def list(
        self,
        *,
        name_query: str | None = None,
        email_query: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Member]:
        query = self._alive()
        if name_query:
            query = query.filter(Member.name.ilike(f"%{name_query}%"))
        if email_query:
            query = query.filter(Member.email.ilike(f"%{email_query}%"))
        return query.order_by(Member.id).offset(offset).limit(limit).all()

    def add(self, member: Member) -> Member:
        self._db.add(member)
        self._db.flush()
        self._db.refresh(member)
        return member

    def delete(self, member: Member) -> None:
        member.soft_delete()
        self._db.flush()
