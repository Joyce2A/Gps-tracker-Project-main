# from paho.mqtt import client as mqtt_client
# import json
# import time
# import logging
# import asyncio
# from app.database import db
# from datetime import datetime

# logger = logging.getLogger(__name__)

# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC_SUBSCRIBE = "my/devices/#"  # Subscribe to all devices
# CLIENT_ID = "device_subscriber"

# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         logger.info("✅ Connected to MQTT Broker!")
#         client.subscribe(TOPIC_SUBSCRIBE)
#         logger.info(f"📡 Subscribed to topic: {TOPIC_SUBSCRIBE}")
#     else:
#         logger.error(f"❌ Failed to connect, return code {rc}")

# def on_message(client, userdata, msg):
#     logger.info(f"📨 Received message from topic `{msg.topic}`")
#     try:
#         # Parse JSON message
#         data = json.loads(msg.payload.decode())
#         logger.info(f"📊 Parsed data: {data}")
        
#         # Process message in a separate thread to handle async operations
#         import threading
#         thread = threading.Thread(target=process_message, args=(data,))
#         thread.daemon = True
#         thread.start()
        
#     except json.JSONDecodeError as e:
#         logger.error(f"❌ JSON decode error: {e}")
#     except Exception as e:
#         logger.error(f"❌ Error processing message: {e}")

# def process_message(data):
#     """Process message and save to MongoDB"""
#     try:
#         # Since we're in a separate thread, we need to run async code properly
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
        
#         # Run the async save operation
#         loop.run_until_complete(save_to_database(data))
#         loop.close()
        
#     except Exception as e:
#         logger.error(f"❌ Error in process_message: {e}")

# async def save_to_database(data):
#     """Save device data to MongoDB"""
#     try:
#         # Prepare the document with timestamp
#         device_document = {
#             "device_id": data.get("device_id"),
#             "device_name": data.get("device_name"),
#             "device_model": data.get("device_model"),
#             "battery_level": data.get("battery_level"),
#             "device_status": data.get("device_status", "online"),
#             "user_id": data.get("user_id"),
#             "timestamp": datetime.utcnow(),
#             "received_at": datetime.utcnow(),
#             "raw_data": data  # Store original data for debugging
#         }
        
#         # Insert into devices collection
#         result = await db.devices.insert_one(device_document)
#         logger.info(f"💾 Saved to MongoDB with id: {result.inserted_id}")
        
#         # Also save to locations collection if GPS data is present
#         if "latitude" in data and "longitude" in data:
#             location_document = {
#                 "device_id": data.get("device_id"),
#                 "latitude": data.get("latitude"),
#                 "longitude": data.get("longitude"),
#                 "altitude": data.get("altitude"),
#                 "speed": data.get("speed"),
#                 "accuracy": data.get("accuracy"),
#                 "timestamp": datetime.utcnow(),
#                 "user_id": data.get("user_id")
#             }
#             location_result = await db.locations.insert_one(location_document)
#             logger.info(f"📍 Location data saved with id: {location_result.inserted_id}")
            
#         # Check for low battery and create alert
#         battery_level = data.get("battery_level")
#         if battery_level and battery_level < 20:
#             alert_document = {
#                 "device_id": data.get("device_id"),
#                 "alert_type": "low_battery",
#                 "message": f"Battery level is low: {battery_level}%",
#                 "severity": "warning",
#                 "timestamp": datetime.utcnow(),
#                 "user_id": data.get("user_id"),
#                 "resolved": False
#             }
#             await db.alerts.insert_one(alert_document)
#             logger.warning(f"🔋 Low battery alert created for device {data.get('device_id')}")
            
#     except Exception as e:
#         logger.error(f"❌ MongoDB save error: {e}")

# def start_mqtt():
#     """Start the MQTT client listener"""
#     try:
#         client = mqtt_client.Client(CLIENT_ID)
#         client.on_connect = on_connect
#         client.on_message = on_message
        
#         # Add reconnect logic
#         client.reconnect_delay_set(min_delay=1, max_delay=120)
        
#         logger.info(f"🚀 Connecting to MQTT broker {BROKER}:{PORT}...")
#         client.connect(BROKER, PORT)
#         logger.info("📡 Starting MQTT listener loop...")
#         client.loop_forever()  # Keep listening for messages
#     except Exception as e:
#         logger.error(f"❌ MQTT client error: {e}")
#         # Attempt to reconnect after 10 seconds
#         logger.info("🔄 Attempting to reconnect in 10 seconds...")
#         time.sleep(10)
#         start_mqtt()


# from paho.mqtt import client as mqtt_client
# import json
# import time
# import logging
# import asyncio
# from datetime import datetime
# from app.database import db

# logger = logging.getLogger(__name__)

# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC_SUBSCRIBE = "my/devices/#"
# CLIENT_ID = "device_subscriber"

# # ---------- MQTT CALLBACKS ----------
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         logger.info("✅ Connected to MQTT Broker!")
#         client.subscribe(TOPIC_SUBSCRIBE)
#         logger.info(f"📡 Subscribed to topic: {TOPIC_SUBSCRIBE}")
#     else:
#         logger.error(f"❌ Failed to connect, return code {rc}")

# def on_message(client, userdata, msg):
#     logger.info(f"📨 Received message from topic `{msg.topic}`")
#     try:
#         data = json.loads(msg.payload.decode())
#         logger.info(f"📊 Parsed data: {data}")

#         # Process message asynchronously
#         import threading
#         thread = threading.Thread(target=process_message, args=(data,))
#         thread.daemon = True
#         thread.start()

#     except json.JSONDecodeError as e:
#         logger.error(f"❌ JSON decode error: {e}")
#     except Exception as e:
#         logger.error(f"❌ Error processing message: {e}")

# # ---------- PROCESS MESSAGE ----------
# def process_message(data):
#     try:
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         loop.run_until_complete(handle_incoming_data(data))
#         loop.close()
#     except Exception as e:
#         logger.error(f"❌ Error in process_message: {e}")

# # ---------- MAIN LOGIC ----------
# async def handle_incoming_data(data):
#     try:
#         device_id = data.get("device_id")
#         user_id = data.get("user_id")

#         if not device_id:
#             logger.warning("⚠️ Ignoring message: Missing device_id")
#             return

#         # 🧾 Step 1 — Save Full Record in device_history
#         history_doc = {
#             "device_id": device_id,
#             "user_id": user_id,
#             "timestamp": datetime.utcnow(),
#             "raw_data": data
#         }
#         await db.device_history.insert_one(history_doc)
#         logger.info(f"🕒 Saved to device_history for {device_id}")

#         # 🧩 Step 2 — Update or Insert into devices
#         device_update = {
#             "$set": {
#                 "device_name": data.get("device_name"),
#                 "device_model": data.get("device_model"),
#                 "battery_level": data.get("battery_level"),
#                 "device_status": data.get("device_status", "online"),
#                 "last_updated": datetime.utcnow(),
#                 "user_id": user_id
#             }
#         }
#         await db.devices.update_one({"device_id": device_id}, device_update, upsert=True)
#         logger.info(f"📦 Updated devices collection for {device_id}")

#         # 📍 Step 3 — If location data available, store latest
#         if "latitude" in data and "longitude" in data:
#             location_doc = {
#                 "device_id": device_id,
#                 "user_id": user_id,
#                 "latitude": data.get("latitude"),
#                 "longitude": data.get("longitude"),
#                 "altitude": data.get("altitude"),
#                 "speed": data.get("speed"),
#                 "accuracy": data.get("accuracy"),
#                 "timestamp": datetime.utcnow()
#             }
#             await db.locations.insert_one(location_doc)
#             logger.info(f"📍 Location saved for {device_id}")

#         # ⚠️ Step 4 — Battery level check
#         battery_level = data.get("battery_level")
#         if battery_level is not None and battery_level < 20:
#             alert_doc = {
#                 "device_id": device_id,
#                 "user_id": user_id,
#                 "alert_type": "low_battery",
#                 "message": f"Battery low: {battery_level}%",
#                 "severity": "warning",
#                 "timestamp": datetime.utcnow(),
#                 "resolved": False
#             }
#             await db.alerts.insert_one(alert_doc)
#             logger.warning(f"🔋 Low battery alert created for {device_id}")

#     except Exception as e:
#         logger.error(f"❌ Error saving incoming data: {e}")

