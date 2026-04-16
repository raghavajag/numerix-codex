const DEFAULT_API_BASE = "https://shaun-effortful-lucien.ngrok-free.dev";

type BackendStatus = "success" | "non_animation" | "error";

export interface RunResponse {
  result: string;
  status: BackendStatus;
}

function normalizeRunUrl(rawUrl?: string) {
  const base = (rawUrl || "").trim();
  if (!base) {
    return `${DEFAULT_API_BASE}/run`;
  }

  if (base.endsWith("/run")) {
    return base;
  }

  return `${base.replace(/\/$/, "")}/run`;
}

export const NUMERIX_RUN_URL = normalizeRunUrl(
  import.meta.env.VITE_NUMERIX_API_URL || import.meta.env.VITE_ANIMAI_API_URL,
);

export async function runNumerixPrompt(prompt: string, language: string) {
  const response = await fetch(NUMERIX_RUN_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt, lang: language }),
  });

  let data: RunResponse | null = null;
  try {
    data = (await response.json()) as RunResponse;
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new Error(data?.result || `Request failed with status ${response.status}`);
  }

  if (!data) {
    throw new Error("The backend returned an empty response.");
  }

  return data;
}
