import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_BASE_URL = process.env.FISCIA_API_URL ?? "http://localhost:8000";

type Context = {
  params: {
    path: string[];
  };
};

async function forward(request: Request, { params }: Context, method: string) {
  const endpoint = params.path.join("/");
  const accessToken = cookies().get("fiscia_access_token")?.value;
  const isAuthenticated = Boolean(accessToken);
  const incomingUrl = new URL(request.url);
  const query = incomingUrl.search ? incomingUrl.search : "";
  const url = `${API_BASE_URL}/${endpoint}${query}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json"
  };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  const body = method === "GET" ? undefined : await request.text();
  const response = await fetch(url, {
    method,
    headers,
    body: body || undefined,
    cache: method === "GET" && !isAuthenticated ? "force-cache" : "no-store",
    next: method === "GET" && !isAuthenticated ? { revalidate: 60 } : undefined
  });

  const payload = await response.text();
  let data: unknown = payload;
  try {
    data = payload ? JSON.parse(payload) : {};
  } catch {
    data = { message: payload };
  }

  const proxied = NextResponse.json(data, { status: response.status });
  if (method === "GET" && !isAuthenticated) {
    proxied.headers.set("Cache-Control", "public, s-maxage=60, stale-while-revalidate=120");
  } else {
    proxied.headers.set("Cache-Control", "private, no-store");
  }
  return proxied;
}

export async function GET(request: Request, context: Context) {
  return forward(request, context, "GET");
}

export async function POST(request: Request, context: Context) {
  return forward(request, context, "POST");
}

export async function PUT(request: Request, context: Context) {
  return forward(request, context, "PUT");
}

export async function DELETE(request: Request, context: Context) {
  return forward(request, context, "DELETE");
}


