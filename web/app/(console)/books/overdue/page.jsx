"use client";

import { useEffect, useState } from "react";
import { getBookClient, getErrorMessage } from "@/api";
import { useAuth } from "@/auth";
import { GENRES, formatTime } from "@/labels";

export default function OverduePage() {
  const { token } = useAuth();
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [publisher, setPublisher] = useState("");
  const [genre, setGenre] = useState("");

  async function loadData() {
    setError("");
    try {
      const req = {
        pageSize: 100,
        pageToken: "",
      };
      if (publisher) {
        req.publisher = publisher;
      }
      if (genre) {
        req.genre = Number(genre);
      }
      const result = await getBookClient(token).getOverdueBooks(req);
      setRows(result.response.books);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  useEffect(() => {
    if (token) {
      loadData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  function onFilter(e) {
    e.preventDefault();
    loadData();
  }

  return (
    <section className="stack">
      <div className="section-head">
        <h1>Overdue books</h1>
        <p>Books that were not returned on time</p>
      </div>

      {error ? <p className="error">{error}</p> : null}

      <form className="panel form-grid" onSubmit={onFilter}>
        <h2>Filters</h2>
        <label>
          Publisher
          <input
            value={publisher}
            onChange={(e) => setPublisher(e.target.value)}
          />
        </label>
        <label>
          Genre
          <select value={genre} onChange={(e) => setGenre(e.target.value)}>
            <option value="">Any</option>
            {GENRES.map((g) => (
              <option key={g.value} value={g.value}>
                {g.label}
              </option>
            ))}
          </select>
        </label>
        <div className="actions span-2">
          <button className="btn primary" type="submit">
            Apply
          </button>
        </div>
      </form>

      <div className="panel">
        <div className="table-head">
          <h2>Results</h2>
          <button type="button" className="btn ghost" onClick={loadData}>
            Refresh
          </button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Book</th>
                <th>ISBN</th>
                <th>Member</th>
                <th>Loan</th>
                <th>Due</th>
                <th>Borrowed</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={6}>Nothing overdue</td>
                </tr>
              ) : (
                rows.map((row) => (
                  <tr key={row.loan.id}>
                    <td>
                      #{row.book.id} {row.book.title}
                      <div className="muted">{row.book.author}</div>
                    </td>
                    <td>{row.book.isbn}</td>
                    <td>
                      #{row.member.id} {row.member.name}
                    </td>
                    <td>#{row.loan.id}</td>
                    <td>{formatTime(row.loan.dueAt)}</td>
                    <td>{formatTime(row.loan.borrowedAt)}</td>
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
