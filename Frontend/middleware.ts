// ============================================================
// SatyamAI – Route Protection Middleware
// 🔧 Session-based auth middleware. Swap with SSO middleware here.
// ============================================================

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Routes that don't require authentication
const PUBLIC_ROUTES = ["/login", "/api/auth/login"];

// Role hierarchy for access control
const ROLE_HIERARCHY: Record<string, number> = {
  Admin: 3,
  Analyst: 2,
  Reviewer: 1,
};

// Route access requirements
const PROTECTED_ROUTES: Record<string, string> = {
  "/users": "Admin",
  "/settings": "Admin",
  "/audit-logs": "Analyst",
};

function decodeSessionFromCookie(value: string) {
  try {
    const payload = JSON.parse(atob(value));
    if (payload.expiresAt < Date.now()) return null;
    return payload;
  } catch {
    return null;
  }
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public routes
  if (PUBLIC_ROUTES.some((route) => pathname.startsWith(route))) {
    return NextResponse.next();
  }

  // Allow API routes except protected ones
  if (pathname.startsWith("/api/") && !pathname.startsWith("/api/auth/users")) {
    return NextResponse.next();
  }

  // Authentication is now handled client-side using JWT stored in localStorage.
  // Middleware no longer enforces cookie sessions.

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
