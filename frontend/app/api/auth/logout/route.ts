import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_BASE_URL = process.env.FISCIA_API_URL ?? "http://localhost:8000";

export async function POST(request: Request) {
  const payload = await request.json().catch(() => ({}));
  const cookieStore = cookies();
  const refreshTokenFromCookie = cookieStore.get("fiscia_refresh_token")?.value;
  const accessToken = cookieStore.get("fiscia_access_token")?.value;
  const refreshToken = payload.refresh_token || refreshTokenFromCookie || "";

  if (accessToken && refreshToken) {
    await fetch(`${API_BASE_URL}/auth/logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`
      },
      body: JSON.stringify({ refresh_token: refreshToken })
    }).catch(() => null);
  }

  cookieStore.set("fiscia_access_token", "", {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 0
  });
  cookieStore.set("fiscia_refresh_token", "", {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 0
  });

  return NextResponse.json({ status: "logged_out" });
}


