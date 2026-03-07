import { NextResponse, type NextRequest } from "next/server";

const PROTECTED_PREFIXES = ["/tableau-de-bord", "/dashboard"];
const AUTH_PREFIXES = ["/auth/connexion", "/auth/inscription", "/auth/mot-de-passe-oublie", "/auth/login", "/auth/register", "/auth/forgot-password"];

export function middleware(request: NextRequest) {
  const token = request.cookies.get("fiscia_access_token")?.value;
  const { pathname } = request.nextUrl;

  const isProtected = PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix));
  const isAuth = AUTH_PREFIXES.some((prefix) => pathname.startsWith(prefix));

  if (isProtected && !token) {
    const loginUrl = new URL("/auth/connexion", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (isAuth && token && !pathname.includes("mot-de-passe-oublie") && !pathname.includes("forgot-password")) {
    return NextResponse.redirect(new URL("/tableau-de-bord", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/tableau-de-bord/:path*", "/dashboard/:path*", "/auth/:path*"]
};

