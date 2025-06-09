#!/usr/bin/env python3

import json
from kafka_config import kafka_config

def main():
    """Simple Kafka consumer for testing"""
    print("Starting Kafka Consumer...")
    
    try:
        consumer = kafka_config.get_consumer(group_id='cli-consumer-group')
        print(f"Connected to Kafka at {kafka_config.bootstrap_servers}")
        print(f"Listening for messages on topic: {kafka_config.topic}")
        print("Press Ctrl+C to exit\n")
        
        message_count = 0
        for message in consumer:
            try:
                message_count += 1
                message_data = message.value
                
                print(f"\n--- Message {message_count} ---")
                print(f"Username: {message_data.get('username', 'Unknown')}")
                print(f"Message: {message_data.get('message', '')}")
                print(f"Timestamp: {message_data.get('timestamp', 'No timestamp')}")
                print(f"Message ID: {message_data.get('message_id', 'N/A')}")
                print("-" * 30)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error processing message: {e}")
                
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
    except Exception as e:
        print(f"Failed to create consumer: {e}")
    finally:
        if 'consumer' in locals():
            consumer.close()
        print("Consumer closed.")

if __name__ == "__main__":
    main() 