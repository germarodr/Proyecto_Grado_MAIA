export async function proxyApi(path: "predictions" | "health" | "examples", request?: Request) {
  try {
    const base = (process.env.API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
    const response = await fetch(`${base}/${path}`, {
      method: request?.method ?? "GET",
      headers: { "Content-Type": "application/json" },
      body: request?.method === "POST" ? await request.text() : undefined,
      cache: "no-store",
      signal: AbortSignal.timeout(330_000),
    });
    return new Response(await response.text(), {
      status: response.status,
      headers: { "Content-Type": response.headers.get("content-type") ?? "application/json", "Cache-Control": "no-store" },
    });
  } catch {
    return Response.json({ detail: "No se pudo conectar con la API. Compruebe que el servicio esté activo y que los modelos estén cargados." }, { status: 503 });
  }
}
