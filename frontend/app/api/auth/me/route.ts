import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_BASE_URL = process.env.FISCIA_API_URL ?? "http://localhost:8000";

async function refreshAccessToken(refreshToken: string): Promise<string | undefined> {
  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken })
  });

  if (!response.ok) return undefined;
  const data = await response.json().catch(() => ({}));
  const accessToken: string = data?.tokens?.access_token ?? data?.access_token ?? "";
  const nextRefreshToken: string = data?.tokens?.refresh_token ?? data?.refresh_token ?? refreshToken;
  if (!accessToken) return undefined;

  const cookieStore = cookies();
  cookieStore.set("fiscia_access_token", accessToken, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 15
  });
  cookieStore.set("fiscia_refresh_token", nextRefreshToken, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24 * 7
  });

  return accessToken;
}

export async function GET() {
  const cookieStore = cookies();
  let accessToken = cookieStore.get("fiscia_access_token")?.value;
  const refreshToken = cookieStore.get("fiscia_refresh_token")?.value;

  if (!accessToken && refreshToken) {
    accessToken = await refreshAccessToken(refreshToken);
  }

  if (!accessToken) {
    return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
  }

  let response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });

  if (response.status === 401 && refreshToken) {
    const renewedToken = await refreshAccessToken(refreshToken);
    if (renewedToken) {
      response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${renewedToken}`
        }
      });
    }
  }

  const data = await response.json().catch(() => ({}));
  return NextResponse.json(data, { status: response.status });
}
