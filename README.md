# Chat App with Kafka and Docker

A simple real-time chat application built with Python, FastAPI, Apache Kafka, and Docker. This application demonstrates how to use Kafka for message streaming in a web application.

## Features

- Real-time chat using WebSockets
- Apache Kafka for message streaming and persistence
- Docker containerization for easy deployment
- Web-based chat interface
- Command-line producer/consumer tools for testing
- RESTful API endpoints

## Architecture

- **FastAPI**: Web framework and WebSocket server
- **Apache Kafka**: Message streaming platform
- **Zookeeper**: Kafka coordination service
- **Docker**: Containerization platform

## Prerequisites

- Docker and Docker Compose installed
- Python 3.9+ (for local development)

## Quick Start

### 1. Clone and Navigate
```bash
cd /path/to/your/project
```

### 2. Start the Application
```bash
docker-compose up --build
```

This will start:
- Zookeeper (port 2181)
- Kafka (port 9092)
- Chat App (port 8000)

### 3. Access the Application

- **Web Chat Interface**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs

## Usage

### Web Interface
1. Open http://localhost:8000 in multiple browser tabs/windows
2. Start typing messages in any tab
3. Messages will appear in real-time across all connected clients

### Command Line Tools

Open separate terminals and run:

**Consumer (to listen for messages):**
```bash
docker exec -it chatapp python kafka_consumer.py
```

**Producer (to send messages):**
```bash
docker exec -it chatapp python kafka_producer.py
```

### REST API
Send messages via API:
```bash
curl -X POST "http://localhost:8000/send-message" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello from API", "username": "API-User"}'
```

## Project Structure

```
.
├── main.py                 # FastAPI application with WebSocket support
├── kafka_config.py         # Kafka configuration and connection management
├── kafka_producer.py       # CLI producer for testing
├── kafka_consumer.py       # CLI consumer for testing
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Multi-container Docker setup
└── README.md             # This file
```

## Configuration

### Environment Variables
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses (default: localhost:9092)

### Kafka Topic
- Default topic: `chat-messages`
- Automatically created when first message is sent

## Development

### Local Development (without Docker)

1. **Start Kafka and Zookeeper:**
```bash
docker-compose up kafka zookeeper
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python main.py
```

### Testing Kafka Separately

1. **Start infrastructure:**
```bash
docker-compose up kafka zookeeper
```

2. **Run consumer in one terminal:**
```bash
python kafka_consumer.py
```

3. **Run producer in another terminal:**
```bash
python kafka_producer.py
```

## API Endpoints

- `GET /`: Chat web interface
- `GET /health`: Health check
- `POST /send-message`: Send message via API
- `WebSocket /ws`: Real-time communication

## Troubleshooting

### Common Issues

1. **Kafka connection failed:**
   - Ensure Docker containers are running: `docker-compose ps`
   - Check logs: `docker-compose logs kafka`

2. **Port conflicts:**
   - Modify ports in `docker-compose.yml` if needed
   - Default ports: 8000 (app), 9092 (Kafka), 2181 (Zookeeper)

3. **Messages not appearing:**
   - Check WebSocket connection in browser console
   - Verify Kafka topic exists: `docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092`

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f chatapp
docker-compose logs -f kafka
```

### Cleanup
```bash
# Stop all services
docker-compose down

# Remove volumes (clears Kafka data)
docker-compose down -v
```

## Extensions

This basic application can be extended with:
- User authentication and authorization
- Message persistence to database
- Message history loading
- Private/group chat rooms
- File sharing capabilities
- Message encryption