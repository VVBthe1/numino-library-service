from app.models.member import Member
from app.repositories.member import MemberRepository


class MemberService:
    def __init__(self, members: MemberRepository) -> None:
        self._members = members

    def create(self, **fields) -> Member:
        raise NotImplementedError

    def get(self, member_id: int) -> Member:
        raise NotImplementedError

    def list(self, **filters) -> list[Member]:
        raise NotImplementedError

    def update(self, member_id: int, **fields) -> Member:
        raise NotImplementedError

    def delete(self, member_id: int) -> None:
        raise NotImplementedError
