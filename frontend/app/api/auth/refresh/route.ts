import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_BASE_URL = process.env.FISCIA_API_URL ?? "http://localhost:8000";

export async function POST(request: Request) {
  const payload = await request.json().catch(() => ({}));
  const cookieStore = cookies();
  const refreshTokenFromCookie = cookieStore.get("fiscia_refresh_token")?.value;
  const refreshToken = payload.refresh_token || refreshTokenFromCookie;

  if (!refreshToken) {
    return NextResponse.json({ detail: "Refresh token manquant" }, { status: 401 });
  }

  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken })
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    return NextResponse.json(data, { status: response.status });
  }

  const accessToken: string = data?.tokens?.access_token ?? data?.access_token ?? "";
  const newRefreshToken: string = data?.tokens?.refresh_token ?? data?.refresh_token ?? refreshToken;

  if (!accessToken) {
    return NextResponse.json({ detail: "Token d'acces absent" }, { status: 502 });
  }

  cookieStore.set("fiscia_access_token", accessToken, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 15
  });

  cookieStore.set("fiscia_refresh_token", newRefreshToken, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24 * 7
  });

  return NextResponse.json({ status: "ok" });
}
