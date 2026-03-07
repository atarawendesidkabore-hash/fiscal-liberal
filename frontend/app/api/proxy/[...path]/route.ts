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
  const url = `${API_BASE_URL}/${endpoint}`;

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
    body: body || undefined
  });

  const payload = await response.text();
  let data: unknown = payload;
  try {
    data = payload ? JSON.parse(payload) : {};
  } catch {
    data = { message: payload };
  }

  return NextResponse.json(data, { status: response.status });
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