# # ---------- START MQTT ----------
# def start_mqtt():
#     try:
#         client = mqtt_client.Client(CLIENT_ID)
#         client.on_connect = on_connect
#         client.on_message = on_message

#         client.reconnect_delay_set(min_delay=1, max_delay=120)
#         logger.info(f"🚀 Connecting to MQTT broker {BROKER}:{PORT}...")
#         client.connect(BROKER, PORT)
#         logger.info("📡 Listening for messages...")
#         client.loop_forever()
#     except Exception as e:
#         logger.error(f"❌ MQTT client error: {e}")
#         time.sleep(10)
#         logger.info("🔄 Reconnecting...")
#         start_mqtt()


# from paho.mqtt import client as mqtt_client
# import json
# import time
# import logging
# import asyncio
# from datetime import datetime
# from app.database import db

# logger = logging.getLogger(__name__)

# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC_SUBSCRIBE = "my/devices/#"
# CLIENT_ID = "device_subscriber"

# # --------------------------------------------------
# # PAYLOAD NORMALIZER
# # --------------------------------------------------
# def normalize_payload(payload: dict):
#     return {
#         "device_id": payload.get("device_id"),
#         "battery_level": payload.get("battery") or payload.get("battery_level"),
#         "latitude": payload.get("lat") or payload.get("latitude"),
#         "longitude": payload.get("lon") or payload.get("longitude"),
#         "timestamp": payload.get("time") or datetime.utcnow(),
#         "raw_data": payload
#     }


# # --------------------------------------------------
# # MQTT CALLBACKS
# # --------------------------------------------------
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         logger.info("✅ Connected to MQTT Broker")
#         client.subscribe(TOPIC_SUBSCRIBE)
#         logger.info(f"📡 Subscribed to {TOPIC_SUBSCRIBE}")
#     else:
#         logger.error(f"❌ MQTT connection failed: {rc}")


# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())
#         asyncio.run(process_mqtt_payload(payload))
#     except json.JSONDecodeError:
#         logger.error("❌ Invalid JSON received")
#     except Exception as e:
#         logger.error(f"❌ MQTT message error: {e}")


# # --------------------------------------------------
# # CORE MQTT HANDLER
# # --------------------------------------------------
# async def process_mqtt_payload(payload: dict):
#     try:
#         normalized = normalize_payload(payload)
#         device_id = normalized["device_id"]

#         if not device_id:
#             logger.warning("⚠️ device_id missing — ignoring")
#             return

#         # 🔍 Step 1 — Check device exists
#         device = await db.devices.find_one({"device_id": device_id})

#         # 🧾 Step 2 — Save RAW data always
#         await db.device_history.insert_one({
#             "device_id": device_id,
#             "user_id": device["user_id"] if device else None,
#             "received_at": datetime.utcnow(),
#             "raw_data": payload
#         })

#         # ❌ Step 3 — If device NOT registered → STOP
#         if not device:
#             logger.warning(f"⚠️ Unregistered device {device_id}. Data saved only in history.")
#             return

#         # 🔄 Step 4 — Update devices (NO UPSERT)
#         update_fields = {
#             "device_status": "online",
#             "last_updated": datetime.utcnow()
#         }

#         if normalized["battery_level"] is not None:
#             update_fields["battery_level"] = normalized["battery_level"]

#         await db.devices.update_one(
#             {"device_id": device_id},
#             {"$set": update_fields}
#         )

#         # 📍 Step 5 — Location insert
#         if normalized["latitude"] is not None and normalized["longitude"] is not None:
#             await db.locations.insert_one({
#                 "device_id": device_id,
#                 "user_id": device["user_id"],
#                 "latitude": normalized["latitude"],
#                 "longitude": normalized["longitude"],
#                 "timestamp": normalized["timestamp"]
#             })

#         # ⚠️ Step 6 — Low battery alert
#         if normalized["battery_level"] is not None and normalized["battery_level"] < 20:
#             await db.alerts.insert_one({
#                 "device_id": device_id,
#                 "user_id": device["user_id"],
#                 "alert_type": "low_battery",
#                 "message": f"Battery low: {normalized['battery_level']}%",
#                 "severity": "warning",
#                 "created_at": datetime.utcnow(),
#                 "resolved": False
#             })

#         logger.info(f"✅ Processed data for device {device_id}")

#     except Exception as e:
#         logger.exception(f"🔥 Error processing MQTT payload: {e}")


# # --------------------------------------------------
# # START MQTT CLIENT
# # --------------------------------------------------
# def start_mqtt():
#     while True:
#         try:
#             client = mqtt_client.Client(CLIENT_ID)
#             client.on_connect = on_connect
#             client.on_message = on_message
#             client.connect(BROKER, PORT)
#             client.loop_forever()
#         except Exception as e:
#             logger.error(f"❌ MQTT error: {e}")
#             time.sleep(5)

# from paho.mqtt import client as mqtt_client
# import json
# import time
# import logging
# import asyncio
# import threading
# from datetime import datetime
# from app.database import db

# # --------------------------------------------------
# # CONFIG
# # --------------------------------------------------
# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC_SUBSCRIBE = "my/devices/#"
# CLIENT_ID = "device_subscriber"

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("Mqtt_client")

# # --------------------------------------------------
# # GLOBAL EVENT LOOP (🔥 VERY IMPORTANT)
# # --------------------------------------------------
# event_loop = asyncio.new_event_loop()
# asyncio.set_event_loop(event_loop)

# def start_event_loop():
#     event_loop.run_forever()

# threading.Thread(target=start_event_loop, daemon=True).start()

# # --------------------------------------------------
# # PAYLOAD NORMALIZER
# # --------------------------------------------------
# def normalize_payload(payload: dict):
#     return {
#         "device_id": payload.get("device_id"),
#         "battery_level": payload.get("battery") or payload.get("battery_level"),
#         "latitude": payload.get("lat") or payload.get("latitude"),
#         "longitude": payload.get("lon") or payload.get("longitude"),
#         "timestamp": payload.get("time") or datetime.utcnow(),
#         "raw_data": payload
#     }

# # --------------------------------------------------
# # MQTT CALLBACKS
# # --------------------------------------------------
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         logger.info("✅ Connected to MQTT Broker")
#         client.subscribe(TOPIC_SUBSCRIBE)
#         logger.info(f"📡 Subscribed to {TOPIC_SUBSCRIBE}")
#     else:
#         logger.error(f"❌ MQTT connection failed: {rc}")

# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())

#         # ✅ SAFE async execution
#         asyncio.run_coroutine_threadsafe(
#             process_mqtt_payload(payload),
#             event_loop
#         )

#     except json.JSONDecodeError:
#         logger.error("❌ Invalid JSON received")
#     except Exception as e:
#         logger.exception(f"❌ MQTT message error: {e}")

# # --------------------------------------------------
# # CORE MQTT HANDLER (ASYNC)
# # --------------------------------------------------
# async def process_mqtt_payload(payload: dict):
#     try:
#         normalized = normalize_payload(payload)
#         device_id = normalized["device_id"]

#         if not device_id:
#             logger.warning("⚠️ device_id missing — ignoring")
#             return

#         # 🔍 Step 1 — Check device exists
#         device = await db.devices.find_one({"device_id": device_id})

#         # 🧾 Step 2 — Save RAW history ALWAYS
#         await db.device_history.insert_one({
#             "device_id": device_id,
#             "user_id": device["user_id"] if device else None,
#             "received_at": datetime.utcnow(),
#             "raw_data": payload
#         })

#         # ❌ Step 3 — Stop if unregistered device
#         if not device:
#             logger.warning(f"⚠️ Unregistered device {device_id}. Saved only in history.")
#             return

#         # 🔄 Step 4 — Update devices (NO UPSERT)
#         update_fields = {
#             "device_status": "online",
#             "last_updated": datetime.utcnow()
#         }

#         if normalized["battery_level"] is not None:
#             update_fields["battery_level"] = normalized["battery_level"]

#         await db.devices.update_one(
#             {"device_id": device_id},
#             {"$set": update_fields}
#         )

#         # 📍 Step 5 — Save location
#         if normalized["latitude"] is not None and normalized["longitude"] is not None:
#             await db.locations.insert_one({
#                 "device_id": device_id,
#                 "user_id": device["user_id"],
#                 "latitude": normalized["latitude"],
#                 "longitude": normalized["longitude"],
#                 "timestamp": normalized["timestamp"]
#             })

