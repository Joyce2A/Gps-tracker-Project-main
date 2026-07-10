# from paho.mqtt import client as mqtt_client
# import json

# client = mqtt_client.Client("test_pub")
# client.connect("broker.hivemq.com", 1883)

# data = {
#     "device_id": "D100",
#     "device_name": "Node Tracker",
#     "device_model": "ESP32-GPS",
#     "battery_level": 78,
#     "device_status": "online"
# }

# client.publish("my/devices/D100", json.dumps(data))
# print("✅ Sent:", data)

# from paho.mqtt import client as mqtt_client
# import json
# import time

# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC = "my/devices/D100"

# client = mqtt_client.Client("test_pub")
# client.connect(BROKER, PORT)

# data = {
#     "device_id": "D107",
#     "device_name": "GPS Tracker2",
#     "device_model": "ESP32-GPS",
#     "battery_level": 78,
#     "device_status": "online"
# }

# client.publish(TOPIC, json.dumps(data))
# print("✅ Published:", data)

# # Optional: Wait for network flush
# time.sleep(1)
# client.disconnect()


# from paho.mqtt import client as mqtt_client
# import json
# import time

# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC = "my/devices/D107"   # Must match your subscription pattern: my/devices/#
# CLIENT_ID = "test_pub"

# # Initialize client
# client = mqtt_client.Client(CLIENT_ID)
# client.connect(BROKER, PORT)

# # Payload
# data = {
#     "device_id": "D107",
#     "device_name": "GPS Tracker2",
#     "device_model": "ESP32-GPS",
#     "battery_level": 78,
#     "device_status": "online",
#     "user_id": "user_123"
# }

# # Convert to JSON and publish
# result = client.publish(TOPIC, json.dumps(data))

# # Check if publish was successful
# status = result[0]
# if status == 0:
#     print(f"✅ Published to topic `{TOPIC}`: {data}")
# else:
#     print(f"❌ Failed to send message to topic {TOPIC}")

# # Wait a bit so the message is transmitted before disconnect
# time.sleep(2)

# client.disconnect()
from paho.mqtt import client as mqtt_client
import json
import time
import random
from datetime import datetime

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "my/devices/DEV-1011A"
CLIENT_ID = "test_publisher"

def create_mqtt_client():
    """Create and connect MQTT client"""
    client = mqtt_client.Client(CLIENT_ID)
    client.connect(BROKER, PORT)
    return client

def publish_device_data(client, device_data):
    """Publish device data to MQTT topic"""
    result = client.publish(TOPIC, json.dumps(device_data))
    return result

def generate_test_data(device_id="DEV-1011A"):
    """Generate realistic test device data"""
    return {
        "device_id": device_id,
        "device_name": f"GPS Tracker {device_id}",
        "device_model": "ESP32-GPS",
        "battery_level": random.randint(10, 100),
        "device_status": random.choice(["online", "offline", "sleeping"]),
        "user_id": "user_123",
        "latitude": round(40.7128 + random.uniform(-0.1, 0.1), 6),
        "longitude": round(-74.0060 + random.uniform(-0.1, 0.1), 6),
        "altitude": round(random.uniform(0, 100), 2),
        "speed": round(random.uniform(0, 80), 2),
        "accuracy": round(random.uniform(1, 50), 2),
        "timestamp": datetime.utcnow().isoformat(),
        "hdop": round(random.uniform(0.5, 5.0), 2),
        "satellites": random.randint(4, 12)
    }

def publish_single_message():
    """Publish a single test message"""
    client = create_mqtt_client()
    
    data = generate_test_data()
    result = publish_device_data(client, data)
    
    # Check if publish was successful
    status = result[0]
    if status == 0:
        print(f"✅ Published to topic `{TOPIC}`")
        print(f"📊 Data: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Failed to send message to topic {TOPIC}")
    
    # Wait a bit so the message is transmitted before disconnect
    time.sleep(2)
    client.disconnect()

def publish_multiple_messages(count=5, delay=3):
    """Publish multiple test messages with delay"""
    client = create_mqtt_client()
    
    for i in range(count):
        data = generate_test_data()
        result = publish_device_data(client, data)
        
        status = result[0]
        if status == 0:
            print(f"✅ Message {i+1}/{count} published to `{TOPIC}`")
            print(f"📊 Battery: {data['battery_level']}%, Location: {data['latitude']}, {data['longitude']}")
        else:
            print(f"❌ Failed to send message {i+1} to topic {TOPIC}")
        
        if i < count - 1:  # Don't sleep after the last message
            time.sleep(delay)
    
    client.disconnect()
    print(f"🎉 Finished publishing {count} messages")

def publish_multiple_devices(device_count=3, messages_per_device=2):
    """Publish messages from multiple devices"""
    client = create_mqtt_client()
    
    for device_num in range(1, device_count + 1):
        device_id = f"D{100 + device_num}"  # D101, D102, D103, etc.
        
        for msg_num in range(messages_per_device):
            data = generate_test_data(device_id)
            topic = f"my/devices/{device_id}"
            
            result = client.publish(topic, json.dumps(data))
            
            status = result[0]
            if status == 0:
                print(f"✅ Device {device_id} - Message {msg_num+1} published")
            else:
                print(f"❌ Failed to send message from {device_id}")
            
            time.sleep(1)  # Short delay between messages
    
    client.disconnect()
    print(f"🎉 Finished publishing from {device_count} devices")

if __name__ == "__main__":
    print("🚀 MQTT Test Publisher")
    print("1. Publish single message")
    print("2. Publish multiple messages")
    print("3. Publish from multiple devices")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        publish_single_message()
    elif choice == "2":
        count = int(input("How many messages? (default 5): ") or "5")
        publish_multiple_messages(count)
    elif choice == "3":
        devices = int(input("How many devices? (default 3): ") or "3")
        messages = int(input("Messages per device? (default 2): ") or "2")
        publish_multiple_devices(devices, messages)
    else:
        print("❌ Invalid choice")