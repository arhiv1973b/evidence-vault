import socket
import json
import subprocess

# Integration point for acting as the default model provider
HOST = "127.0.0.1"
PORT = 65432
ES_PATH = r"F:\Мой диск\es.exe"


def search_files(query):
    try:
        # Ищем по запросу через es.exe
        result = subprocess.run(
            [ES_PATH, query], capture_output=True, text=True, encoding="cp866"
        )
        return result.stdout
    except Exception as e:
        return f"Error executing search: {str(e)}"


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Actor Model Socket listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(4096)
                if not data:
                    break

                try:
                    request = json.loads(data.decode())
                    print(f"Received request: {request}")

                    action = request.get("action")
                    if action == "search":
                        query = request.get("query", "socet")
                        data_result = search_files(query)
                        response = {"status": "success", "data": data_result}
                    else:
                        response = {"status": "error", "message": "Unknown action"}
                except json.JSONDecodeError:
                    response = {"status": "error", "message": "Invalid JSON"}

                conn.sendall(json.dumps(response).encode())


if __name__ == "__main__":
    start_server()
