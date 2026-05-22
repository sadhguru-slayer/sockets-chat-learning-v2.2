# FastAPI Real-Time Group Chat (WebSockets + Redis)

A real-time group chat application built with **FastAPI**, **WebSockets**, and **Redis Pub/Sub**, fully containerized using **Docker** and **Docker Compose**.

It supports:
- Group-based chat rooms
- Real-time messaging via WebSockets
- Typing indicators
- Online users tracking
- Message history (Redis-backed)
- Multi-client support using Redis Pub/Sub

---

## 🚀 Features

- 🔥 Real-time chat using WebSockets
- 👥 Group chat rooms (`group_id` based)
- 📡 Redis Pub/Sub for message broadcasting
- 💾 Persistent chat history (last 50 messages per group)
- 🟢 Online users tracking
- ⌨️ Typing indicator support
- 🐳 Dockerized for easy setup

---

## 🧱 Tech Stack

- **Backend:** FastAPI
- **WebSockets:** FastAPI WebSocket support
- **Cache / PubSub:** Redis
- **Server:** Uvicorn
- **Containerization:** Docker + Docker Compose

---

## 📁 Project Structure

```

.
├── main.py              # FastAPI app + WebSocket routes + Redis listener
├── manager.py           # ConnectionManager (handles groups & users)
├── redis_client.py      # Redis async client
├── index.html           # Frontend UI
├── static/              # Static files (if any)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md

```

---

## ⚙️ How It Works

### 1. WebSocket Connection
Clients connect to:

```

ws://localhost:8000/ws/{group_id}?client_id=USERNAME

```

Each client joins a group chat identified by `group_id`.

---

### 2. Messaging Flow

- Client sends message → FastAPI WebSocket
- Server publishes message to Redis channel:  
  `group:{group_id}`
- Redis listener receives message
- Server broadcasts message to all connected clients in that group

---

### 3. Message Types

Supported message types:

- `chat` → normal chat message
- `typing` → typing indicator
- `system` → join/leave notifications
- `online_users` → active users list

---

### 4. Message History

On connection:
- Last **50 messages** are loaded from Redis list:
```

group:{group_id}:history

````

---

## 🐳 Running with Docker

### 1. Build and start services

```bash
docker-compose up --build
````

This will start:

* FastAPI app → [http://localhost:8000](http://localhost:8000)
* Redis server → localhost:6379

---

### 2. Services in Docker Compose

```yaml
version: '3.9'

services:
  fastapi:
    build: .
    container_name: fastapi_app
    ports:
      - "8000:8000"
    depends_on:
      - redis

  redis:
    image: redis:7
    container_name: redis-server
    ports:
      - "6379:6379"
```

---

## 🐳 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🧪 Running Locally (without Docker)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis

Make sure Redis is running on port 6379:

```bash
redis-server
```

### 3. Run FastAPI

```bash
uvicorn main:app --reload
```

---

## 🌐 WebSocket Example Client

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/mygroup?client_id=alice");

ws.onmessage = (event) => {
  console.log("Message:", JSON.parse(event.data));
};

ws.send(JSON.stringify({
  type: "chat",
  message: "Hello everyone!"
}));
```

---

## 📌 Notes

* Each group is isolated using Redis channels: `group:{group_id}`
* Chat history is stored in Redis lists (last 50 messages)
* Duplicate usernames in same group are not allowed
* Designed for horizontal scaling using Redis Pub/Sub

---

## 📈 Future Improvements

* Authentication (JWT-based login)
* Private messaging
* Message timestamps formatting
* Rate limiting
* Message persistence in database (PostgreSQL/MongoDB)
* Frontend UI improvements (React/Vue)

---

## 🧑‍💻 Author
Built with FastAPI + Redis for learning real-time systems and scalable chat architecture.
