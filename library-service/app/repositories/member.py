from sqlalchemy.orm import Session

from app.models.member import Member


class MemberRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, member_id: int) -> Member | None:
        raise NotImplementedError

    def get_by_email(self, email: str) -> Member | None:
        raise NotImplementedError

    def list(
        self,
        *,
        name_query: str | None = None,
        email_query: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Member]:
        raise NotImplementedError

    def add(self, member: Member) -> Member:
        raise NotImplementedError

    def delete(self, member: Member) -> None:
        raise NotImplementedError
