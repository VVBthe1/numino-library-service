"use client";

import { createContext, useContext, useState } from "react";
import { getAuthClient, getErrorMessage } from "@/api";

const AuthContext = createContext(null);

const TOKEN_KEY = "library_jwt";

export function AuthProvider({ children }) {
  // try to restore token after refresh
  const [token, setToken] = useState(() => {
    if (typeof window === "undefined") {
      return null;
    }
    return sessionStorage.getItem(TOKEN_KEY);
  });

  async function login(username, password) {
    try {
      const client = getAuthClient();
      const result = await client.login({
        username: username,
        password: password,
      });
      const accessToken = result.response.accessToken;
      if (!accessToken) {
        throw new Error("Login failed");
      }
      sessionStorage.setItem(TOKEN_KEY, accessToken);
      setToken(accessToken);
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }

  function logout() {
    sessionStorage.removeItem(TOKEN_KEY);
    setToken(null);
  }

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return value;
}
