import socket
from config import HOST, PORT, BUFFER_SIZE, ENCODING, CLIENT_DOWNLOADS
from pathlib import Path


def receive_file(client_socket, filename: str, file_size: int,):
    """
    Receive exactly file_size bytes
    and save them to disk.
    """

    destination = CLIENT_DOWNLOADS / filename

    received = 0

    with open(destination, "wb") as file:
        while received < file_size:

            remaining = file_size - received

            chunk_size = min(BUFFER_SIZE, remaining,)
            chunk = client_socket.recv(chunk_size)

            if not chunk:
                raise ConnectionError("Connection closed during transfer.")
            
            file.write(chunk)
            received += len(chunk)

            print(f"Received {received}/{file_size} bytes")

    print(f"Download complete: {destination}")


def receive_response(client_socket):
    """
    Read exactly one protocol response.
    Responses are terminated by '\n'.
    """
    data = b""

    while b"\n" not in data:
        chunk = client_socket.recv(1)

        if not chunk:
            raise ConnectionError("Server disconnected.")

        data += chunk

    return data.decode(ENCODING).strip()


def send_file(client_socket, filepath: Path):
    """
    Stream a file to the server.
    """

    file_size = filepath.stat().st_size

    client_socket.sendall(f"{file_size}\n".encode(ENCODING))

    response = receive_response(client_socket)

    print(f"Server: {response}")

    if response != "OK SEND FILE":
        return

    sent = 0

    with open(filepath, "rb") as file:
        while chunk := file.read(BUFFER_SIZE):
            client_socket.sendall(chunk)

            sent += len(chunk)

            print(f"Sent {sent}/{file_size} bytes")

    print(f"Upload complete: {filepath.name}")


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}")

        while True:
            message = input("> ").strip()

            if message.lower() == "exit":
                break

            #
            # Pre-validate PUT
            #
            filepath = None

            if message.upper().startswith("PUT "):
                parts = message.split(maxsplit=1)

                if len(parts) != 2:
                    print("Usage: PUT <filename>")
                    continue

                filepath = Path(parts[1])

                if not filepath.is_file():
                    print("Local file does not exist.")
                    continue

            #
            # Send command
            #
            client_socket.sendall(f"{message}\n".encode(ENCODING))

            #
            # Receive response
            #
            response = receive_response(client_socket)

            print(f"Server: {response}")

            if message.upper() == "QUIT":
                break

            #
            # GET
            #
            if message.upper().startswith("GET "):
                parts = response.split(" ",maxsplit=1,)

                if (len(parts) == 2 and parts[0] == "OK"):
                    file_size = int(parts[1])

                    filename = message.split(maxsplit=1)[1]

                    receive_file(client_socket, filename, file_size)

            #
            # PUT
            #
            elif message.upper().startswith("PUT "):
                if response == "OK READY":
                    send_file(client_socket, filepath)

    finally:
        client_socket.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()