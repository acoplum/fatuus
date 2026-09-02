import type { CleanResult, ProbeResult } from "./types";

export class ApiError extends Error {
  status: number;

  constructor(status: number) {
    super(`Chamada à API falhou com status ${status}`);
    this.name = "ApiError";
    this.status = status;
  }
}

async function postJson<T>(path: string, text: string, lang: string): Promise<T> {
  const headers: Record<string, string> = {
    "content-type": "application/json",
  };

  let targetUrl = path;
  if (
    typeof window !== "undefined" &&
    (window.location?.href?.includes("@") || (typeof document !== "undefined" && document.baseURI?.includes("@")))
  ) {
    try {
      const url = new URL(path, window.location.origin);
      url.username = "";
      url.password = "";
      targetUrl = url.href;

      const current = new URL(window.location.href);
      if (current.username && current.password) {
        const creds = btoa(`${current.username}:${current.password}`);
        headers["authorization"] = `Basic ${creds}`;
      }
    } catch {
      // Fallback
    }
  }

  const response = await fetch(targetUrl, {
    method: "POST",
    headers,
    body: JSON.stringify({ text, lang }),
  });
  if (!response.ok) {
    throw new ApiError(response.status);
  }
  return response.json() as Promise<T>;
}

export function probeText(text: string, lang = "pt"): Promise<ProbeResult> {
  return postJson<ProbeResult>("/probe", text, lang);
}

export function cleanText(text: string, lang = "pt"): Promise<CleanResult> {
  return postJson<CleanResult>("/clean", text, lang);
}
