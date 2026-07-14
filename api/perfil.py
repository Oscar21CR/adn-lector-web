import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from upstash_redis import Redis


def get_redis() -> Redis:
    return Redis(
        url=os.environ["UPSTASH_REDIS_REST_URL"],
        token=os.environ["UPSTASH_REDIS_REST_TOKEN"],
    )


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            perfil_id = query.get("id", [""])[0].strip()

            if not perfil_id:
                self._html(400, self._error_page("Falta el ID del perfil."))
                return

            redis = get_redis()
            html = redis.get(f"perfil:{perfil_id}")

            if not html:
                self._html(404, self._error_page(
                    "Perfil no encontrado o expirado.",
                    "Los perfiles están disponibles por 90 días desde su generación."
                ))
                return

            body = html.encode("utf-8") if isinstance(html, str) else html
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        except Exception as e:
            self._html(500, self._error_page(f"Error interno: {e}"))

    def _html(self, status: int, body: bytes):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error_page(self, title: str, detail: str = "") -> bytes:
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ADN Lector</title>
  <style>
    body{{font-family:'Helvetica Neue',sans-serif;background:#FBF6EC;color:#241C14;
         display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;}}
    .box{{text-align:center;max-width:420px;padding:40px 24px;}}
    .dna{{font-size:40px;margin-bottom:20px;}}
    h1{{font-size:22px;margin:0 0 12px;}}
    p{{color:#8C7E68;font-size:16px;margin:0;}}
  </style>
</head>
<body>
  <div class="box">
    <div class="dna">🧬</div>
    <h1>{title}</h1>
    <p>{detail}</p>
  </div>
</body>
</html>""".encode("utf-8")

    def log_message(self, format, *args):
        pass