#         # ⚠️ Step 6 — Low battery alert
#         if normalized["battery_level"] is not None and normalized["battery_level"] < 20:
#             await db.alerts.insert_one({
#                 "device_id": device_id,
#                 "user_id": device["user_id"],
#                 "alert_type": "low_battery",
#                 "message": f"Battery low: {normalized['battery_level']}%",
#                 "severity": "warning",
#                 "created_at": datetime.utcnow(),
#                 "resolved": False
#             })

#         logger.info(f"✅ Processed data for device {device_id}")

#     except Exception:
#         logger.exception("🔥 Error processing MQTT payload")

# # --------------------------------------------------
# # START MQTT CLIENT
# # --------------------------------------------------
# def start_mqtt():
#     while True:
#         try:
#             client = mqtt_client.Client(CLIENT_ID)
#             client.on_connect = on_connect
#             client.on_message = on_message
#             client.connect(BROKER, PORT)
#             client.loop_forever()

#         except Exception as e:
#             logger.error(f"❌ MQTT error: {e}")
#             time.sleep(5)

# import asyncio
# import json
# import logging
# from datetime import datetime

# from paho.mqtt import client as mqtt_client
# from app.database import db

# # --------------------------------------------------
# # LOGGING
# # --------------------------------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("Mqtt_client")

# # --------------------------------------------------
# # MQTT CONFIG
# # --------------------------------------------------
# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC_SUBSCRIBE = "my/devices/#"
# CLIENT_ID = "device_subscriber"

# # --------------------------------------------------
# # ASYNC PAYLOAD PROCESSOR
# # --------------------------------------------------
# async def process_mqtt_payload(payload: dict):
#     """
#     Process MQTT payload:
#     - Save raw data to device_history
#     - Upsert device in devices collection
#     - Save location if present
#     - Create low battery alert
#     """
#     try:
#         # 1️⃣ Normalize payload
#         device_id = str(payload.get("device_id"))
#         if not device_id:
#             logger.warning("⚠️ device_id missing in payload")
#             return

#         normalized = {
#             "device_id": device_id,
#             "battery_level": payload.get("battery"),
#             "latitude": payload.get("lat"),
#             "longitude": payload.get("lon"),
#             "user_id": payload.get("user_id"),
#             "raw_data": payload
#         }

#         now = datetime.utcnow()

#         # 2️⃣ Save device history
#         await db.device_history.insert_one({
#             "device_id": device_id,
#             "received_at": now,
#             "raw_data": payload
#         })

#         # 3️⃣ Upsert devices
#         result = await db.devices.update_one(
#             {"device_id": device_id},
#             {
#                 "$set": {
#                     "device_status": "online",
#                     "battery_level": normalized["battery_level"],
#                     "last_seen": now
#                 },
#                 "$setOnInsert": {
#                     "created_at": now,
#                     "user_id": normalized.get("user_id")
#                 }
#             },
#             upsert=True
#         )

#         if result.matched_count:
#             logger.info(f"✅ Updated device {device_id}")
#         elif result.upserted_id:
#             logger.info(f"➕ Inserted new device {device_id}")

#         # 4️⃣ Save location if lat/lon present
#         if normalized["latitude"] is not None and normalized["longitude"] is not None:
#             await db.locations.insert_one({
#                 "device_id": device_id,
#                 "latitude": normalized["latitude"],
#                 "longitude": normalized["longitude"],
#                 "timestamp": now,
#                 "user_id": normalized.get("user_id")
#             })

#         # 5️⃣ Low battery alert
#         if normalized["battery_level"] is not None and normalized["battery_level"] < 20:
#             await db.alerts.insert_one({
#                 "device_id": device_id,
#                 "user_id": normalized.get("user_id"),
#                 "alert_type": "low_battery",
#                 "message": f"Battery low: {normalized['battery_level']}%",
#                 "severity": "warning",
#                 "created_at": now,
#                 "resolved": False
#             })
#             logger.warning(f"🔋 Low battery alert created for device {device_id}")

#         logger.info(f"✅ Processed payload for device {device_id}")

#     except Exception:
#         logger.exception("🔥 Error processing MQTT payload")


# # --------------------------------------------------
# # MQTT CALLBACKS
# # --------------------------------------------------
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         logger.info("✅ Connected to MQTT Broker")
#         client.subscribe(TOPIC_SUBSCRIBE)
#         logger.info(f"📡 Subscribed to {TOPIC_SUBSCRIBE}")
#     else:
#         logger.error(f"❌ MQTT connection failed: {rc}")


# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())
#         logger.info(f"📨 {msg.topic} → {payload}")

#         # Schedule payload processing in the same asyncio loop
#         loop = asyncio.get_running_loop()
#         loop.create_task(process_mqtt_payload(payload))

#     except Exception:
#         logger.exception("❌ Error in on_message callback")


# # --------------------------------------------------
# # ASYNC MQTT STARTER
# # --------------------------------------------------
# async def start_mqtt():
#     """
#     Start MQTT client and run it asynchronously in FastAPI
#     """
#     client = mqtt_client.Client(CLIENT_ID)
#     client.on_connect = on_connect
#     client.on_message = on_message

#     logger.info(f"🚀 Connecting to MQTT Broker {BROKER}:{PORT}...")
#     client.connect(BROKER, PORT)

#     # Run MQTT loop in executor (non-blocking)
#     loop = asyncio.get_running_loop()
#     await loop.run_in_executor(None, client.loop_forever)


# # --------------------------------------------------
# # USAGE IN FASTAPI
# # --------------------------------------------------
# # In your main.py / FastAPI startup event:
# #
# # @app.on_event("startup")
# # async def startup_event():
# #     await init_db()  # Ensure DB indexes
# #     asyncio.create_task(start_mqtt())  # Start MQTT in the same event loop
# #
# # No threading needed. Fully async-safe.

# import asyncio
# import json
# import logging
# from datetime import datetime

# from paho.mqtt import client as mqtt_client
# from app.database import db

# # --------------------------------------------------
# # LOGGING
# # --------------------------------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("Mqtt_client")

# # --------------------------------------------------
# # MQTT CONFIG
# # --------------------------------------------------
# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC_SUBSCRIBE = "my/devices/#"
# CLIENT_ID = "device_subscriber"

# # --------------------------------------------------
# # GLOBAL STATE
# # --------------------------------------------------
# MAIN_EVENT_LOOP: asyncio.AbstractEventLoop | None = None
# MQTT_STARTED = False   # 🔒 prevent multiple starts

# # --------------------------------------------------
# # ASYNC PAYLOAD PROCESSOR
# # --------------------------------------------------
# async def process_mqtt_payload(payload: dict):
#     try:
#         device_id = payload.get("device_id")
#         if not device_id:
#             logger.warning("⚠️ device_id missing")
#             return

#         device_id = str(device_id)
#         now = datetime.utcnow()

#         # 1️⃣ DEVICE HISTORY (ALWAYS)
#         await db.device_history.insert_one({
#             "device_id": device_id,
#             "received_at": now,
#             "raw_data": payload
#         })

#         # 2️⃣ DEVICE UPSERT
#         await db.devices.update_one(
#             {"device_id": device_id},
#             {
#                 "$set": {
#                     "device_status": "online",
#                     "battery_level": payload.get("battery"),
#                     "last_seen": now
#                 },
#                 "$setOnInsert": {
#                     "created_at": now,
#                     "user_id": payload.get("user_id")
#                 }
#             },
#             upsert=True
#         )

#         # 3️⃣ LOCATION
#         if payload.get("lat") is not None and payload.get("lon") is not None:
#             await db.locations.insert_one({
#                 "device_id": device_id,
#                 "latitude": payload.get("lat"),
#                 "longitude": payload.get("lon"),
#                 "timestamp": now,
#                 "user_id": payload.get("user_id")
#             })

#         # 4️⃣ LOW BATTERY ALERT
#         battery = payload.get("battery")
#         if battery is not None and battery < 20:
#             await db.alerts.insert_one({
#                 "device_id": device_id,
#                 "alert_type": "low_battery",
#                 "message": f"Battery low: {battery}%",
#                 "severity": "warning",
#                 "created_at": now,
#                 "resolved": False
#             })
#             logger.warning(f"🔋 Low battery alert for {device_id}")

#         logger.info(f"✅ Processed device {device_id}")

#     except Exception:
#         logger.exception("🔥 Error processing MQTT payload")

