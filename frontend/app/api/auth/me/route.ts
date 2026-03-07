import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_BASE_URL = process.env.FISCIA_API_URL ?? "http://localhost:8000";

export async function GET() {
  const accessToken = cookies().get("fiscia_access_token")?.value;
  if (!accessToken) {
    return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
  }

  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });

  const data = await response.json().catch(() => ({}));
  return NextResponse.json(data, { status: response.status });
}


