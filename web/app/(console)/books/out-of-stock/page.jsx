"use client";

import { useEffect, useState } from "react";
import { getBookClient, getErrorMessage } from "@/api";
import { useAuth } from "@/auth";
import { PaginationBar } from "@/components/PaginationBar";
import { GENRES, getGenreLabel } from "@/labels";

export default function OutOfStockPage() {
  const { token } = useAuth();
  const [books, setBooks] = useState([]);
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
      const result = await getBookClient(token).getOutOfStockBooks(req);
      setBooks(result.response.books);
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
        <h1>Out of stock</h1>
        <p>Books with 0 available copies</p>
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
                <th>ID</th>
                <th>Title</th>
                <th>Author</th>
                <th>Genre</th>
                <th>Total</th>
                <th>Avail</th>
              </tr>
            </thead>
            <tbody>
              {books.length === 0 ? (
                <tr>
                  <td colSpan={6}>None</td>
                </tr>
              ) : (
                books.map((b) => (
                  <tr key={b.id}>
                    <td>{b.id}</td>
                    <td>{b.title}</td>
                    <td>{b.author}</td>
                    <td>{getGenreLabel(b.genre)}</td>
                    <td>{b.totalQuantity}</td>
                    <td>{b.availableQuantity}</td>
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
