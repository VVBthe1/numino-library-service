import { GrpcWebFetchTransport } from "@protobuf-ts/grpcweb-transport";
import { AuthServiceClient } from "@/gen/auth.client";
import { BookServiceClient } from "@/gen/book.client";
import { LoanServiceClient } from "@/gen/loan.client";
import { MemberServiceClient } from "@/gen/member.client";

// in docker we hit the same host (nginx proxies grpc)
// for local next dev set NEXT_PUBLIC_GRPC_BASE_URL=http://localhost:8081
function getBaseUrl() {
  if (process.env.NEXT_PUBLIC_GRPC_BASE_URL) {
    return process.env.NEXT_PUBLIC_GRPC_BASE_URL.replace(/\/$/, "");
  }
  if (typeof window !== "undefined") {
    return window.location.origin;
  }
  return "http://localhost:8081";
}

function makeTransport(token) {
  const meta = {};
  if (token) {
    meta.authorization = "Bearer " + token;
  }
  return new GrpcWebFetchTransport({
    baseUrl: getBaseUrl(),
    meta: meta,
  });
}

export function getAuthClient(token) {
  return new AuthServiceClient(makeTransport(token));
}

export function getBookClient(token) {
  return new BookServiceClient(makeTransport(token));
}

export function getMemberClient(token) {
  return new MemberServiceClient(makeTransport(token));
}

export function getLoanClient(token) {
  return new LoanServiceClient(makeTransport(token));
}

// grpc errors usually have a message field
export function getErrorMessage(err) {
  if (err && err.message) {
    return err.message;
  }
  return String(err);
}