# # --------------------------------------------------
# # MQTT CALLBACKS (RUNS IN MQTT THREAD)
# # --------------------------------------------------
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         logger.info("✅ Connected to MQTT Broker")
#         client.subscribe(TOPIC_SUBSCRIBE)
#         logger.info(f"📡 Subscribed to {TOPIC_SUBSCRIBE}")
#     else:
#         logger.error(f"❌ MQTT connection failed: {rc}")

# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())
#         logger.info(f"📨 {msg.topic} → {payload}")

#         if MAIN_EVENT_LOOP is None or MAIN_EVENT_LOOP.is_closed():
#             logger.error("❌ Event loop not available, skipping message")
#             return

#         asyncio.run_coroutine_threadsafe(
#             process_mqtt_payload(payload),
#             MAIN_EVENT_LOOP
#         )

#     except Exception:
#         logger.exception("❌ MQTT message error")

# # --------------------------------------------------
# # MQTT STARTER (ASYNC – CALLED FROM FASTAPI)
# # --------------------------------------------------
# async def start_mqtt():
#     global MAIN_EVENT_LOOP, MQTT_STARTED

#     if MQTT_STARTED:
#         logger.warning("⚠️ MQTT already running, skipping")
#         return

#     MQTT_STARTED = True
#     MAIN_EVENT_LOOP = asyncio.get_running_loop()

#     client = mqtt_client.Client(CLIENT_ID)
#     client.on_connect = on_connect
#     client.on_message = on_message

#     logger.info(f"🚀 Connecting to MQTT Broker {BROKER}:{PORT}")
#     client.connect(BROKER, PORT)

#     # Run MQTT network loop without blocking FastAPI
#     await asyncio.to_thread(client.loop_forever)

# import asyncio
# import json
# import logging
# from datetime import datetime
# from queue import Queue, Empty
# from threading import Thread

# from paho.mqtt import client as mqtt_client
# from app.database import db

# # --------------------------------------------------
# # LOGGING
# # --------------------------------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("Mqtt_client")

# # --------------------------------------------------
# # MQTT CONFIG
# # --------------------------------------------------
# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC_SUBSCRIBE = "my/devices/#"
# CLIENT_ID = "device_subscriber"

# # --------------------------------------------------
# # GLOBAL STATE
# # --------------------------------------------------
# MESSAGE_QUEUE: Queue = Queue(maxsize=10000)
# MAIN_EVENT_LOOP: asyncio.AbstractEventLoop | None = None
# MQTT_STARTED = False

# # --------------------------------------------------
# # ASYNC PAYLOAD PROCESSOR (UNCHANGED LOGIC)
# # --------------------------------------------------
# async def process_mqtt_payload(payload: dict):
#     try:
#         device_id = payload.get("device_id")
#         if not device_id:
#             logger.warning("⚠️ device_id missing")
#             return

#         device_id = str(device_id)
#         now = datetime.utcnow()

#         # 1️⃣ HISTORY
#         await db.device_history.insert_one({
#             "device_id": device_id,
#             "received_at": now,
#             "raw_data": payload
#         })

#         # 2️⃣ DEVICE UPSERT
#         await db.devices.update_one(
#             {"device_id": device_id},
#             {
#                 "$set": {
#                     "device_status": "online",
#                     "battery_level": payload.get("battery"),
#                     "last_seen": now
#                 },
#                 "$setOnInsert": {
#                     "created_at": now,
#                     "user_id": payload.get("user_id")
#                 }
#             },
#             upsert=True
#         )

#         # 3️⃣ LOCATION
#         if payload.get("lat") is not None and payload.get("lon") is not None:
#             await db.locations.insert_one({
#                 "device_id": device_id,
#                 "latitude": payload.get("lat"),
#                 "longitude": payload.get("lon"),
#                 "timestamp": now,
#                 "user_id": payload.get("user_id")
#             })

#         # 4️⃣ ALERT
#         battery = payload.get("battery")
#         if battery is not None and battery < 20:
#             await db.alerts.insert_one({
#                 "device_id": device_id,
#                 "alert_type": "low_battery",
#                 "message": f"Battery low: {battery}%",
#                 "severity": "warning",
#                 "created_at": now,
#                 "resolved": False
#             })
#             logger.warning(f"🔋 Low battery alert for {device_id}")

#         logger.info(f"✅ Processed device {device_id}")

#     except Exception:
#         logger.exception("🔥 Error processing MQTT payload")

# # --------------------------------------------------
# # QUEUE WORKER (ASYNC)
# # --------------------------------------------------
# async def queue_worker():
#     while True:
#         try:
#             payload = MESSAGE_QUEUE.get_nowait()
#             await process_mqtt_payload(payload)
#         except Empty:
#             await asyncio.sleep(0.01)
#         except Exception:
#             logger.exception("❌ Worker error")

# # --------------------------------------------------
# # MQTT CALLBACKS (FAST & SAFE)
# # --------------------------------------------------
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         logger.info("✅ Connected to MQTT Broker")
#         client.subscribe(TOPIC_SUBSCRIBE)
#         logger.info(f"📡 Subscribed to {TOPIC_SUBSCRIBE}")
#     else:
#         logger.error(f"❌ MQTT connection failed: {rc}")

# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())
#         logger.info(f"📨 {msg.topic} → {payload}")

#         # ⚡ VERY FAST (no async calls here)
#         MESSAGE_QUEUE.put_nowait(payload)

#     except Exception:
#         logger.exception("❌ MQTT message error")

# # --------------------------------------------------
# # MQTT STARTER
# # --------------------------------------------------
# async def start_mqtt():
#     global MAIN_EVENT_LOOP, MQTT_STARTED

#     if MQTT_STARTED:
#         logger.warning("⚠️ MQTT already running")
#         return

#     MQTT_STARTED = True
#     MAIN_EVENT_LOOP = asyncio.get_running_loop()

#     # Start async workers
#     for _ in range(4):
#         asyncio.create_task(queue_worker())

#     client = mqtt_client.Client(CLIENT_ID)
#     client.on_connect = on_connect
#     client.on_message = on_message

#     logger.info(f"🚀 Connecting to MQTT Broker {BROKER}:{PORT}")
#     client.connect(BROKER, PORT)

#     # Run MQTT loop in separate thread
#     Thread(target=client.loop_forever, daemon=True).start()


# import asyncio
# import json
# import logging
# from datetime import datetime
# from queue import Queue, Empty
# from threading import Thread

# from paho.mqtt import client as mqtt_client
# from app.database import db

# # --------------------------------------------------
# # LOGGING
# # --------------------------------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("Mqtt_client")

# # --------------------------------------------------
# # MQTT CONFIG
# # --------------------------------------------------
# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC_SUBSCRIBE = "my/devices/#"
# CLIENT_ID = "device_subscriber"

# # --------------------------------------------------
# # GLOBAL STATE
# # --------------------------------------------------
# MESSAGE_QUEUE: Queue = Queue(maxsize=10000)
# MAIN_EVENT_LOOP: asyncio.AbstractEventLoop | None = None
# MQTT_STARTED = False

# # --------------------------------------------------
# # ASYNC PAYLOAD PROCESSOR
# # --------------------------------------------------
# async def process_mqtt_payload(payload: dict):
#     try:
#         device_id = payload.get("device_id")
#         if not device_id:
#             logger.warning("⚠️ device_id missing")
#             return

#         device_id = str(device_id)
#         now = datetime.utcnow()

#         # --------------------------------------------------
#         # 1️⃣ DEVICE LOOKUP (🔧 STEP 3.1 FIX)
#         # --------------------------------------------------
#         device = await db.devices.find_one(
#             {"device_id": device_id},
#             {"user_id": 1}
#         )
#         user_id = device["user_id"] if device else None

#         # --------------------------------------------------
#         # 2️⃣ HISTORY
#         # --------------------------------------------------
#         await db.device_history.insert_one({
#             "device_id": device_id,
#             "received_at": now,
#             "raw_data": payload
#         })

#         # --------------------------------------------------
#         # 3️⃣ DEVICE UPSERT
#         # --------------------------------------------------
#         await db.devices.update_one(
#             {"device_id": device_id},
#             {
#                 "$set": {
#                     "device_status": "online",
#                     "battery_level": payload.get("battery"),
#                     "last_seen": now
#                 },
#                 "$setOnInsert": {
#                     "created_at": now,
#                     "user_id": user_id
#                 }
#             },
#             upsert=True
#         )

