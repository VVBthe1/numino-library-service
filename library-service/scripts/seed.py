#!/usr/bin/env python3
"""Idempotent demo seed (no extra packages). Safe to run on every boot."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.database import SessionLocal
from app.models.book import Book, Genre
from app.models.loan import Loan
from app.models.member import Member

SEED_ISBN = "9780000000001"


def main() -> None:
    db = SessionLocal()
    try:
        if db.query(Book).filter(Book.isbn == SEED_ISBN).first() is not None:
            print("seed: already applied, skipping")
            return

        now = datetime.now(timezone.utc)
        today = date.today()

        dune = Book(
            title="Dune",
            author="Frank Herbert",
            isbn=SEED_ISBN,
            genre=Genre.SCIENCE_FICTION,
            publisher="Chilton",
            publication_year=1965,
            total_quantity=2,
            description="Seed catalog title",
        )
        hobbit = Book(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            isbn="9780000000002",
            genre=Genre.FANTASY,
            publisher="Allen & Unwin",
            publication_year=1937,
            total_quantity=1,
        )
        mystery = Book(
            title="Murder on the Orient Express",
            author="Agatha Christie",
            isbn="9780000000003",
            genre=Genre.MYSTERY,
            publisher="Collins",
            publication_year=1934,
            total_quantity=1,
        )
        db.add_all([dune, hobbit, mystery])
        db.flush()

        ada = Member(
            name="Ada Lovelace",
            email="ada@example.com",
            phone="555-0100",
            membership_start_date=today - timedelta(days=30),
            membership_end_date=today + timedelta(days=335),
        )
        alan = Member(
            name="Alan Turing",
            email="alan@example.com",
            membership_start_date=today - timedelta(days=10),
            membership_end_date=today + timedelta(days=355),
        )
        db.add_all([ada, alan])
        db.flush()

        # overdue active loan (due yesterday)
        db.add(
            Loan(
                book_id=dune.id,
                member_id=ada.id,
                borrowed_at=now - timedelta(days=10),
                due_at=now - timedelta(days=1),
            )
        )
        # active loan due in the future
        db.add(
            Loan(
                book_id=hobbit.id,
                member_id=alan.id,
                borrowed_at=now - timedelta(days=2),
                due_at=now + timedelta(days=5),
            )
        )
        # returned loan (history)
        db.add(
            Loan(
                book_id=mystery.id,
                member_id=ada.id,
                borrowed_at=now - timedelta(days=20),
                due_at=now - timedelta(days=13),
                returned_at=now - timedelta(days=14),
            )
        )
        # second active loan on Dune → out of stock (qty 2, 2 active after overdue + this)
        db.add(
            Loan(
                book_id=dune.id,
                member_id=alan.id,
                borrowed_at=now - timedelta(days=3),
                due_at=now + timedelta(days=4),
            )
        )

        db.commit()
        print("seed: demo books, members, loans applied (includes overdue + out of stock)")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
