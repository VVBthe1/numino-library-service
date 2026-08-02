from __future__ import annotations

from datetime import date

from app.models.member import Member
from app.repositories.loan import LoanRepository
from app.repositories.member import MemberRepository


def _parse_date(value: str, *, field: str) -> date:
    value = value.strip()
    if not value:
        raise ValueError(f"{field} is required")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be YYYY-MM-DD") from exc


class MemberService:
    def __init__(self, members: MemberRepository, loans: LoanRepository) -> None:
        self._members = members
        self._loans = loans

    def create(
        self,
        *,
        name: str,
        email: str,
        membership_start_date: str,
        phone: str | None = None,
        address: str | None = None,
        membership_end_date: str | None = None,
    ) -> Member:
        name = name.strip()
        email = email.strip().lower()

        if not name:
            raise ValueError("name is required")
        if not email:
            raise ValueError("email is required")
        if self._members.get_by_email(email) is not None:
            raise ValueError("email already exists")

        start = _parse_date(membership_start_date, field="membership_start_date")
        end = (
            _parse_date(membership_end_date, field="membership_end_date")
            if membership_end_date
            else None
        )
        if end is not None and end < start:
            raise ValueError("membership_end_date must be on or after start date")

        member = Member(
            name=name,
            email=email,
            phone=phone.strip() if phone else None,
            address=address.strip() if address else None,
            membership_start_date=start,
            membership_end_date=end,
        )
        return self._members.add(member)

    def get(self, member_id: int) -> Member:
        if member_id <= 0:
            raise ValueError("id must be a positive integer")
        return self._members.get_by_id(member_id)

    def list(
        self,
        *,
        name_query: str | None = None,
        email_query: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Member]:
        if limit <= 0:
            raise ValueError("page_size must be a positive integer")
        return self._members.list(
            name_query=name_query.strip() if name_query else None,
            email_query=email_query.strip() if email_query else None,
            limit=limit,
            offset=offset,
        )

    def update(
        self,
        member_id: int,
        *,
        name: str,
        email: str,
        membership_start_date: str,
        phone: str | None = None,
        address: str | None = None,
        membership_end_date: str | None = None,
    ) -> Member:
        if member_id <= 0:
            raise ValueError("id must be a positive integer")

        name = name.strip()
        email = email.strip().lower()
        if not name:
            raise ValueError("name is required")
        if not email:
            raise ValueError("email is required")

        member = self._members.get_by_id(member_id)
        existing = self._members.get_by_email(email)
        if existing is not None and existing.id != member.id:
            raise ValueError("email already exists")

        start = _parse_date(membership_start_date, field="membership_start_date")
        end = (
            _parse_date(membership_end_date, field="membership_end_date")
            if membership_end_date
            else None
        )
        if end is not None and end < start:
            raise ValueError("membership_end_date must be on or after start date")

        member.name = name
        member.email = email
        member.phone = phone.strip() if phone else None
        member.address = address.strip() if address else None
        member.membership_start_date = start
        member.membership_end_date = end
        return member

    def delete(self, member_id: int) -> None:
        if member_id <= 0:
            raise ValueError("id must be a positive integer")
        member = self._members.get_by_id(member_id)
        active = self._loans.count_active_for_member(member.id)
        if active > 0:
            raise ValueError("cannot delete member with active loans")
        self._members.delete(member)