#         # --------------------------------------------------
#         # 4️⃣ LOCATION (🔧 user_id FIXED)
#         # --------------------------------------------------
#         if payload.get("lat") is not None and payload.get("lon") is not None:
#             await db.locations.insert_one({
#                 "device_id": device_id,
#                 "latitude": payload.get("lat"),
#                 "longitude": payload.get("lon"),
#                 "timestamp": now,
#                 "user_id": user_id
#             })

#         # --------------------------------------------------
#         # 5️⃣ ALERT
#         # --------------------------------------------------
#         battery = payload.get("battery")
#         if battery is not None and battery < 20:
#             await db.alerts.insert_one({
#                 "device_id": device_id,
#                 "alert_type": "low_battery",
#                 "message": f"Battery low: {battery}%",
#                 "severity": "warning",
#                 "created_at": now,
#                 "resolved": False
#             })
#             logger.warning(f"🔋 Low battery alert for {device_id}")

#         logger.info(
#             f"✅ Location saved | device={device_id}, user={user_id}"
#         )

#     except Exception:
#         logger.exception("🔥 Error processing MQTT payload")

# # --------------------------------------------------
# # QUEUE WORKER
# # --------------------------------------------------
# async def queue_worker():
#     while True:
#         try:
#             payload = MESSAGE_QUEUE.get_nowait()
#             await process_mqtt_payload(payload)
#         except Empty:
#             await asyncio.sleep(0.01)
#         except Exception:
#             logger.exception("❌ Worker error")

# # --------------------------------------------------
# # MQTT CALLBACKS
# # --------------------------------------------------
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         logger.info("✅ Connected to MQTT Broker")
#         client.subscribe(TOPIC_SUBSCRIBE)
#         logger.info(f"📡 Subscribed to {TOPIC_SUBSCRIBE}")
#     else:
#         logger.error(f"❌ MQTT connection failed: {rc}")

# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())
#         logger.info(f"📨 {msg.topic} → {payload}")
#         MESSAGE_QUEUE.put_nowait(payload)
#     except Exception:
#         logger.exception("❌ MQTT message error")

# # --------------------------------------------------
# # MQTT STARTER
# # --------------------------------------------------
# async def start_mqtt():
#     global MAIN_EVENT_LOOP, MQTT_STARTED

#     if MQTT_STARTED:
#         logger.warning("⚠️ MQTT already running")
#         return

#     MQTT_STARTED = True
#     MAIN_EVENT_LOOP = asyncio.get_running_loop()

#     for _ in range(4):
#         asyncio.create_task(queue_worker())

#     client = mqtt_client.Client(CLIENT_ID)
#     client.on_connect = on_connect
#     client.on_message = on_message

#     logger.info(f"🚀 Connecting to MQTT Broker {BROKER}:{PORT}")
#     client.connect(BROKER, PORT)

#     Thread(target=client.loop_forever, daemon=True).start()


# import asyncio
# import json
# import logging
# from datetime import datetime
# from queue import Queue, Empty
# from threading import Thread

# from paho.mqtt import client as mqtt_client
# from app.database import db

# # --------------------------------------------------
# # LOGGING
# # --------------------------------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("Mqtt_client")

# # --------------------------------------------------
# # MQTT CONFIG
# # --------------------------------------------------
# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC_SUBSCRIBE = "my/devices/#"
# CLIENT_ID = "device_subscriber"

# # --------------------------------------------------
# # GLOBAL STATE
# # --------------------------------------------------
# MESSAGE_QUEUE: Queue = Queue(maxsize=10000)
# MAIN_EVENT_LOOP: asyncio.AbstractEventLoop | None = None
# MQTT_STARTED = False

# # --------------------------------------------------
# # ASYNC PAYLOAD PROCESSOR
# # --------------------------------------------------
# async def process_mqtt_payload(payload: dict):
#     try:
#         # --------------------------------------------------
#         # 0️⃣ DEVICE ID VALIDATION
#         # --------------------------------------------------
#         device_id = payload.get("device_id")
#         if not device_id:
#             logger.warning("⚠️ device_id missing")
#             return

#         device_id = str(device_id)
#         now = datetime.utcnow()

#         # --------------------------------------------------
#         # 1️⃣ DEVICE LOOKUP (user_id FIX)
#         # --------------------------------------------------
#         device = await db.devices.find_one(
#             {"device_id": device_id},
#             {"user_id": 1}
#         )
#         user_id = device["user_id"] if device else None

#         # --------------------------------------------------
#         # 2️⃣ DEVICE HISTORY (RAW DATA)
#         # --------------------------------------------------
#         await db.device_history.insert_one({
#             "device_id": device_id,
#             "received_at": now,
#             "raw_data": payload
#         })

#         # --------------------------------------------------
#         # 3️⃣ DEVICE UPSERT
#         # --------------------------------------------------
#         await db.devices.update_one(
#             {"device_id": device_id},
#             {
#                 "$set": {
#                     "device_status": "online",
#                     "battery_level": payload.get("battery"),
#                     "last_seen": now
#                 },
#                 "$setOnInsert": {
#                     "created_at": now,
#                     "user_id": user_id
#                 }
#             },
#             upsert=True
#         )

#         # --------------------------------------------------
#         # 4️⃣ LOCATION SAVE (SINGLE SOURCE OF TRUTH)
#         # --------------------------------------------------
#         if payload.get("lat") is not None and payload.get("lon") is not None:
#             await db.locations.insert_one({
#                 "device_id": device_id,
#                 "latitude": payload.get("lat"),
#                 "longitude": payload.get("lon"),
#                 "timestamp": now,
#                 "user_id": user_id
#             })
#         else:
#             logger.info(f"ℹ️ No GPS coordinates for device {device_id}")
#             return

#         # --------------------------------------------------
#         # 5️⃣ ASSET LINK CHECK (STEP 3.2 ✅)
#         # --------------------------------------------------
#         asset_link = await db.asset_device_links.find_one({
#             "device_id": device_id,
#             "status": "active"
#         })

#         if not asset_link:
#             logger.info(f"ℹ️ No active asset linked for device {device_id}")
#             return

#         asset_id = asset_link["asset_id"]
#         logger.info(f"🚗 Device {device_id} belongs to asset {asset_id}")

#         # 🔴 STOP HERE FOR NOW
#         # Step 3.3 (distance / geofence) next

#         # --------------------------------------------------
#         # 6️⃣ LOW BATTERY ALERT (EXISTING LOGIC)
#         # --------------------------------------------------
#         battery = payload.get("battery")
#         if battery is not None and battery < 20:
#             await db.alerts.insert_one({
#                 "device_id": device_id,
#                 "alert_type": "low_battery",
#                 "message": f"Battery low: {battery}%",
#                 "severity": "warning",
#                 "created_at": now,
#                 "resolved": False
#             })
#             logger.warning(f"🔋 Low battery alert for {device_id}")

#         logger.info(
#             f"✅ Processed | device={device_id}, asset={asset_id}, user={user_id}"
#         )

#     except Exception:
#         logger.exception("🔥 Error processing MQTT payload")

# # --------------------------------------------------
# # QUEUE WORKER
# # --------------------------------------------------
# async def queue_worker():
#     while True:
#         try:
#             payload = MESSAGE_QUEUE.get_nowait()
#             await process_mqtt_payload(payload)
#         except Empty:
#             await asyncio.sleep(0.01)
#         except Exception:
#             logger.exception("❌ Worker error")

# # --------------------------------------------------
# # MQTT CALLBACKS
# # --------------------------------------------------
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         logger.info("✅ Connected to MQTT Broker")
#         client.subscribe(TOPIC_SUBSCRIBE)
#         logger.info(f"📡 Subscribed to {TOPIC_SUBSCRIBE}")
#     else:
#         logger.error(f"❌ MQTT connection failed: {rc}")

# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())
#         logger.info(f"📨 {msg.topic} → {payload}")
#         MESSAGE_QUEUE.put_nowait(payload)
#     except Exception:
#         logger.exception("❌ MQTT message error")

# # --------------------------------------------------
# # MQTT STARTER
# # --------------------------------------------------
# async def start_mqtt():
#     global MAIN_EVENT_LOOP, MQTT_STARTED

#     if MQTT_STARTED:
#         logger.warning("⚠️ MQTT already running")
#         return

#     MQTT_STARTED = True
#     MAIN_EVENT_LOOP = asyncio.get_running_loop()

