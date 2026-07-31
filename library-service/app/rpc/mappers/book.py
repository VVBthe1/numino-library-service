from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp

from app.models.book import Book, Genre
from app.pb import entities_pb2


def genre_from_proto(value: entities_pb2.Genre) -> Genre:
    name = entities_pb2.Genre.Name(value)
    if name == "GENRE_UNSPECIFIED":
        raise ValueError("genre is required")
    return Genre[name.removeprefix("GENRE_")]


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
