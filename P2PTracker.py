import socket
import argparse
import threading
import sys
import hashlib
import time
import logging


logging.basicConfig(filename="logger.log", format="%(message)s", filemode="a")
log = logging.getLogger()
log.setLevel(logging.DEBUG)
IP = "localhost"
PORT = 5100
chunk_info = {}
mutex = threading.Lock()

def start():
	sock = socket.socket()
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((IP, PORT))
	sock.listen()
	while True:
		client, addr = sock.accept()
		threading.Thread(target=handle_client, args=(client, addr)).start()

def handle_client(client, addr):
	while True:
		try:
			data = client.recv(1024).decode().split('\n')
			for d in data:
				d = d.split(',')
				if len(d) > 1:
					index = int(d[1])
					if d[0] == "WHERE_CHUNK":
						with mutex:
							handle_where_chunk(client, index)
					elif d[0] == "LOCAL_CHUNKS":
							if int(index) not in chunk_info:
								chunk_info[index] = []
							chunk_info[index].append((d[2], int(d[3])))
		except Exception as e:
			client.close()
			break

def handle_where_chunk(client, index):
	if index in chunk_info:
		peer_list = chunk_info[index]
		message = f"GET_CHUNK_FROM,{index}"
		for peer in peer_list:
			message += f",{peer[0]},{peer[1]}"
		client.sendall(message.encode())
		log.info(f"P2PTracker,{str(message)}")
		log.handlers[0].flush()
	else:
		client.sendall(f"CHUNK_LOCATION_UNKNOWN,{index}".encode())
		log.info(f"P2PTracker,CHUNK_LOCATION_UNKNOWN,{index}")
		log.handlers[0].flush()

if __name__ == "__main__":
	start()