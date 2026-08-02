"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/auth";

// redirect to login if not signed in
export function RequireAuth({ children }) {
  const { token } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!token) {
      router.replace("/login");
    }
  }, [token]);

  if (!token) {
    return null;
  }
  return children;
}

export function Shell({ children }) {
  const { logout } = useAuth();
  const pathname = usePathname();

  function linkClass(path) {
    if (pathname === path) {
      return "active";
    }
    return "";
  }

  function onLogout() {
    logout();
    // hard refresh so state is gone
    window.location.href = "/login";
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">NL</span>
          <div>
            <p className="brand-name">Neighborhood Library</p>
            <p className="brand-sub">Staff console</p>
          </div>
        </div>
        <nav className="nav">
          <Link className={linkClass("/books")} href="/books">
            Books
          </Link>
          <Link className={linkClass("/books/overdue")} href="/books/overdue">
            Overdue
          </Link>
          <Link
            className={linkClass("/books/out-of-stock")}
            href="/books/out-of-stock"
          >
            Out of stock
          </Link>
          <Link className={linkClass("/members")} href="/members">
            Members
          </Link>
          <Link className={linkClass("/loans")} href="/loans">
            Loans
          </Link>
        </nav>
        <button type="button" className="btn ghost" onClick={onLogout}>
          Log out
        </button>
      </header>
      <main className="page">{children}</main>
    </div>
  );
}
