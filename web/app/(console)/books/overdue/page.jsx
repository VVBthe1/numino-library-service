"use client";

import { useEffect, useState } from "react";
import { getBookClient, getErrorMessage } from "@/api";
import { useAuth } from "@/auth";
import { PaginationBar } from "@/components/PaginationBar";
import { GENRES, formatTime } from "@/labels";

export default function OverduePage() {
  const { token } = useAuth();
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [publisher, setPublisher] = useState("");
  const [genre, setGenre] = useState("");
  const [pageSize, setPageSize] = useState(20);
  const [pageToken, setPageToken] = useState("");
  const [nextToken, setNextToken] = useState("");
  const [prevTokens, setPrevTokens] = useState([]);

  async function loadData(opts) {
    const size = opts && opts.pageSize != null ? opts.pageSize : pageSize;
    const tokenPage =
      opts && opts.pageToken != null ? opts.pageToken : pageToken;
    setError("");
    try {
      const req = {
        pageSize: size,
        pageToken: tokenPage || "",
      };
      if (publisher) req.publisher = publisher;
      if (genre) req.genre = Number(genre);
      const result = await getBookClient(token).getOverdueBooks(req);
      setRows(result.response.books);
      setNextToken(result.response.nextPageToken || "");
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  function resetPageAndLoad(size) {
    setPageToken("");
    setPrevTokens([]);
    setNextToken("");
    loadData({ pageToken: "", pageSize: size != null ? size : pageSize });
  }

  useEffect(() => {
    if (token) resetPageAndLoad();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  function onFilter(e) {
    e.preventDefault();
    resetPageAndLoad();
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
            maxLength={255}
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
          <button type="button" className="btn ghost" onClick={() => loadData()}>
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
        <PaginationBar
          pageSize={pageSize}
          onPageSizeChange={(size) => {
            setPageSize(size);
            resetPageAndLoad(size);
          }}
          canPrev={prevTokens.length > 0}
          canNext={Boolean(nextToken)}
          onPrev={() => {
            const stack = prevTokens.slice();
            const prev = stack.pop() || "";
            setPrevTokens(stack);
            setPageToken(prev);
            loadData({ pageToken: prev });
          }}
          onNext={() => {
            setPrevTokens(prevTokens.concat([pageToken]));
            setPageToken(nextToken);
            loadData({ pageToken: nextToken });
          }}
        />
      </div>
    </section>
  );
}
