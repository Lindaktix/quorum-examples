import paho.mqtt.client as mqtt
import json
from web3 import Web3
import time
from eth_account import Account
import os
from pathlib import Path

# MQTT Configuration
MQTT_BROKER = "localhost"
TEMP_TOPIC = "factory/temperature"
MOTOR_CONTROL_TOPIC = "factory/motor"

# Quorum Configuration
QUORUM_RPC_URL = "http://127.0.0.1:22000"
PRIVATE_KEY = "e6181caaffff94a09d7e332fc8da9884d99902c7874eb74354bdcadf411929f1"
CONTRACT_ADDRESS = "0xCE1663b2f636a04Fd661fF3caFD7A96458FE3696"

# Load contract ABI
contract_path = Path(__file__).parent / "build/contracts/TemperatureStorage.json"
with open(contract_path) as f:
    contract_json = json.load(f)
    CONTRACT_ABI = contract_json['abi']

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(QUORUM_RPC_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
account = Account.from_key(PRIVATE_KEY)

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(TEMP_TOPIC)

def on_message(client, userdata, msg):
    try:
        temperature = float(msg.payload.decode())
        print(f"Received temperature: {temperature}°C")

        # Convert temperature for contract (multiply by 100)
        temp_for_contract = int(temperature * 100)

        # Build transaction
        nonce = w3.eth.get_transaction_count(account.address)
        transaction = contract.functions.logTemperature(temp_for_contract).build_transaction({
            'from': account.address,
            'gas': 2000000,
            'gasPrice': 0,
            'nonce': nonce,
        })

        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Temperature recorded on blockchain. TX Hash: {tx_receipt.transactionHash.hex()}")

        # Check if temperature exceeds threshold
        threshold = contract.functions.temperatureThreshold().call()
        if temp_for_contract >= threshold:
            print("⚠️ High Temperature! Stopping Stepper Motor...")
            client.publish(MOTOR_CONTROL_TOPIC, "STOP")

    except Exception as e:
        print(f"Error processing temperature: {e}")

# Set up MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
try:
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()
except Exception as e:
    print(f"Error connecting to MQTT broker: {e}")
