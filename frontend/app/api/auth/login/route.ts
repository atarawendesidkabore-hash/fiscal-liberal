import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_BASE_URL = process.env.FISCIA_API_URL ?? "http://localhost:8000";

export async function POST(request: Request) {
  const payload = await request.json();

  let response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok && [400, 401, 422].includes(response.status)) {
    const params = new URLSearchParams();
    params.set("username", payload.email ?? "");
    params.set("password", payload.password ?? "");
    response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: params.toString()
    });
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    return NextResponse.json(data, { status: response.status });
  }

  const accessToken: string = data?.tokens?.access_token ?? data?.access_token ?? "";
  const refreshToken: string = data?.tokens?.refresh_token ?? data?.refresh_token ?? "";
  const cookieStore = cookies();

  if (accessToken) {
    cookieStore.set("fiscia_access_token", accessToken, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 15
    });
  }

  if (refreshToken) {
    cookieStore.set("fiscia_refresh_token", refreshToken, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60 * 24 * 7
    });
  }

  return NextResponse.json(data);
}