#     for _ in range(4):
#         asyncio.create_task(queue_worker())

#     client = mqtt_client.Client(CLIENT_ID)
#     client.on_connect = on_connect
#     client.on_message = on_message

#     logger.info(f"🚀 Connecting to MQTT Broker {BROKER}:{PORT}")
#     client.connect(BROKER, PORT)

#     Thread(target=client.loop_forever, daemon=True).start()



# import asyncio
# import json
# import logging
# from datetime import datetime
# from queue import Queue, Empty
# from threading import Thread

# from paho.mqtt import client as mqtt_client
# from app.database import db
# from app.services.geofence_service import check_geofence




# # --------------------------------------------------
# # LOGGING
# # --------------------------------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("Mqtt_client")

# # --------------------------------------------------
# # MQTT CONFIG
# # --------------------------------------------------
# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC_SUBSCRIBE = "my/devices/#"
# CLIENT_ID = "device_subscriber"

# # --------------------------------------------------
# # GLOBAL STATE
# # --------------------------------------------------
# MESSAGE_QUEUE: Queue = Queue(maxsize=10000)
# MAIN_EVENT_LOOP: asyncio.AbstractEventLoop | None = None
# MQTT_STARTED = False

# # --------------------------------------------------
# # ASYNC PAYLOAD PROCESSOR
# # --------------------------------------------------
# async def process_mqtt_payload(payload: dict):
#     try:
#         # --------------------------------------------------
#         # 0️⃣ DEVICE ID VALIDATION
#         # --------------------------------------------------
#         device_id = payload.get("device_id")
#         if not device_id:
#             logger.warning("⚠️ device_id missing")
#             return

#         device_id = str(device_id)
#         now = datetime.utcnow()

#         # --------------------------------------------------
#         # 1️⃣ DEVICE LOOKUP
#         # --------------------------------------------------
#         device = await db.devices.find_one(
#             {"device_id": device_id},
#             {"user_id": 1}
#         )
#         user_id = device["user_id"] if device else None

#         # --------------------------------------------------
#         # 2️⃣ DEVICE HISTORY
#         # --------------------------------------------------
#         await db.device_history.insert_one({
#             "device_id": device_id,
#             "received_at": now,
#             "raw_data": payload
#         })

#         # --------------------------------------------------
#         # 3️⃣ DEVICE UPSERT
#         # --------------------------------------------------
#         await db.devices.update_one(
#             {"device_id": device_id},
#             {
#                 "$set": {
#                     "device_status": "online",
#                     "battery_level": payload.get("battery"),
#                     "last_seen": now
#                 },
#                 "$setOnInsert": {
#                     "created_at": now,
#                     "user_id": user_id
#                 }
#             },
#             upsert=True
#         )

#         # --------------------------------------------------
#         # 4️⃣ LOCATION SAVE
#         # --------------------------------------------------
#         lat = payload.get("lat")
#         lon = payload.get("lon")

#         if lat is None or lon is None:
#             logger.info(f"ℹ️ No GPS coordinates for device {device_id}")
#             return

#         await db.locations.insert_one({
#             "device_id": device_id,
#             "latitude": lat,
#             "longitude": lon,
#             "timestamp": now,
#             "user_id": user_id
#         })

#         # --------------------------------------------------
#         # 5️⃣ ASSET LINK CHECK
#         # --------------------------------------------------
#         asset_link = await db.asset_device_links.find_one({
#             "device_id": device_id,
#             "status": "active"
#         })

#         if not asset_link:
#             logger.info(f"ℹ️ No active asset linked for device {device_id}")
#             return

#         asset_id = asset_link["asset_id"]
#         logger.info(f"🚗 Device {device_id} belongs to asset {asset_id}")

#         # --------------------------------------------------
#         # 6️⃣ FETCH ASSET BASE LOCATION (GEOFENCE)
#         # --------------------------------------------------
#         asset = await db.assets.find_one(
#             {"asset_id": asset_id},
#             {"registered_location": 1}
#         )

#         if not asset or "registered_location" not in asset:
#             logger.warning(f"⚠️ No geofence configured for asset {asset_id}")
#             return

#         geo = asset["registered_location"]

#         base_lat = geo.get("latitude")
#         base_lon = geo.get("longitude")
#         radius = geo.get("radius", 0)

#         if base_lat is None or base_lon is None or radius <= 0:
#             logger.warning(f"⚠️ Invalid geofence data for asset {asset_id}")
#             return

#         # --------------------------------------------------
#         # 7️⃣ GEOFENCE CHECK
#         geo_result = check_geofence(
#             payload["lat"],
#             payload["lon"],
#             asset["registered_location"]["latitude"],
#             asset["registered_location"]["longitude"],
#             asset["registered_location"]["radius"]
#         )


#         # # --------------------------------------------------
#         # geo_result = check_geofence(
#         #     device_lat=lat,
#         #     device_lon=lon,
#         #     geofence_lat=base_lat,
#         #     geofence_lon=base_lon,
#         #     radius_meters=radius
#         # )

#         inside = geo_result["inside"]
#         distance = geo_result["distance_meters"]

#         logger.info(
#             f"📍 Asset {asset_id} | Distance={distance}m | Inside={inside}"
#         )

#         # --------------------------------------------------
#         # 8️⃣ SAVE ASSET STATUS (LIVE)
#         # --------------------------------------------------
#         await db.asset_status.update_one(
#             {"asset_id": asset_id},
#             {
#                 "$set": {
#                     "device_id": device_id,
#                     "last_lat": lat,
#                     "last_lon": lon,
#                     "distance_from_base": distance,
#                     "inside_geofence": inside,
#                     "updated_at": now
#                 }
#             },
#             upsert=True
#         )

#         # --------------------------------------------------
#         # 9️⃣ GEOFENCE BREACH ALERT
#         # --------------------------------------------------
#         if not inside:
#             await db.alerts.insert_one({
#                 "asset_id": asset_id,
#                 "device_id": device_id,
#                 "alert_type": "geofence_breach",
#                 "message": f"Asset {asset_id} moved outside base radius ({distance}m)",
#                 "severity": "critical",
#                 "created_at": now,
#                 "resolved": False
#             })

#             logger.warning(
#                 f"🚨 GEOFENCE BREACH | Asset {asset_id} | {distance} meters"
#             )

#         # --------------------------------------------------
#         # 🔋 LOW BATTERY ALERT
#         # --------------------------------------------------
#         battery = payload.get("battery")
#         if battery is not None and battery < 20:
#             await db.alerts.insert_one({
#                 "device_id": device_id,
#                 "alert_type": "low_battery",
#                 "message": f"Battery low: {battery}%",
#                 "severity": "warning",
#                 "created_at": now,
#                 "resolved": False
#             })
#             logger.warning(f"🔋 Low battery alert for {device_id}")

#         logger.info(
#             f"✅ Processed | device={device_id}, asset={asset_id}, user={user_id}"
#         )

#     except Exception:
#         logger.exception("🔥 Error processing MQTT payload")

# # --------------------------------------------------
# # QUEUE WORKER
# # --------------------------------------------------
# async def queue_worker():
#     while True:
#         try:
#             payload = MESSAGE_QUEUE.get_nowait()
#             await process_mqtt_payload(payload)
#         except Empty:
#             await asyncio.sleep(0.01)
#         except Exception:
#             logger.exception("❌ Worker error")

# # --------------------------------------------------
# # MQTT CALLBACKS
# # --------------------------------------------------
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         logger.info("✅ Connected to MQTT Broker")
#         client.subscribe(TOPIC_SUBSCRIBE)
#         logger.info(f"📡 Subscribed to {TOPIC_SUBSCRIBE}")
#     else:
#         logger.error(f"❌ MQTT connection failed: {rc}")

# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())
#         logger.info(f"📨 {msg.topic} → {payload}")
#         MESSAGE_QUEUE.put_nowait(payload)
#     except Exception:
#         logger.exception("❌ MQTT message error")

# # --------------------------------------------------
# # MQTT STARTER
# # --------------------------------------------------
# async def start_mqtt():
#     global MAIN_EVENT_LOOP, MQTT_STARTED

#     if MQTT_STARTED:
#         logger.warning("⚠️ MQTT already running")
#         return

#     MQTT_STARTED = True
#     MAIN_EVENT_LOOP = asyncio.get_running_loop()

#     for _ in range(4):
#         asyncio.create_task(queue_worker())

