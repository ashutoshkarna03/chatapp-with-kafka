from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import threading
from datetime import datetime
from typing import List
import logging
from kafka_config import kafka_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chat App with Kafka", version="1.0.0")

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection established. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# Kafka message handler
class KafkaMessageHandler:
    def __init__(self):
        self.producer = None
        self.consumer = None
        self.running = False
        
    def start(self):
        """Start the Kafka consumer in a separate thread"""
        if not self.running:
            self.running = True
            self.producer = kafka_config.get_producer()
            consumer_thread = threading.Thread(target=self._consume_messages, daemon=True)
            consumer_thread.start()
            logger.info("Kafka message handler started")
    
    def stop(self):
        """Stop the Kafka consumer"""
        self.running = False
        if self.producer:
            self.producer.close()
        logger.info("Kafka message handler stopped")
    
    def _consume_messages(self):
        """Consume messages from Kafka topic"""
        try:
            consumer = kafka_config.get_consumer()
            logger.info("Started consuming messages from Kafka...")
            
            for message in consumer:
                if not self.running:
                    break
                
                try:
                    # Broadcast message to all WebSocket connections
                    asyncio.run(manager.broadcast(json.dumps(message.value)))
                except Exception as e:
                    logger.error(f"Error processing Kafka message: {e}")
                    
        except Exception as e:
            logger.error(f"Error in Kafka consumer: {e}")
        finally:
            if consumer:
                consumer.close()
    
    def send_message(self, message_data: dict):
        """Send message to Kafka topic"""
        try:
            if self.producer:
                self.producer.send(kafka_config.topic, value=message_data)
                self.producer.flush()
                logger.info(f"Message sent to Kafka: {message_data}")
            else:
                logger.error("Kafka producer not initialized")
        except Exception as e:
            logger.error(f"Error sending message to Kafka: {e}")
            raise

# Global Kafka handler
kafka_handler = KafkaMessageHandler()

@app.on_event("startup")
async def startup_event():
    """Initialize Kafka connection on startup"""
    try:
        kafka_handler.start()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up Kafka connections on shutdown"""
    kafka_handler.stop()
    logger.info("Application shutdown complete")

@app.get("/")
async def get_chat_page():
    """Serve the chat page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chat App with Kafka</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .chat-container {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .messages {
                height: 400px;
                overflow-y: auto;
                border: 1px solid #ddd;
                padding: 10px;
                margin-bottom: 20px;
                background: #fafafa;
                border-radius: 5px;
            }
            .message {
                margin-bottom: 10px;
                padding: 8px;
                background: #e3f2fd;
                border-radius: 5px;
                border-left: 4px solid #2196f3;
            }
            .input-container {
                display: flex;
                gap: 10px;
            }
            input[type="text"] {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
            }
            button {
                padding: 10px 20px;
                background: #2196f3;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background: #1976d2;
            }
            .status {
                margin-bottom: 10px;
                padding: 10px;
                border-radius: 5px;
                text-align: center;
            }
            .connected {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .disconnected {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <h1>Chat App with Kafka</h1>
            <div id="status" class="status disconnected">Disconnected</div>
            <div id="messages" class="messages"></div>
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="Type your message..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");
            const messages = document.getElementById('messages');
            const messageInput = document.getElementById('messageInput');
            const status = document.getElementById('status');

            ws.onopen = function(event) {
                status.textContent = 'Connected';
                status.className = 'status connected';
            };

            ws.onmessage = function(event) {
                const messageData = JSON.parse(event.data);
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message';
                messageDiv.innerHTML = `
                    <strong>${messageData.username}:</strong> ${messageData.message}
                    <br><small>${messageData.timestamp}</small>
                `;
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            };

            ws.onclose = function(event) {
                status.textContent = 'Disconnected';
                status.className = 'status disconnected';
            };

            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                status.textContent = 'Connection Error';
                status.className = 'status disconnected';
            };

            function sendMessage() {
                const message = messageInput.value.trim();
                if (message) {
                    ws.send(JSON.stringify({
                        message: message,
                        username: 'User' + Math.floor(Math.random() * 1000)
                    }));
                    messageInput.value = '';
                }
            }

            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Add timestamp
            message_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Send message to Kafka
            kafka_handler.send_message(message_data)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Chat app is running"}

@app.post("/send-message")
async def send_message_api(message: dict):
    """API endpoint to send messages"""
    try:
        # Add timestamp
        message['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Send to Kafka
        kafka_handler.send_message(message)
        
        return {"status": "success", "message": "Message sent successfully"}
    except Exception as e:
        logger.error(f"Error sending message via API: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 