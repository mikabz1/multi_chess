# Multi Chess Pro

A web-based real-time multiplayer chess platform. Play against friends via invite links or get paired instantly with Quick Match. Built with Vue 3, Flask, PostgreSQL, and Socket.IO.

**Repository:** https://github.com/mikabz1/multi_chess

---

## Team Members

| Full Name | ID Number | Email | Phone |
|-----------|-----------|-------|-------|
| Michael Benzekri | 315262329 | mikabz1@gmail.com | 0586422074 |
| Ron Adi | 206549594 | Ronadi789@gmail.com | 0544606379 |
| Roei Shitrit | 206436065 | roeishi489@gmail.com | 0522053935 |

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10 or later)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2 or later)

No local installation of Python, Node.js, or PostgreSQL is required when using Docker.

---

## Installation and Run (Docker — Recommended)

### 1. Clone the repository

```bash
git clone https://github.com/mikabz1/multi_chess.git
cd multi_chess
```

### 2. Create the environment file

```bash
cp .env.example .env
```

The default values in `.env.example` work out of the box for local development. For production, change at minimum:

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `POSTGRES_PASSWORD`

### 3. Start all services

```bash
docker compose up --build
```

On the first run, Docker will download images, install dependencies, and create the database tables automatically.

Wait until all four services are running:

| Service | Role |
|---------|------|
| `db` | PostgreSQL database |
| `backend` | Flask REST API + Socket.IO |
| `frontend` | Vue 3 development server (Vite) |
| `proxy` | Caddy reverse proxy |

### 4. Open the application

| URL | Description |
|-----|-------------|
| **http://localhost** | Main entry point (via Caddy proxy) |
| http://localhost:5173 | Frontend directly |
| http://localhost:5001/api/health | Backend health check |

Use **http://localhost** for normal usage — the proxy routes API and WebSocket traffic to the backend and serves the frontend for all other paths.

### 5. Stop the application

```bash
docker compose down
```

To stop and remove database data:

```bash
docker compose down -v
```

---

## How to Play (Two Players on One Computer)

1. Open **http://localhost** in a regular Chrome tab.
2. Register a new user (e.g. `player1`) and log in.
3. Open an **Incognito** window and go to **http://localhost**.
4. Register a second user (e.g. `player2`) and log in.
5. In one window, go to the Lobby and click **Find Opponent** (Quick Match), or create a private game and share the invite link with the other window.
6. Play chess in real time.

---

## Cloud Demo

The project is also deployed on a cloud server:

**http://multi-chess.gleeze.com**

The cloud servers are not running continuously. To request a live demo, contact the project team so the server can be started.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database username | `chess` |
| `POSTGRES_PASSWORD` | Database password | `chess` |
| `POSTGRES_DB` | Database name | `chess_db` |
| `DATABASE_URL` | SQLAlchemy connection URI | `postgresql://chess:chess@db:5432/chess_db` |
| `SECRET_KEY` | Flask secret key | `change-this-secret` |
| `JWT_SECRET_KEY` | JWT signing key | `change-this-jwt-secret` |
| `CORS_ORIGINS` | Allowed API origins | `*` |

---

## Project Structure

```
multi_chess/
├── backend/          # Flask API, Socket.IO, chess logic
│   ├── app/
│   │   ├── models/   # Database models
│   │   ├── routes/   # REST API endpoints
│   │   ├── services/ # Business logic
│   │   └── sockets/  # Real-time events
│   └── run.py
├── frontend/         # Vue 3 SPA
│   └── src/
│       ├── pages/    # Login, Lobby, Game, History
│       └── components/
├── proxy/            # Caddy reverse-proxy config
└── docker-compose.yml
```

---

## Troubleshooting

**Port 80 already in use**

Another service is using port 80. Stop it, or change the proxy port in `docker-compose.yml`:

```yaml
proxy:
  ports:
    - "8080:80"
```

Then open **http://localhost:8080**.

**Backend fails to connect to the database**

Wait a few seconds for PostgreSQL to become healthy, then restart:

```bash
docker compose restart backend
```

**401 errors when loading a game**

Log out and log back in. The JWT token may have expired or been cleared.

**Quick Match does not find an opponent**

Two different users must be in the queue at the same time. Use two browser sessions as described above.

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| Frontend | Vue 3, Vue Router, Pinia, Vite, Axios, Socket.IO Client, chess.js |
| Backend | Python, Flask, Flask-JWT-Extended, Flask-SocketIO, python-chess |
| Database | PostgreSQL 16 |
| Infrastructure | Docker Compose, Caddy |
