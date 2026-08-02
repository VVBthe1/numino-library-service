"use client";

import { useEffect, useState } from "react";
import {
  getBookClient,
  getErrorMessage,
  getLoanClient,
  getMemberClient,
} from "@/api";
import { useAuth } from "@/auth";
import { formatTime } from "@/labels";

export default function LoansPage() {
  const { token } = useAuth();

  const [loans, setLoans] = useState([]);
  const [books, setBooks] = useState([]);
  const [members, setMembers] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const [bookId, setBookId] = useState("");
  const [memberId, setMemberId] = useState("");

  const [filterBookId, setFilterBookId] = useState("");
  const [filterMemberId, setFilterMemberId] = useState("");
  const [activeOnly, setActiveOnly] = useState(true);

  async function loadLoans() {
    setError("");
    try {
      const req = {
        pageSize: 100,
        pageToken: "",
      };
      if (filterBookId) {
        req.bookId = Number(filterBookId);
      }
      if (filterMemberId) {
        req.memberId = Number(filterMemberId);
      }
      if (activeOnly) {
        req.activeOnly = true;
      }
      const result = await getLoanClient(token).listLoans(req);
      setLoans(result.response.loans);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function loadDropdowns() {
    try {
      const bookRes = await getBookClient(token).listBooks({
        pageSize: 100,
        pageToken: "",
      });
      const memberRes = await getMemberClient(token).listMembers({
        pageSize: 100,
        pageToken: "",
      });
      setBooks(bookRes.response.books);
      setMembers(memberRes.response.members);

      // pick first options if empty
      if (!bookId && bookRes.response.books.length > 0) {
        setBookId(String(bookRes.response.books[0].id));
      }
      if (!memberId && memberRes.response.members.length > 0) {
        setMemberId(String(memberRes.response.members[0].id));
      }
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  useEffect(() => {
    if (token) {
      loadDropdowns();
      loadLoans();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function handleBorrow(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await getLoanClient(token).borrowBook({
        bookId: Number(bookId),
        memberId: Number(memberId),
      });
      await loadLoans();
      await loadDropdowns();
    } catch (err) {
      setError(getErrorMessage(err));
    }
    setSaving(false);
  }

  async function handleReturn(loanId) {
    try {
      await getLoanClient(token).returnBook({ loanId: loanId });
      await loadLoans();
      await loadDropdowns();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  function applyFilters(e) {
    e.preventDefault();
    loadLoans();
  }

  return (
    <section className="stack">
      <div className="section-head">
        <h1>Loans</h1>
        <p>Borrow / return books</p>
      </div>

      {error ? <p className="error">{error}</p> : null}

      <form className="panel form-grid" onSubmit={handleBorrow}>
        <h2>Borrow</h2>
        <label>
          Book
          <select
            value={bookId}
            onChange={(e) => setBookId(e.target.value)}
            required
          >
            <option value="">Select book</option>
            {books.map((b) => (
              <option key={b.id} value={b.id}>
                #{b.id} {b.title} (avail {b.availableQuantity})
              </option>
            ))}
          </select>
        </label>
        <label>
          Member
          <select
            value={memberId}
            onChange={(e) => setMemberId(e.target.value)}
            required
          >
            <option value="">Select member</option>
            {members.map((m) => (
              <option key={m.id} value={m.id}>
                #{m.id} {m.name}
              </option>
            ))}
          </select>
        </label>
        <div className="actions span-2">
          <button className="btn primary" type="submit" disabled={saving}>
            {saving ? "Working..." : "Borrow"}
          </button>
        </div>
      </form>

      <form className="panel form-grid" onSubmit={applyFilters}>
        <h2>Filters</h2>
        <label>
          Book id
          <input
            type="number"
            value={filterBookId}
            onChange={(e) => setFilterBookId(e.target.value)}
          />
        </label>
        <label>
          Member id
          <input
            type="number"
            value={filterMemberId}
            onChange={(e) => setFilterMemberId(e.target.value)}
          />
        </label>
        <label className="inline-check span-2">
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(e) => setActiveOnly(e.target.checked)}
          />
          Active only
        </label>
        <div className="actions span-2">
          <button className="btn primary" type="submit">
            Apply
          </button>
        </div>
      </form>

      <div className="panel">
        <div className="table-head">
          <h2>Loan list</h2>
          <button type="button" className="btn ghost" onClick={loadLoans}>
            Refresh
          </button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Book</th>
                <th>Member</th>
                <th>Borrowed</th>
                <th>Due</th>
                <th>Returned</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {loans.length === 0 ? (
                <tr>
                  <td colSpan={7}>No loans</td>
                </tr>
              ) : (
                loans.map((row) => (
                  <tr key={row.loan.id}>
                    <td>{row.loan.id}</td>
                    <td>
                      #{row.book.id} {row.book.title}
                    </td>
                    <td>
                      #{row.member.id} {row.member.name}
                    </td>
                    <td>{formatTime(row.loan.borrowedAt)}</td>
                    <td>{formatTime(row.loan.dueAt)}</td>
                    <td>
                      {row.loan.returnedAt
                        ? formatTime(row.loan.returnedAt)
                        : "-"}
                    </td>
                    <td>
                      {!row.loan.returnedAt ? (
                        <button
                          type="button"
                          className="btn primary"
                          onClick={() => handleReturn(row.loan.id)}
                        >
                          Return
                        </button>
                      ) : null}
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
