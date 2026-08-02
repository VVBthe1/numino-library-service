import { AuthProvider } from "@/auth";
import "./globals.css";

export const metadata = {
  title: "Neighborhood Library",
  description: "Staff console",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
