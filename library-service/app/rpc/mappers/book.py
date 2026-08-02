from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp

from app.models.book import Book, Genre
from app.models.loan import Loan
from app.models.member import Member
from app.pb import entities_pb2


def genre_from_proto(value: entities_pb2.Genre) -> Genre:
    try:
        name = entities_pb2.Genre.Name(value)
    except ValueError as exc:
        raise ValueError(f"genre not found: {int(value)}") from exc

    if name == "GENRE_UNSPECIFIED":
        raise ValueError("genre is required")

    key = name.removeprefix("GENRE_")
    try:
        return Genre[key]
    except KeyError as exc:
        raise ValueError(f"genre not found: {name}") from exc


def genre_to_proto(genre: Genre) -> entities_pb2.Genre:
    return entities_pb2.Genre.Value(f"GENRE_{genre.name}")


def datetime_to_proto(value: datetime) -> Timestamp:
    ts = Timestamp()
    ts.FromDatetime(value)
    return ts


def book_to_proto(book: Book, *, available_quantity: int) -> entities_pb2.Book:
    message = entities_pb2.Book(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        genre=genre_to_proto(book.genre),
        total_quantity=book.total_quantity,
        available_quantity=available_quantity,
        created_at=datetime_to_proto(book.created_at),
        updated_at=datetime_to_proto(book.updated_at),
    )
    if book.publication_year is not None:
        message.publication_year = book.publication_year
    if book.publisher is not None:
        message.publisher = book.publisher
    if book.description is not None:
        message.description = book.description
    return message


def book_minimal_to_proto(book: Book) -> entities_pb2.BookMinimal:
    return entities_pb2.BookMinimal(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
    )


def member_to_proto(member: Member) -> entities_pb2.Member:
    message = entities_pb2.Member(
        id=member.id,
        name=member.name,
        email=member.email,
        membership_start_date=member.membership_start_date.isoformat(),
        created_at=datetime_to_proto(member.created_at),
        updated_at=datetime_to_proto(member.updated_at),
    )
    if member.phone is not None:
        message.phone = member.phone
    if member.address is not None:
        message.address = member.address
    if member.membership_end_date is not None:
        message.membership_end_date = member.membership_end_date.isoformat()
    return message


def member_minimal_to_proto(member: Member) -> entities_pb2.MemberMinimal:
    message = entities_pb2.MemberMinimal(
        id=member.id,
        name=member.name,
        email=member.email,
    )
    if member.phone is not None:
        message.phone = member.phone
    return message


def loan_to_proto(loan: Loan) -> entities_pb2.Loan:
    message = entities_pb2.Loan(
        id=loan.id,
        book_id=loan.book_id,
        member_id=loan.member_id,
        borrowed_at=datetime_to_proto(loan.borrowed_at),
        due_at=datetime_to_proto(loan.due_at),
        created_at=datetime_to_proto(loan.created_at),
        updated_at=datetime_to_proto(loan.updated_at),
    )
    if loan.returned_at is not None:
        message.returned_at.CopyFrom(datetime_to_proto(loan.returned_at))
    return message
