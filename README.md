# FPS Anti-Cheat Research Service

This project is a practical backend testbed where I developed a FastAPI service for FPS anti-cheat research.

The service accepts gameplay image payloads and analyzes them using:

- A lightweight OpenCV-based filtering stage.
- Gemini-based escalation for frames that look suspicious.

Together, these are used to reduce unnecessary LLM calls while still flagging behavior that may indicate cheating.

## Backend

Related game repository: [[Game](https://github.com/Pawanjot-Randhawa/MultiplayerFPS)]

- This backend is deployed on Azure using Docker, but the deployment is currently turned off.
- If you want a Docker + Azure demo, contact me.

## Running Locally

### Requirements

- Python 3.13 or newer
- A Google Gemini API key in your environment
- The game client or test source that sends image payloads to this backend
- Docker, if you want to run the service in a container

### Notes

- The API is exposed with FastAPI and can be started directly with Uvicorn.
- The main entrypoint is `app.main:app` and the server listens on port `8000` by default.
- The `/image/upload` endpoint accepts binary image payloads, including Godot-compressed PNG data.
- For local testing, run the backend alongside the game so the game can send screenshots or frame payloads to the service.

### Local Run

1. Install dependencies.
2. Set your environment variables, including the Gemini API key.
3. Start the backend with Uvicorn or Docker.
4. Run the game locally and point it at the backend.

Example commands:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
docker compose up --build
```

## Project Structure (High Level)

- `app/main.py` - FastAPI application setup and router registration.
- `app/server.py` - Uvicorn entrypoint for local development.
- `app/api/routes/image.py` - Image upload, stats, and connection endpoints.
- `app/services/decompress.py` - Decodes raw or Godot-compressed PNG payloads.
- `app/services/filter.py` - Heuristic image filter used before Gemini escalation.
- `app/services/gemini_filter.py` - Gemini-based classification for suspicious frames.
- `app/schemas/responses.py` - Response models returned by the API.

## Purpose

This repository is focused on experimentation and evaluation of anti-cheat filtering ideas in a real-time FPS context.
