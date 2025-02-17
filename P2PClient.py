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
mutex = threading.Lock()

class P2PClient:
    def __init__(self, folder, trans_port, name, file_path, tracker_ip, tracker_port):
        self.folder = folder
        self.trans_port = trans_port
        self.name = name
        self.file_path = file_path
        self.tracker_ip = tracker_ip
        self.tracker_port = tracker_port
        self.total_chunks = 0

    def start(self):
        self.sock_listen = socket.socket()
        self.sock_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_listen.bind(("", self.trans_port))
        self.sock_listen.listen()

        self.sock_tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tracker.connect((self.tracker_ip, self.tracker_port))

        self.chunks = self.prepare_chunks()
        self.send_tracker_info()

    def send_tracker_info(self):
        for index in self.chunks.keys():
            message = f"LOCAL_CHUNKS,{index},localhost,{self.trans_port}"
            self.sock_tracker.sendall(message.encode())
            log.info(f"{self.name},LOCAL_CHUNKS,{index},localhost,{self.trans_port}")
            log.handlers[0].flush()
            time.sleep(1)
        self.client_run()

    def client_run(self):
        threading.Thread(target=self.listen_for_peers).start()
        chunks_needed = self.find_missing_chunk()
        while len(chunks_needed) != 0:
            for chunk_need in chunks_needed:
                message = f"WHERE_CHUNK,{chunk_need}"
                self.sock_tracker.send(message.encode())
                log.info(f"{self.name},WHERE_CHUNK,{chunk_need}")
                log.handlers[0].flush()
                data = self.sock_tracker.recv(2048).decode()
                time.sleep(1)
                if data.split(',')[0] == "GET_CHUNK_FROM":
                    data = data.split(',')[2:]
                    for j in range(len(data) // 2):
                        if chunk_need in self.chunks:
                            break
                        peer_info = (data[j*2], data[j*2 + 1])
                        self.handle_ask_peer(peer_info, chunk_need)
            chunks_needed = self.find_missing_chunk()
        self.sock_tracker.close()

    def handle_ask_peer(self, peer_info, chunk_need):
        peer_info = (peer_info[0], int(peer_info[1]))
        peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer.connect(peer_info)
        message = f"REQUEST_CHUNK,{chunk_need}"
        peer.sendall(message.encode())
        incoming_chunk = bytearray()
        while True:
            chunklet = peer.recv(2048)
            if not chunklet:
                break
            else:
                incoming_chunk += chunklet
        log.info(f"{self.name},REQUEST_CHUNK,{chunk_need},localhost,{peer_info[1]}")
        log.handlers[0].flush()
        peer.close()
        with open(f"{self.folder}/chunk_{chunk_need}", "wb") as f:
            f.write(incoming_chunk)
        self.chunks[chunk_need] = f"chunk_{chunk_need}"
        message = f"LOCAL_CHUNKS,{chunk_need},localhost,{self.trans_port}"
        self.sock_tracker.sendall(message.encode())
        log.info(f"{self.name},LOCAL_CHUNKS,{chunk_need},localhost,{peer_info[1]}")
        log.handlers[0].flush()
        time.sleep(1)



    def listen_for_peers(self):
        while True:
            client, addr = self.sock_listen.accept()
            threading.Thread(target=self.handle_peer_connection, args=(client,)).start()

    def handle_peer_connection(self, client):
        data = client.recv(1024).decode()
        if data.split(',')[0] == "REQUEST_CHUNK":
            self.handle_get_chunks(data, client)

    def handle_get_chunks(self, data, client):
        index = data.split(',')[1]
        index = int(index)
        if index in self.chunks:
            try:
                with open(self.folder + f"/{self.chunks[index]}", "rb") as f:
                    client.sendall(f.read())
                
            except FileNotFoundError:
                client.send("CHUNK_NOT_FOUND".encode())
                client.close()
        else:
            client.send("CHUNK_NOT_FOUND".encode())
        client.close()

    def find_missing_chunk(self):
        missing = []
        for i in range(1, self.total_chunks + 1):
            if i not in self.chunks:
                missing.append(i)
        return missing

    def prepare_chunks(self):
        chunks = {}
        with open(self.file_path, "r") as f:
            for line in f:
                index, local_chunk = line.strip().split(',')
                if local_chunk == 'LASTCHUNK':
                    self.total_chunks = int(index)
                    break
                chunks[int(index)] = local_chunk
        return chunks

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-folder", required=True)
	parser.add_argument("-transfer_port", required=True, type=int)
	parser.add_argument("-name", required=True)
	args = parser.parse_args()
	folder = args.folder
	trans_port = args.transfer_port
	name = args.name
	file_path = folder + "/local_chunks.txt"
	tracker_ip = "localhost"
	tracker_port = 5100
	client = P2PClient(folder, trans_port, name, file_path, tracker_ip, tracker_port)
	client.start()