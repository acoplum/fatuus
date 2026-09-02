import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, cleanText, probeText } from "./api";

describe("api", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("probeText posts to /probe and returns the parsed analysis", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ synthetic_score: 10, slop_count: 1 }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await probeText("olá", "pt");

    expect(fetchMock).toHaveBeenCalledWith(
      "/probe",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ text: "olá", lang: "pt" }),
      })
    );
    expect(result).toEqual({ synthetic_score: 10, slop_count: 1 });
  });

  it("cleanText posts to /clean and returns the parsed pipeline result", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ cleaned_text: "Texto limpo.", layer1_accepted: true }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await cleanText("texto", "pt");

    expect(fetchMock).toHaveBeenCalledWith(
      "/clean",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ text: "texto", lang: "pt" }),
      })
    );
    expect(result).toEqual({ cleaned_text: "Texto limpo.", layer1_accepted: true });
  });

  it("defaults lang to pt when not given", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({}) });
    vi.stubGlobal("fetch", fetchMock);

    await probeText("olá");

    expect(fetchMock).toHaveBeenCalledWith(
      "/probe",
      expect.objectContaining({ body: JSON.stringify({ text: "olá", lang: "pt" }) })
    );
  });

  it("throws ApiError with the response status when the request fails", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: false, status: 401, json: async () => ({}) });
    vi.stubGlobal("fetch", fetchMock);

    await expect(probeText("olá")).rejects.toThrow(ApiError);
    await expect(probeText("olá")).rejects.toMatchObject({ status: 401 });
  });
});