#     client = mqtt_client.Client(CLIENT_ID)
#     client.on_connect = on_connect
#     client.on_message = on_message

#     logger.info(f"🚀 Connecting to MQTT Broker {BROKER}:{PORT}")
#     client.connect(BROKER, PORT)

#     Thread(target=client.loop_forever, daemon=True).start()


# import asyncio
# import json
# import logging
# from datetime import datetime
# from queue import Queue, Empty
# from threading import Thread

# from paho.mqtt import client as mqtt_client
# from app.database import db
# from app.services.geofence_service import check_geofence

# # --------------------------------------------------
# # LOGGING
# # --------------------------------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("Mqtt_client")

# # --------------------------------------------------
# # MQTT CONFIG
# # --------------------------------------------------
# BROKER = "broker.hivemq.com"
# PORT = 1883
# TOPIC_SUBSCRIBE = "my/devices/#"
# CLIENT_ID = "device_subscriber"

# # --------------------------------------------------
# # GLOBAL STATE
# # --------------------------------------------------
# MESSAGE_QUEUE: Queue = Queue(maxsize=10000)
# MQTT_STARTED = False

# # --------------------------------------------------
# # ASYNC PAYLOAD PROCESSOR
# # --------------------------------------------------
# async def process_mqtt_payload(payload: dict):
#     try:
#         # --------------------------------------------------
#         # 0️⃣ DEVICE ID VALIDATION
#         # --------------------------------------------------
#         device_id = payload.get("device_id")
#         if not device_id:
#             logger.warning("⚠️ device_id missing in payload")
#             return

#         device_id = str(device_id)
#         now = datetime.utcnow()

#         # --------------------------------------------------
#         # 1️⃣ DEVICE LOOKUP (STRICT)
#         # --------------------------------------------------
#         device = await db.devices.find_one(
#             {"device_id": device_id},
#             {"user_id": 1}
#         )

#         # --------------------------------------------------
#         # 2️⃣ SAVE RAW HISTORY (even for unknown devices)
#         # --------------------------------------------------
#         await db.device_history.insert_one({
#             "device_id": device_id,
#             "received_at": now,
#             "raw_data": payload
#         })

#         # --------------------------------------------------
#         # 🚫 UNREGISTERED DEVICE → WARNING ONLY
#         # --------------------------------------------------
#         if not device:
#             logger.warning(
#                 f"🚫 GPS IGNORED | Unregistered device detected: {device_id}"
#             )
#             return

#         user_id = device["user_id"]

#         # --------------------------------------------------
#         # 3️⃣ UPDATE REGISTERED DEVICE (NO UPSERT)
#         # --------------------------------------------------
#         await db.devices.update_one(
#             {"device_id": device_id},
#             {
#                 "$set": {
#                     "device_status": "online",
#                     "battery_level": payload.get("battery"),
#                     "last_seen": now
#                 }
#             }
#         )

#         # --------------------------------------------------
#         # 4️⃣ LOCATION SAVE
#         # --------------------------------------------------
#         lat = payload.get("lat")
#         lon = payload.get("lon")

#         if lat is None or lon is None:
#             logger.info(f"ℹ️ No GPS data for device {device_id}")
#             return

#         await db.locations.insert_one({
#             "device_id": device_id,
#             "latitude": lat,
#             "longitude": lon,
#             "timestamp": now,
#             "user_id": user_id
#         })

#         # --------------------------------------------------
#         # 5️⃣ ASSET LINK CHECK
#         # --------------------------------------------------
#         asset_link = await db.asset_device_links.find_one({
#             "device_id": device_id,
#             "status": "active"
#         })

#         if not asset_link:
#             logger.info(f"ℹ️ No active asset linked for device {device_id}")
#             return

#         asset_id = asset_link["asset_id"]
#         logger.info(f"🚗 Device {device_id} belongs to asset {asset_id}")

#         # --------------------------------------------------
#         # 6️⃣ FETCH GEOFENCE DATA
#         # --------------------------------------------------
#         asset = await db.assets.find_one(
#             {"asset_id": asset_id},
#             {"registered_location": 1}
#         )

#         if not asset or "registered_location" not in asset:
#             logger.warning(f"⚠️ No geofence configured for asset {asset_id}")
#             return

#         geo = asset["registered_location"]
#         base_lat = geo.get("latitude")
#         base_lon = geo.get("longitude")
#         radius = geo.get("radius", 0)

#         if base_lat is None or base_lon is None or radius <= 0:
#             logger.warning(f"⚠️ Invalid geofence for asset {asset_id}")
#             return

#         # --------------------------------------------------
#         # 7️⃣ GEOFENCE CHECK
#         # --------------------------------------------------
#         geo_result = check_geofence(
#             lat,
#             lon,
#             base_lat,
#             base_lon,
#             radius
#         )

#         inside = geo_result["inside"]
#         distance = geo_result["distance_meters"]

#         logger.info(
#             f"📍 Asset {asset_id} | Distance={distance}m | Inside={inside}"
#         )

#         # --------------------------------------------------
#         # 8️⃣ UPDATE ASSET LIVE STATUS
#         # --------------------------------------------------
#         await db.asset_status.update_one(
#             {"asset_id": asset_id},
#             {
#                 "$set": {
#                     "device_id": device_id,
#                     "last_lat": lat,
#                     "last_lon": lon,
#                     "distance_from_base": distance,
#                     "inside_geofence": inside,
#                     "updated_at": now
#                 }
#             },
#             upsert=True
#         )

#         # --------------------------------------------------
#         # 9️⃣ GEOFENCE BREACH ALERT
#         # --------------------------------------------------
#         if not inside:
#             await db.alerts.insert_one({
#                 "asset_id": asset_id,
#                 "device_id": device_id,
#                 "alert_type": "geofence_breach",
#                 "message": f"Asset {asset_id} moved outside radius ({distance}m)",
#                 "severity": "critical",
#                 "created_at": now,
#                 "resolved": False
#             })

#             logger.warning(
#                 f"🚨 GEOFENCE BREACH | Asset {asset_id} | {distance} meters"
#             )

#         # --------------------------------------------------
#         # 🔋 LOW BATTERY ALERT
#         # --------------------------------------------------
#         battery = payload.get("battery")
#         if battery is not None and battery < 20:
#             await db.alerts.insert_one({
#                 "device_id": device_id,
#                 "alert_type": "low_battery",
#                 "message": f"Battery low: {battery}%",
#                 "severity": "warning",
#                 "created_at": now,
#                 "resolved": False
#             })
#             logger.warning(f"🔋 Low battery alert for {device_id}")

#         logger.info(
#             f"✅ Processed | device={device_id}, asset={asset_id}, user={user_id}"
#         )

#     except Exception:
#         logger.exception("🔥 Error processing MQTT payload")

# # --------------------------------------------------
# # QUEUE WORKER
# # --------------------------------------------------
# async def queue_worker():
#     while True:
#         try:
#             payload = MESSAGE_QUEUE.get_nowait()
#             await process_mqtt_payload(payload)
#         except Empty:
#             await asyncio.sleep(0.01)
#         except Exception:
#             logger.exception("❌ Worker error")

# # --------------------------------------------------
# # MQTT CALLBACKS
# # --------------------------------------------------
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         logger.info("✅ Connected to MQTT Broker")
#         client.subscribe(TOPIC_SUBSCRIBE)
#         logger.info(f"📡 Subscribed to {TOPIC_SUBSCRIBE}")
#     else:
#         logger.error(f"❌ MQTT connection failed: {rc}")

# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())
#         logger.info(f"📨 {msg.topic} → {payload}")
#         MESSAGE_QUEUE.put_nowait(payload)
#     except Exception:
#         logger.exception("❌ MQTT message error")

# # --------------------------------------------------
# # MQTT STARTER
# # --------------------------------------------------
# async def start_mqtt():
#     global MQTT_STARTED

#     if MQTT_STARTED:
#         logger.warning("⚠️ MQTT already running")
#         return

#     MQTT_STARTED = True

#     for _ in range(4):
#         asyncio.create_task(queue_worker())

#     client = mqtt_client.Client(CLIENT_ID)
#     client.on_connect = on_connect
#     client.on_message = on_message

#     logger.info(f"🚀 Connecting to MQTT Broker {BROKER}:{PORT}")
#     client.connect(BROKER, PORT)

#     Thread(target=client.loop_forever, daemon=True).start()


