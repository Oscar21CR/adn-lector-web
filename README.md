# ADN Lector — Web

Proyecto de hosting para los perfiles ADN Lector.
Cada perfil generado recibe una URL pública permanente (90 días).

## Stack

- **Vercel** — hosting y serverless functions (gratis)
- **Upstash Redis** — almacenamiento de perfiles (gratis)
- **Jinja2** — motor de plantillas HTML

---

## Setup inicial (una sola vez)

### 1. Crear cuenta en Upstash

1. Ir a **upstash.com** y registrarte (podés usar "Sign in with GitHub")
2. Clic en **"Create Database"**
3. Tipo: **Redis**
4. Nombre: `adn-lector`
5. Región: **US-East-1** (o la más cercana a ti)
6. Plan: **Free**
7. Clic en **"Create"**
8. En la pantalla del database, copiá estos dos valores:
   - `UPSTASH_REDIS_REST_URL`  → algo como `https://xxxxx.upstash.io`
   - `UPSTASH_REDIS_REST_TOKEN` → un token largo

### 2. Conectar Vercel con GitHub

1. Ir a **vercel.com** (ya tenés cuenta)
2. Clic en **"Add New Project"**
3. Importar el repositorio `adn-lector-web` desde GitHub
4. Antes de hacer deploy, ir a **"Environment Variables"** y agregar:
   - `UPSTASH_REDIS_REST_URL` → el valor copiado de Upstash
   - `UPSTASH_REDIS_REST_TOKEN` → el valor copiado de Upstash
5. Clic en **"Deploy"**
6. En ~1 minuto vas a tener una URL tipo `adn-lector-web.vercel.app`

---

## Probar que funciona

Una vez deployado, abrí una terminal y corré:

```bash
curl -X POST https://TU-DOMINIO.vercel.app/api/generate \
  -H "Content-Type: application/json" \
  -d @ejemplo_oscar.json
```

Deberías recibir algo como:
```json
{
  "ok": true,
  "url": "https://adn-lector-web.vercel.app/api/perfil?id=655230f2",
  "id": "655230f2"
}
```

Abrí esa URL en el navegador — es la página pública del perfil.

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/generate` | Recibe JSON del perfil, devuelve `{ url, id }` |
| GET | `/api/perfil?id=xxx` | Sirve el HTML del perfil |

### Formato del POST

El body debe ser el JSON del perfil en el formato definido.
Ver `ejemplo_oscar.json` como referencia.

### Respuesta del POST

```json
{
  "ok": true,
  "url": "https://adn-lector-web.vercel.app/api/perfil?id=abc123",
  "id": "abc123"
}
```

Usá `url` para enviársela al usuario por correo.

---

## Flujo completo con Make.com

```
Notion (nueva respuesta)
  → Claude API (genera JSON del perfil)
  → POST /api/generate (devuelve URL)
  → Gmail (envía correo con la URL)
```
