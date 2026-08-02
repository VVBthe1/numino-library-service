import pytest

from app.models.book import Genre
from app.pb import entities_pb2
from app.rpc.mappers.book import genre_from_proto, genre_to_proto


def test_genre_from_proto_valid():
    assert genre_from_proto(entities_pb2.GENRE_SCIENCE_FICTION) == Genre.SCIENCE_FICTION


def test_genre_to_proto_roundtrip():
    assert genre_to_proto(Genre.NON_FICTION) == entities_pb2.GENRE_NON_FICTION
    assert genre_from_proto(entities_pb2.GENRE_NON_FICTION) == Genre.NON_FICTION


def test_genre_from_proto_unspecified():
    with pytest.raises(ValueError, match="genre is required"):
        genre_from_proto(entities_pb2.GENRE_UNSPECIFIED)


def test_genre_from_proto_unknown_value():
    with pytest.raises(ValueError, match="genre not found: 99"):
        genre_from_proto(99)
