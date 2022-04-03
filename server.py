import socket
import threading


HOST = "127.0.0.1"
PORT = 9090
FORMAT = "utf-8"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []


def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client):

    while True:

        try:
            message = client.recv(1024)
            print(f"{nicknames[clients.index(client)]} says {message.decode(FORMAT)}")
            broadcast(message)

        except:

            index = clients.index(client)
            broadcast(f"{nicknames[index]} has left the chat\n".encode(FORMAT))

            index = clients.index(client)
            clients.remove(client)
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break


def receive():

    while True:
        client, address = server.accept()
        print(f"{str(address)} has connected...")

        client.send("NICK".encode(FORMAT))
        nickname = client.recv(1024).decode(FORMAT)
        nicknames.append(nickname)

        clients.append(client)
        print(f"Name of new client is {nickname}")

        broadcast(f"{nickname} has joined the chat\n".encode(FORMAT))
        client.send("Connected to chat".encode(FORMAT))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server running...")
receive()
