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
  const response = await fetch(path, {
    method: "POST",
    headers: { "content-type": "application/json" },
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