import asyncio
import json
import logging
from datetime import datetime
from queue import Queue, Empty
from threading import Thread

from paho.mqtt import client as mqtt_client
from app.database import db
from app.services.geofence_service import check_geofence

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Mqtt_client")

# --------------------------------------------------
# MQTT CONFIG
# --------------------------------------------------
# BROKER = "broker.hivemq.com"
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_SUBSCRIBE = "my/device/#"
CLIENT_ID = "device_subscriber"

# --------------------------------------------------
# GLOBAL STATE
# --------------------------------------------------
MESSAGE_QUEUE: Queue = Queue(maxsize=10000)
MAIN_EVENT_LOOP: asyncio.AbstractEventLoop | None = None
MQTT_STARTED = False

# --------------------------------------------------
# ASYNC PAYLOAD PROCESSOR
# --------------------------------------------------
async def process_mqtt_payload(payload: dict):
    try:
        # --------------------------------------------------
        # 0️⃣ DEVICE ID VALIDATION
        # --------------------------------------------------
        device_id = payload.get("device_id")
        if not device_id:
            logger.warning("⚠️ device_id missing in payload")
            return

        device_id = str(device_id)
        now = datetime.utcnow()

        # --------------------------------------------------
        # 1️⃣ CHECK REGISTERED DEVICE
        # --------------------------------------------------
        device = await db.devices.find_one(
            {"device_id": device_id},
            {"user_id": 1}
        )

        # --------------------------------------------------
        # 2️⃣ HANDLE UNREGISTERED DEVICE
        # --------------------------------------------------
        if not device:
            logger.warning(f"🆕 Unregistered device detected: {device_id}")

            await db.unregistered_devices.update_one(
                {"device_id": device_id},
                {
                    "$set": {
                        "last_seen": now,
                        "last_payload": payload
                    },
                    "$setOnInsert": {
                        "device_id": device_id,
                        "first_seen": now,
                        "status": "unregistered"
                    },
                    "$inc": {
                        "seen_count": 1
                    }
                },
                upsert=True
            )

            # Still store history for audit
            await db.device_history.insert_one({
                "device_id": device_id,
                "received_at": now,
                "raw_data": payload,
                "registered": False
            })

            return  # ⛔ STOP further processing

        # --------------------------------------------------
        # 3️⃣ REGISTERED DEVICE FLOW
        # --------------------------------------------------
        user_id = device.get("user_id")

        # --------------------------------------------------
        # 4️⃣ DEVICE HISTORY
        # --------------------------------------------------
        await db.device_history.insert_one({
            "device_id": device_id,
            "received_at": now,
            "raw_data": payload,
            "registered": True
        })

        # --------------------------------------------------
        # 5️⃣ DEVICE UPSERT (REGISTERED)
        # --------------------------------------------------
        await db.devices.update_one(
            {"device_id": device_id},
            {
                "$set": {
                    "device_status": "online",
                    "battery_level": payload.get("battery"),
                    "last_seen": now
                }
            }
        )

        # --------------------------------------------------
        # 6️⃣ LOCATION SAVE
        # --------------------------------------------------
        lat = payload.get("lat")
        lon = payload.get("lon")

        if lat is None or lon is None:
            logger.info(f"ℹ️ No GPS data for device {device_id}")
            return

        await db.locations.insert_one({
            "device_id": device_id,
            "latitude": lat,
            "longitude": lon,
            "timestamp": now,
            "user_id": user_id
        })

        # --------------------------------------------------
        # 7️⃣ ASSET LINK CHECK
        # --------------------------------------------------
        asset_link = await db.asset_device_links.find_one({
            "device_id": device_id,
            "status": "active"
        })

        if not asset_link:
            logger.info(f"ℹ️ No active asset linked for device {device_id}")
            return

        asset_id = asset_link["asset_id"]

        # --------------------------------------------------
        # 8️⃣ FETCH ASSET GEOFENCE
        # --------------------------------------------------
        asset = await db.assets.find_one(
            {"asset_id": asset_id},
            {"registered_location": 1}
        )

        if not asset or "registered_location" not in asset:
            logger.warning(f"⚠️ No geofence for asset {asset_id}")
            return

        geo = asset["registered_location"]

        base_lat = geo.get("latitude")
        base_lon = geo.get("longitude")
        radius = geo.get("radius", 0)

        if base_lat is None or base_lon is None or radius <= 0:
            logger.warning(f"⚠️ Invalid geofence for asset {asset_id}")
            return

        # --------------------------------------------------
        # 9️⃣ GEOFENCE CHECK
        # --------------------------------------------------
        geo_result = check_geofence(
            lat,
            lon,
            base_lat,
            base_lon,
            radius
        )

        inside = geo_result["inside"]
        distance = geo_result["distance_meters"]

        logger.info(
            f"📍 Asset {asset_id} | Distance={distance}m | Inside={inside}"
        )

        # --------------------------------------------------
        # 🔟 SAVE ASSET STATUS
        # --------------------------------------------------
        # await db.asset_status.update_one(
        #     {"asset_id": asset_id},
        #     {
        #         "$set": {
        #             "device_id": device_id,
        #             "last_lat": lat,
        #             "last_lon": lon,
        #             "distance_from_base": distance,
        #             "inside_geofence": inside,
        #             "updated_at": now
        #         }
        #     },
        #     upsert=True
        # )

        await db.asset_status.update_one(
            {"asset_id": asset_id},
            {
                "$set": {
                    "device_id": device_id,
                    "last_lat": lat,
                    "last_lon": lon,

                    "geofence_lat": base_lat,
                    "geofence_lon": base_lon,
                    "geofence_radius": radius,

                    "distance_from_base": distance,
                    "inside_geofence": inside,
                    "updated_at": now
                }
            },
            upsert=True
        )

        # --------------------------------------------------
        # 1️⃣1️⃣ GEOFENCE BREACH ALERT
        # --------------------------------------------------
        if not inside:
            await db.alerts.insert_one({
                "asset_id": asset_id,
                "device_id": device_id,
                "alert_type": "geofence_breach",
                "message": f"Asset {asset_id} moved outside radius ({distance}m)",
                "severity": "critical",
                "created_at": now,
                "resolved": False
            })

            logger.warning(
                f"🚨 GEOFENCE BREACH | Asset {asset_id}"
            )

        # --------------------------------------------------
        # 1️⃣2️⃣ LOW BATTERY ALERT
        # --------------------------------------------------
        battery = payload.get("battery")
        if battery is not None and battery < 20:
            await db.alerts.insert_one({
                "device_id": device_id,
                "alert_type": "low_battery",
                "message": f"Battery low: {battery}%",
                "severity": "warning",
                "created_at": now,
                "resolved": False
            })
            logger.warning(f"🔋 Low battery alert for {device_id}")

        logger.info(
            f"✅ Processed | device={device_id}, asset={asset_id}, user={user_id}"
        )

    except Exception:
        logger.exception("🔥 Error processing MQTT payload")

# --------------------------------------------------
# QUEUE WORKER
# --------------------------------------------------
async def queue_worker():
    while True:
        try:
            payload = MESSAGE_QUEUE.get_nowait()
            await process_mqtt_payload(payload)
        except Empty:
            await asyncio.sleep(0.01)
        except Exception:
            logger.exception("❌ Queue worker error")

# --------------------------------------------------
# MQTT CALLBACKS
# --------------------------------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("✅ Connected to MQTT Broker")
        client.subscribe(TOPIC_SUBSCRIBE)
        logger.info(f"📡 Subscribed to {TOPIC_SUBSCRIBE}")
    else:
        logger.error(f"❌ MQTT connection failed: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        logger.info(f"📨 {msg.topic} → {payload}")
        MESSAGE_QUEUE.put_nowait(payload)
    except Exception:
        logger.exception("❌ MQTT message error")

# --------------------------------------------------
# MQTT STARTER
# --------------------------------------------------
async def start_mqtt():
    global MAIN_EVENT_LOOP, MQTT_STARTED

    if MQTT_STARTED:
        logger.warning("⚠️ MQTT already running")
        return

    MQTT_STARTED = True
    MAIN_EVENT_LOOP = asyncio.get_running_loop()

    for _ in range(4):
        asyncio.create_task(queue_worker())

    client = mqtt_client.Client(CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    logger.info(f"🚀 Connecting to MQTT Broker {BROKER}:{PORT}")
    client.connect(BROKER, PORT)

    Thread(target=client.loop_forever, daemon=True).start()
