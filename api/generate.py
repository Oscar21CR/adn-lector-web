import json
import os
import uuid
from pathlib import Path
from http.server import BaseHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader
from upstash_redis import Redis

# Plantilla vive en la raíz del proyecto
TEMPLATE_DIR = str(Path(__file__).parent.parent)
TEMPLATE_NAME = "template.html.j2"

# 90 días de expiración por perfil
EXPIRY_SECONDS = 60 * 60 * 24 * 90


def render_profile(perfil: dict) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    return env.get_template(TEMPLATE_NAME).render(**perfil)


def get_redis() -> Redis:
    return Redis(
        url=os.environ["UPSTASH_REDIS_REST_URL"],
        token=os.environ["UPSTASH_REDIS_REST_TOKEN"],
    )


def build_base_url() -> str:
    """Detecta automáticamente la URL del deployment de Vercel."""
    url = os.environ.get("VERCEL_URL", "")
    if url and not url.startswith("http"):
        url = f"https://{url}"
    return url or "http://localhost:3000"


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        """Preflight CORS para que Make.com pueda llamar al endpoint."""
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            perfil = json.loads(raw)

            # 1. Renderizar HTML
            html = render_profile(perfil)

            # 2. Generar ID único si no viene en el JSON
            perfil_id = (perfil.get("id") or str(uuid.uuid4()))[:32]
            perfil_id = perfil_id.replace(" ", "-").lower()

            # 3. Guardar en Redis con expiración
            redis = get_redis()
            redis.set(f"perfil:{perfil_id}", html, ex=EXPIRY_SECONDS)

            # 4. Construir URL pública
            base = build_base_url()
            url = f"{base}/api/perfil?id={perfil_id}"

            self._json(200, {"ok": True, "url": url, "id": perfil_id})

        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)})

    def _json(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def log_message(self, format, *args):
        pass  # Silencia los logs de acceso en Vercel
