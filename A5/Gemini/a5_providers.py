"""Perfiles públicos y consulta de catálogo Gemini. Nunca persiste credenciales."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request

PROFILES = {
    "openai": {"endpoint": "https://api.openai.com/v1/chat/completions",
               "api_key_env": "OPENAI_API_KEY", "output_token_parameter": "max_completion_tokens"},
    "gemini": {"endpoint": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
               "api_key_env": "GEMINI_API_KEY", "output_token_parameter": "max_tokens"},
}

# Tarifas estándar consultadas; se seleccionan junto con el modelo para no heredar las de Sol al usar Luna.
OPENAI_MODELS = {
    "gpt-6.1-sol": {"model": "gpt-6.1-sol", "input_usd": 2.0, "output_usd": 10.0,
                    "pricing_verified": True, "pricing_date": "2026-11-14",
                    "pricing_source": "https://developers.openai.com/api/docs/models/gpt-6.1-sol"},
    "gpt-6-luna": {"model": "gpt-6-luna", "input_usd": 0.1, "output_usd": 0.5,
                   "pricing_verified": True, "pricing_date": "2026-11-14",
                   "pricing_source": "https://developers.openai.com/api/docs/models/gpt-6-luna"},
}


def profile(provider, model=""):
    if provider not in PROFILES:
        raise ValueError("PROVIDER debe ser openai o gemini")
    model = model.strip()
    prefix = "gpt-" if provider == "openai" else "gemini-"
    if model and (not model.startswith(prefix) or not re.fullmatch(r"[A-Za-z0-9._-]+", model)):
        raise ValueError("El identificador del modelo no corresponde al proveedor seleccionado")
    return {"provider": provider, "model": model, **PROFILES[provider]}


def run_id(provider, model, stage, sequence):
    profile(provider, model)
    if stage not in {"conexion", "piloto45", "test"} or not re.fullmatch(r"[A-Za-z0-9_-]+", str(sequence)):
        raise ValueError("Usa etapa conexion/piloto45/test y una secuencia sin rutas")
    slug = model.replace(".", "_").replace("-", "_") if model else "sin_modelo"
    if provider == "openai" and model == "gpt-6.1-sol":
        label = "sol"
    elif provider == "openai" and model == "gpt-6-luna":
        label = "luna"
    elif provider == "gemini":
        label = "gemini_" + slug.removeprefix("gemini_")
    else:
        label = provider + "_" + slug
    return f"a5_{label}_{stage}_{sequence}"


def validate_config(cfg):
    expected = profile(cfg["provider"], cfg["model"])
    for key in ("endpoint", "output_token_parameter"):
        if cfg[key] != expected[key]:
            raise ValueError("Configuración mezclada: vuelve a ejecutar el bloque 4 y reconstruye CFG")
    if not cfg["model"]:
        raise ValueError("Consulta el catálogo y selecciona el modelo antes de activar la API")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def list_gemini_models(token, opener=None):
    """Solo GET de metadatos con paginación. No envía textos ni hace inferencias.

    Aparecer en el catálogo no confirma facturación, cuota ni compatibilidad
    de todos los parámetros: se requiere después una prueba de conexión.
    """
    if not isinstance(token, str) or not token.strip():
        raise ValueError("Ingresa la clave Gemini en el campo oculto")
    client = opener or urllib.request.build_opener(NoRedirect())
    models, seen_pages, page = {}, set(), None
    for _ in range(20):
        query = {"pageSize": 1000}
        if page:
            query["pageToken"] = page
        url = "https://generativelanguage.googleapis.com/v1beta/models?" + urllib.parse.urlencode(query)
        request = urllib.request.Request(url, headers={"x-goog-api-key": token}, method="GET")
        try:
            with client.open(request, timeout=30) as response:
                body = json.loads(response.read())
        except urllib.error.HTTPError as exc:
            code = exc.code
            exc.close()
            raise RuntimeError(f"No se pudo consultar Gemini (HTTP {code}). Revisa clave, permisos y restricciones del proyecto.") from None
        except (urllib.error.URLError, OSError, ValueError):
            raise RuntimeError("No se pudo leer el catálogo Gemini. Revisa conexión y acceso; no se realizó inferencia.") from None
        if not isinstance(body, dict) or not isinstance(body.get("models", []), list):
            raise ValueError("Respuesta de catálogo inválida")
        for row in body.get("models", []):
            name = row.get("name", "").removeprefix("models/")
            methods = row.get("supportedGenerationMethods", [])
            if name.startswith("gemini-") and "generateContent" in methods:
                models[name] = {"model_id": name, "display_name": row.get("displayName", name),
                                "input_token_limit": row.get("inputTokenLimit"),
                                "output_token_limit": row.get("outputTokenLimit")}
        page = body.get("nextPageToken")
        if not page:
            return [models[k] for k in sorted(models)]
        if not isinstance(page, str) or page in seen_pages:
            raise ValueError("Paginación de catálogo inválida")
        seen_pages.add(page)
    raise ValueError("Catálogo excede el límite de páginas; no se devuelve una lista incompleta")
