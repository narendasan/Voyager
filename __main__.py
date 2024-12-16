import psutil
from voyager import Voyager
from dotenv import load_dotenv
import os
import socket
import struct
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


def to_varint(n):
    """Convert integer to VarInt (used in Minecraft networking)."""
    byte_array = bytearray()
    while (n & ~0x7F) != 0:
        byte_array.append((n & 0x7F) | 0x80)
        n >>= 7
    byte_array.append(n)
    return bytes(byte_array)


# Add a shared event
stop_event = threading.Event()

def verify_minecraft_server(ip_addr, port_number):
    print(f"Trying port {port_number}")
    sock = None
    if stop_event.is_set():
        return False
    try:
        # Connect to the server with a timeout
        sock = socket.create_connection((ip_addr, port_number), timeout=1)

        # Construct the Handshake packet
        # 1. Packet ID (1 byte, for Handshake this is 0x00)
        packet_id = b"\x00"
        # 2. Protocol Version (as of 1.19, the protocol version is 759; adjust if necessary)
        protocol_version = to_varint(759)
        # 3. Length of IP address followed by actual IP address
        ip_address_bytes = ip_addr.encode("utf-8")
        ip_address_length = to_varint(len(ip_address_bytes))
        # 4. Port number (2 bytes in big-endian format)
        port_bytes = struct.pack("!H", port_number)
        # 5. Next state (1 byte, 0x01 for status)
        next_state = b"\x01"

        # Combine all parts into a Handshake packet
        handshake_packet = (
                packet_id
                + protocol_version
                + ip_address_length
                + ip_address_bytes
                + port_bytes
                + next_state
        )

        # Prepend the length of the packet as a VarInt
        handshake_length = to_varint(len(handshake_packet))
        full_handshake_packet = handshake_length + handshake_packet

        # Send the Handshake packet
        sock.sendall(full_handshake_packet)

        # Send the Status Request packet (1 byte, 0x00)
        status_request_packet = b"\x01\x00"  # Length of 1 (VarInt) + 0x00 (Packet ID)
        sock.sendall(status_request_packet)

        # Read the response
        # Read the length of the packet (VarInt)
        to_varint(read_varint(sock))
        # Read the Packet ID (VarInt, not needed further)
        read_varint(sock)
        # Read the JSON Data (as a string)
        json_length = read_varint(sock)  # Length of the JSON string
        response = sock.recv(json_length).decode("utf-8")

        # Parse and verify the JSON response
        server_data = json.loads(response)

        if "description" in server_data and "players" in server_data:
            print(f"Found Minecraft server on port {port_number}")
            stop_event.set()
            return True
        else:
            print(f"Port {port_number} is not a valid Minecraft server.")
            return False

    except Exception as e:
        #print(f"Exception on port {port_number}: {e}")
        return False

    finally:
        if sock is not None:
            sock.close()


def read_varint(sock):
    """Reads a VarInt from the socket."""
    value = 0
    size = 0
    while True:
        byte = sock.recv(1)
        if len(byte) == 0:
            raise IOError("Unexpected end of stream while reading VarInt")
        byte = ord(byte) if isinstance(byte, bytes) else byte  # Extract int from byte
        value |= (byte & 0x7F) << (7 * size)
        size += 1
        if size > 5:
            raise IOError("VarInt is too big.")
        if not (byte & 0x80):
            break
    return value


def scan_ports(ip, start_port, end_port, max_workers=100):
    """Scans ports on the given IP address to find an open Minecraft server."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {}
        for port in range(start_port, end_port + 1):
            #print(f"Scanning port {port}")
            future_to_port[executor.submit(verify_minecraft_server, ip, port)] = port
        for future in as_completed(future_to_port):
            port = future_to_port[future]
            if future.result():
                return port
    return None


if __name__ == "__main__":

    print("                  _   _                                   ")
    print("                 | | | |                                  ")
    print("                 | | | | ___  _   _  __ _  __ _  ___ _ __ ")
    print("                 | | | |/ _ \| | | |/ _` |/ _` |/ _ \ '__|")
    print("                 \ \_/ / (_) | |_| | (_| | (_| |  __/ |   ")
    print("                  \___/ \___/ \__, |\__,_|\__, |\___|_|   ")
    print("                               __/ |       __/ |          ")
    print("                              |___/       |___/           ")
    print()
    print("        An Open-Ended Embodied Agent with Large Language Models")
    print()
    print("                          original authors:")
    print("             Guanzhi Wang and Yuqi Xie and Yunfan Jiang and")
    print("              Ajay Mandlekar and Chaowei Xiao and Yuke Zhu")
    print("                  and Linxi Fan and Anima Anandkumar")
    print()

    # Load environment variables from .env file
    load_dotenv()

    # Get OpenAI API key from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")

    ip = "127.0.0.1"
    start_port = 56100
    end_port = 65535
    print(f"Starting port scan from {start_port} to {end_port}")
    #mc_port = scan_ports(ip, start_port, end_port)

    mc_port = 56109

    if mc_port is None:
        print("\n\033[41;33m************************************************************************* \033[0m")
        print("\033[41;33m*** Unable to find an open Minecraft instance. Make sure Minecraft is *** \033[0m")
        print("\033[41;33m*** running and 'Open To LAN' has been clicked.                       *** \033[0m")
        print("\033[41;33m************************************************************************* \033[0m")
        print()
        exit()

    # Ask the user if they want to start over or continue from their previous session
    resume = input("Do you want to continue from your previous session? (yes/no): ").strip().lower() == 'yes'

    # Initialize the Voyager instance with the Minecraft port and OpenAI API key
    voyager = Voyager(
        mc_port=mc_port,
        openai_api_key=openai_api_key,
        resume=resume
    )

    # Start lifelong learning
    voyager.learn()