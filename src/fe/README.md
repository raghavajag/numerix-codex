# Numerix Frontend

This frontend is the Numerix interface.

It is intentionally simple:

- no auth
- local chat/session history
- direct backend call to the Numerix `/run` endpoint
- preserved demo gallery for sample videos

## Local development

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

The dev server runs on:

```text
http://localhost:5173
```

By default the frontend calls the deployed Numerix backend:

```text
https://shaun-effortful-lucien.ngrok-free.dev/run
```

You can override that with:

```bash
VITE_NUMERIX_API_URL=https://shaun-effortful-lucien.ngrok-free.dev
```

## Expected backend

The frontend expects the backend to expose:

- `POST /run`

with body:

```json
{
  "prompt": "Explain Artemis II trajectory",
  "lang": "en"
}
```

and response:

```json
{
  "result": "https://...",
  "status": "success"
}
```

or:

```json
{
  "result": "text reply",
  "status": "non_animation"
}
```

## Main routes

- `/` home
- `/chat` studio
- `/gallery` demo examples
- `/about` product overview
