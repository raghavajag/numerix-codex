import { NextRequest, NextResponse } from "next/server";

const API_URL =
  process.env.NUMERIX_API_URL || process.env.ANIMAI_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const response = await fetch(`${API_URL}/run`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json(
      { result: "Unexpected frontend proxy error", status: "error" },
      { status: 500 }
    );
  }
}
