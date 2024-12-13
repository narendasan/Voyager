import psutil
from voyager import Voyager
from dotenv import load_dotenv
import os

def find_minecraft_java_port():
    """
    Finds the port number on which a Minecraft Java server is listening.
    
    Returns:
        int: The port number if found, otherwise None.
    """
    # Iterate over all network connections
    for conn in psutil.net_connections(kind='inet'):
        # Check if the connection is listening
        if conn.status == psutil.CONN_LISTEN:
            try:
                # Check the process associated with this connection
                process = psutil.Process(conn.pid)
                if 'java' in process.name().lower():
                    # Check for a common identifier of Minecraft server in command line args
                    cmdline = process.cmdline()
                    if any('minecraft' in arg.lower() for arg in cmdline):
                        return conn.laddr.port
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
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

    # Find the port number for the Minecraft Java server
    mc_port = find_minecraft_java_port()

    # Get OpenAI API key from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if mc_port is None:
        print("\n\033[41;33m************************************************************************* \033[0m")
        print("\033[41;33m*** Minecraft Java server not found. Make sure the server is running. *** \033[0m")
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