"use client";

import { useEffect, useState } from "react";
import { getBookClient, getErrorMessage } from "@/api";
import { useAuth } from "@/auth";
import { GENRES, getGenreLabel } from "@/labels";

export default function BooksPage() {
  const { token } = useAuth();

  const [books, setBooks] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  // form fields
  const [editId, setEditId] = useState(null);
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [isbn, setIsbn] = useState("");
  const [genre, setGenre] = useState(1);
  const [totalQuantity, setTotalQuantity] = useState(1);
  const [publicationYear, setPublicationYear] = useState("");
  const [publisher, setPublisher] = useState("");
  const [description, setDescription] = useState("");

  // filters
  const [titleQuery, setTitleQuery] = useState("");
  const [authorQuery, setAuthorQuery] = useState("");
  const [genreFilter, setGenreFilter] = useState("");
  const [publisherFilter, setPublisherFilter] = useState("");
  const [availableOnly, setAvailableOnly] = useState(false);

  function clearForm() {
    setEditId(null);
    setTitle("");
    setAuthor("");
    setIsbn("");
    setGenre(1);
    setTotalQuantity(1);
    setPublicationYear("");
    setPublisher("");
    setDescription("");
  }

  // isbn should be 10 or 13 digits (dashes ok)
  function checkIsbn(value) {
    const cleaned = value.replace(/[\s-]/g, "").toUpperCase();
    if (cleaned.length === 10 || cleaned.length === 13) {
      return cleaned;
    }
    return null;
  }

  async function loadBooks() {
    setError("");
    try {
      const req = {
        pageSize: 100,
        pageToken: "",
      };
      if (titleQuery) req.titleQuery = titleQuery;
      if (authorQuery) req.authorQuery = authorQuery;
      if (genreFilter) req.genre = Number(genreFilter);
      if (publisherFilter) req.publisher = publisherFilter;
      if (availableOnly) req.availableOnly = true;

      const result = await getBookClient(token).listBooks(req);
      setBooks(result.response.books);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  useEffect(() => {
    if (token) {
      loadBooks();
    }
    // only on first load / token change — filters use the Apply button
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  function startEdit(book) {
    setEditId(book.id);
    setTitle(book.title);
    setAuthor(book.author);
    setIsbn(book.isbn);
    setGenre(book.genre);
    setTotalQuantity(book.totalQuantity);
    setPublicationYear(book.publicationYear ? String(book.publicationYear) : "");
    setPublisher(book.publisher || "");
    setDescription(book.description || "");
  }

  async function handleSave(e) {
    e.preventDefault();
    const cleanIsbn = checkIsbn(isbn);
    if (!cleanIsbn) {
      setError("ISBN must be 10 or 13 characters");
      return;
    }

    setSaving(true);
    setError("");
    try {
      const data = {
        title: title,
        author: author,
        isbn: cleanIsbn,
        genre: Number(genre),
        totalQuantity: Number(totalQuantity),
      };
      if (publicationYear) {
        data.publicationYear = Number(publicationYear);
      }
      if (publisher) {
        data.publisher = publisher;
      }
      if (description) {
        data.description = description;
      }

      if (editId) {
        data.id = editId;
        await getBookClient(token).updateBook(data);
      } else {
        await getBookClient(token).createBook(data);
      }
      clearForm();
      await loadBooks();
    } catch (err) {
      setError(getErrorMessage(err));
    }
    setSaving(false);
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete book #" + id + "?")) {
      return;
    }
    try {
      await getBookClient(token).deleteBook({ id: id });
      if (editId === id) {
        clearForm();
      }
      await loadBooks();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  function applyFilters(e) {
    e.preventDefault();
    loadBooks();
  }

  async function clearFiltersAndReload() {
    setTitleQuery("");
    setAuthorQuery("");
    setGenreFilter("");
    setPublisherFilter("");
    setAvailableOnly(false);
    setError("");
    try {
      const result = await getBookClient(token).listBooks({
        pageSize: 100,
        pageToken: "",
      });
      setBooks(result.response.books);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <section className="stack">
      <div className="section-head">
        <h1>Books</h1>
        <p>Manage the catalog</p>
      </div>

      {error ? <p className="error">{error}</p> : null}

      <form className="panel form-grid" onSubmit={handleSave}>
        <h2>{editId ? "Edit book #" + editId : "Add book"}</h2>
        <label>
          Title
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </label>
        <label>
          Author
          <input
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            required
          />
        </label>
        <label>
          ISBN (10 or 13)
          <input
            value={isbn}
            onChange={(e) => setIsbn(e.target.value)}
            required
          />
        </label>
        <label>
          Genre
          <select
            value={genre}
            onChange={(e) => setGenre(Number(e.target.value))}
          >
            {GENRES.map((g) => (
              <option key={g.value} value={g.value}>
                {g.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Total copies
          <input
            type="number"
            min="0"
            value={totalQuantity}
            onChange={(e) => setTotalQuantity(e.target.value)}
            required
          />
        </label>
        <label>
          Year
          <input
            type="number"
            value={publicationYear}
            onChange={(e) => setPublicationYear(e.target.value)}
          />
        </label>
        <label>
          Publisher
          <input
            value={publisher}
            onChange={(e) => setPublisher(e.target.value)}
          />
        </label>
        <label className="span-2">
          Description
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={2}
          />
        </label>
        <div className="actions span-2">
          <button className="btn primary" type="submit" disabled={saving}>
            {saving ? "Saving..." : editId ? "Save" : "Create"}
          </button>
          {editId ? (
            <button type="button" className="btn ghost" onClick={clearForm}>
              Cancel
            </button>
          ) : null}
        </div>
      </form>

      <form className="panel form-grid" onSubmit={applyFilters}>
        <h2>Filters</h2>
        <label>
          Title
          <input
            value={titleQuery}
            onChange={(e) => setTitleQuery(e.target.value)}
          />
        </label>
        <label>
          Author
          <input
            value={authorQuery}
            onChange={(e) => setAuthorQuery(e.target.value)}
          />
        </label>
        <label>
          Genre
          <select
            value={genreFilter}
            onChange={(e) => setGenreFilter(e.target.value)}
          >
            <option value="">Any</option>
            {GENRES.map((g) => (
              <option key={g.value} value={g.value}>
                {g.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Publisher
          <input
            value={publisherFilter}
            onChange={(e) => setPublisherFilter(e.target.value)}
          />
        </label>
        <label className="inline-check span-2">
          <input
            type="checkbox"
            checked={availableOnly}
            onChange={(e) => setAvailableOnly(e.target.checked)}
          />
          Available only
        </label>
        <div className="actions span-2">
          <button className="btn primary" type="submit">
            Apply
          </button>
          <button
            type="button"
            className="btn ghost"
            onClick={clearFiltersAndReload}
          >
            Clear
          </button>
        </div>
      </form>

      <div className="panel">
        <div className="table-head">
          <h2>Catalog</h2>
          <button type="button" className="btn ghost" onClick={loadBooks}>
            Refresh
          </button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Author</th>
                <th>ISBN</th>
                <th>Genre</th>
                <th>Qty</th>
                <th>Avail</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {books.length === 0 ? (
                <tr>
                  <td colSpan={8}>No books</td>
                </tr>
              ) : (
                books.map((b) => (
                  <tr key={b.id}>
                    <td>{b.id}</td>
                    <td>{b.title}</td>
                    <td>{b.author}</td>
                    <td>{b.isbn}</td>
                    <td>{getGenreLabel(b.genre)}</td>
                    <td>{b.totalQuantity}</td>
                    <td>{b.availableQuantity}</td>
                    <td>
                      <div className="row-actions">
                        <button
                          type="button"
                          className="btn ghost"
                          onClick={() => startEdit(b)}
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          className="btn danger"
                          onClick={() => handleDelete(b.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
