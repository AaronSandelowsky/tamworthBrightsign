import socket

# Set up the receiver socket
receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define the IP address and port the receiver will listen on
receiver_ip = '192.168.5.146'  # You can change this to your local IP or use '0.0.0.0' to listen on all available interfaces
receiver_port = 12345     # Choose a port number (should match the sender's port number)

# Bind the socket to the IP and port
receiver_socket.bind((receiver_ip, receiver_port))

# Set a timeout (optional, if you want to limit the time it waits for a message)
receiver_socket.settimeout(10)  # Set timeout to 10 seconds

try:
    # Receive data (1024 bytes buffer size)
    data, sender_address = receiver_socket.recvfrom(1024)

    # Convert the received bytes data to a string
    message = data.decode('utf-8')

    print(f"Received message: '{message}' from {sender_address}")

except socket.timeout:
    print("No message received, timeout occurred.")

finally:
    # Close the socket
    receiver_socket.close()
