"use client";

import { RequireAuth, Shell } from "@/components/Shell";

export default function ConsoleLayout({ children }) {
  return (
    <RequireAuth>
      <Shell>{children}</Shell>
    </RequireAuth>
  );
}
