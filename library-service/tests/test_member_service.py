from datetime import date
from unittest.mock import MagicMock

import pytest

from app.models.member import Member
from app.services.member import MemberService


@pytest.fixture
def members():
    return MagicMock()


@pytest.fixture
def loans():
    return MagicMock()


@pytest.fixture
def service(members, loans):
    return MemberService(members, loans)


def _member(**kwargs) -> Member:
    member = Member(
        name=kwargs.get("name", "Ada Lovelace"),
        email=kwargs.get("email", "ada@example.com"),
        membership_start_date=kwargs.get("membership_start_date", date(2024, 1, 1)),
        membership_end_date=kwargs.get("membership_end_date"),
        phone=kwargs.get("phone"),
        address=kwargs.get("address"),
    )
    member.id = kwargs.get("id", 1)
    return member


class TestCreateFailures:
    @pytest.mark.parametrize(
        "overrides,match",
        [
            ({"name": "  "}, "name is required"),
            ({"email": ""}, "email is required"),
            ({"email": "not-an-email"}, "email is invalid"),
            ({"membership_start_date": "  "}, "membership_start_date is required"),
            ({"membership_start_date": "01-01-2024"}, "YYYY-MM-DD"),
            (
                {"membership_end_date": "2023-01-01"},
                "membership_end_date must be on or after start date",
            ),
        ],
    )
    def test_validation(self, service, members, overrides, match):
        members.get_by_email.return_value = None
        args = {
            "name": "Ada",
            "email": "ada@example.com",
            "membership_start_date": "2024-01-01",
            **overrides,
        }
        with pytest.raises(ValueError, match=match):
            service.create(**args)
        members.add.assert_not_called()

    def test_duplicate_email(self, service, members):
        members.get_by_email.return_value = _member()
        with pytest.raises(ValueError, match="email already exists"):
            service.create(
                name="Ada",
                email="ada@example.com",
                membership_start_date="2024-01-01",
            )
        members.add.assert_not_called()


class TestGetFailures:
    def test_non_positive_id(self, service, members):
        with pytest.raises(ValueError, match="positive integer"):
            service.get(0)
        members.get_by_id.assert_not_called()


class TestUpdateFailures:
    def test_non_positive_id(self, service, members):
        with pytest.raises(ValueError, match="positive integer"):
            service.update(
                0,
                name="Ada",
                email="ada@example.com",
                membership_start_date="2024-01-01",
            )

    @pytest.mark.parametrize(
        "overrides,match",
        [
            ({"name": ""}, "name is required"),
            ({"email": "  "}, "email is required"),
            (
                {"membership_end_date": "2023-01-01"},
                "membership_end_date must be on or after start date",
            ),
        ],
    )
    def test_validation(self, service, members, overrides, match):
        members.get_by_id.return_value = _member()
        members.get_by_email.return_value = None
        args = {
            "name": "Ada",
            "email": "ada@example.com",
            "membership_start_date": "2024-01-01",
            **overrides,
        }
        with pytest.raises(ValueError, match=match):
            service.update(1, **args)

    def test_duplicate_email(self, service, members):
        members.get_by_id.return_value = _member(id=1, email="ada@example.com")
        members.get_by_email.return_value = _member(id=2, email="other@example.com")
        with pytest.raises(ValueError, match="email already exists"):
            service.update(
                1,
                name="Ada",
                email="other@example.com",
                membership_start_date="2024-01-01",
            )


class TestDeleteFailures:
    def test_non_positive_id(self, service, members):
        with pytest.raises(ValueError, match="positive integer"):
            service.delete(-1)
        members.get_by_id.assert_not_called()

    def test_active_loans(self, service, members, loans):
        members.get_by_id.return_value = _member()
        loans.count_active_for_member.return_value = 1
        with pytest.raises(ValueError, match="active loans"):
            service.delete(1)
        members.delete.assert_not_called()

    def test_soft_deletes_when_no_active_loans(self, service, members, loans):
        member = _member()
        members.get_by_id.return_value = member
        loans.count_active_for_member.return_value = 0
        service.delete(1)
        members.delete.assert_called_once_with(member)

def test_list_methods_forward_filters(service, members):
    members.list.return_value = []

    service.list(
        name_query="  ada  ",
        email_query="  ada@example.com  ",
        limit=10,
        offset=5,
    )

    members.list.assert_called_once_with(
        name_query="ada",
        email_query="ada@example.com",
        limit=10,
        offset=5,
    )
