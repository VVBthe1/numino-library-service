"use client";

import { useEffect, useState } from "react";
import { getErrorMessage, getMemberClient } from "@/api";
import { useAuth } from "@/auth";

function todayString() {
  return new Date().toISOString().slice(0, 10);
}

// default membership is 1 year
function oneYearLater(startDate) {
  const d = new Date(startDate + "T00:00:00");
  d.setFullYear(d.getFullYear() + 1);
  return d.toISOString().slice(0, 10);
}

export default function MembersPage() {
  const { token } = useAuth();

  const [members, setMembers] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const [editId, setEditId] = useState(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [startDate, setStartDate] = useState(todayString());
  const [endDate, setEndDate] = useState(oneYearLater(todayString()));

  const [nameQuery, setNameQuery] = useState("");
  const [emailQuery, setEmailQuery] = useState("");

  function clearForm() {
    setEditId(null);
    setName("");
    setEmail("");
    setPhone("");
    setAddress("");
    const start = todayString();
    setStartDate(start);
    setEndDate(oneYearLater(start));
  }

  async function loadMembers(filters) {
    setError("");
    try {
      const req = {
        pageSize: 100,
        pageToken: "",
      };
      if (filters && filters.nameQuery) {
        req.nameQuery = filters.nameQuery;
      }
      if (filters && filters.emailQuery) {
        req.emailQuery = filters.emailQuery;
      }
      const result = await getMemberClient(token).listMembers(req);
      setMembers(result.response.members);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  useEffect(() => {
    if (token) {
      loadMembers({ nameQuery: "", emailQuery: "" });
    }
  }, [token]);

  function onStartChange(value) {
    setStartDate(value);
    // keep end date as start + 1 year
    if (value) {
      setEndDate(oneYearLater(value));
    }
  }

  function startEdit(m) {
    setEditId(m.id);
    setName(m.name);
    setEmail(m.email);
    setPhone(m.phone || "");
    setAddress(m.address || "");
    setStartDate(m.membershipStartDate);
    setEndDate(m.membershipEndDate || "");
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const data = {
        name: name,
        email: email,
        membershipStartDate: startDate,
      };
      if (phone) data.phone = phone;
      if (address) data.address = address;
      if (endDate) data.membershipEndDate = endDate;

      if (editId) {
        data.id = editId;
        await getMemberClient(token).updateMember(data);
      } else {
        await getMemberClient(token).createMember(data);
      }
      clearForm();
      await loadMembers({ nameQuery: nameQuery, emailQuery: emailQuery });
    } catch (err) {
      setError(getErrorMessage(err));
    }
    setSaving(false);
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete member #" + id + "?")) {
      return;
    }
    try {
      await getMemberClient(token).deleteMember({ id: id });
      if (editId === id) {
        clearForm();
      }
      await loadMembers({ nameQuery: nameQuery, emailQuery: emailQuery });
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  function applyFilters(e) {
    e.preventDefault();
    loadMembers({ nameQuery: nameQuery, emailQuery: emailQuery });
  }

  return (
    <section className="stack">
      <div className="section-head">
        <h1>Members</h1>
        <p>Register members (membership defaults to 1 year)</p>
      </div>

      {error ? <p className="error">{error}</p> : null}

      <form className="panel form-grid" onSubmit={handleSave}>
        <h2>{editId ? "Edit member #" + editId : "Add member"}</h2>
        <label>
          Name
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </label>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>
        <label>
          Phone
          <input value={phone} onChange={(e) => setPhone(e.target.value)} />
        </label>
        <label>
          Start date
          <input
            type="date"
            value={startDate}
            onChange={(e) => onStartChange(e.target.value)}
            required
          />
        </label>
        <label>
          End date
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            required
          />
        </label>
        <label className="span-2">
          Address
          <input
            value={address}
            onChange={(e) => setAddress(e.target.value)}
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
          Name
          <input
            value={nameQuery}
            onChange={(e) => setNameQuery(e.target.value)}
          />
        </label>
        <label>
          Email
          <input
            value={emailQuery}
            onChange={(e) => setEmailQuery(e.target.value)}
          />
        </label>
        <div className="actions span-2">
          <button className="btn primary" type="submit">
            Apply
          </button>
          <button
            type="button"
            className="btn ghost"
            onClick={() => {
              setNameQuery("");
              setEmailQuery("");
              loadMembers({});
            }}
          >
            Clear
          </button>
        </div>
      </form>

      <div className="panel">
        <div className="table-head">
          <h2>Directory</h2>
          <button
            type="button"
            className="btn ghost"
            onClick={() =>
              loadMembers({ nameQuery: nameQuery, emailQuery: emailQuery })
            }
          >
            Refresh
          </button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Start</th>
                <th>End</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {members.length === 0 ? (
                <tr>
                  <td colSpan={6}>No members</td>
                </tr>
              ) : (
                members.map((m) => (
                  <tr key={m.id}>
                    <td>{m.id}</td>
                    <td>{m.name}</td>
                    <td>{m.email}</td>
                    <td>{m.membershipStartDate}</td>
                    <td>{m.membershipEndDate || "-"}</td>
                    <td>
                      <div className="row-actions">
                        <button
                          type="button"
                          className="btn ghost"
                          onClick={() => startEdit(m)}
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          className="btn danger"
                          onClick={() => handleDelete(m.id)}
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
