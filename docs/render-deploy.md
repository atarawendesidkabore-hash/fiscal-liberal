# Deploying FiscIA Pro on Render

This repository is configured for a three-service Render deployment:

- `fiscal-liberal-site`: the public marketing website
- `fiscal-liberal-app`: the authenticated Next.js app
- `fiscal-liberal-api`: the FastAPI backend

## What the blueprint does

The root [`render.yaml`](../render.yaml) provisions:

- one PostgreSQL database
- one Python web service for the API
- two Node web services for the marketing site and the app
- cross-service environment wiring for:
  - app -> API public URL
  - app -> marketing public URL
  - marketing -> app public URL
  - backend Stripe redirect URL -> app public URL

## Deploy steps

1. Push the repository to GitHub.
2. In Render, create a new Blueprint instance from the repo.
3. Review the generated services and deploy.
4. After the first deploy, add any optional production secrets you need:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_WEBHOOK_SECRET`
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_PRICE_STARTER`
   - `STRIPE_PRICE_PRO`
   - `STRIPE_PRICE_CABINET`
5. Add your custom domains if you want stable branded URLs.

## AI in production

The core app will run without Ollama, but AI endpoints will only work if you provide a reachable Ollama host. If you want AI in production, set:

- `OLLAMA_HOST`
- `OLLAMA_MODEL`

Example:

```text
OLLAMA_HOST=https://your-ollama-host.example.com
OLLAMA_MODEL=fiscia-fiscal-is-v3
```

## Notes

- Backend startup already creates tables for a fresh database.
- Alembic now respects the `DATABASE_URL` environment variable if you want to run migrations manually.
- The backend CORS policy accepts Render-hosted origins by default and can still be extended with `CORS_EXTRA_ORIGINS`.
