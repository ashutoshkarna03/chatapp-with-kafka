#!/usr/bin/env python3

import json
import time
from datetime import datetime
from kafka_config import kafka_config

def main():
    """Simple Kafka producer for testing"""
    print("Starting Kafka Producer...")
    
    try:
        producer = kafka_config.get_producer()
        print(f"Connected to Kafka at {kafka_config.bootstrap_servers}")
        print("Type messages to send (press Ctrl+C to exit):")
        
        message_count = 0
        while True:
            try:
                user_input = input("Enter message: ")
                if user_input.strip():
                    message_data = {
                        "message": user_input,
                        "username": "CLI-Producer",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "message_id": message_count
                    }
                    
                    # Send message to Kafka
                    producer.send(kafka_config.topic, value=message_data)
                    producer.flush()
                    
                    message_count += 1
                    print(f"Message sent! (ID: {message_count})")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error sending message: {e}")
                
    except Exception as e:
        print(f"Failed to create producer: {e}")
    finally:
        if 'producer' in locals():
            producer.close()
        print("\nProducer closed.")

if __name__ == "__main__":
    main() 