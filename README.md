# P2P File Sharing System

This project implements a Peer-to-Peer (P2P) file-sharing system to mimic the way BitTorrent works, consisting of a **Tracker** and multiple **Clients** that share file chunks. Clients can request missing file chunks from peers and share their available chunks with others.

## How It Works
1. **Tracker (Central Coordinator)**:
   - Maintains a record of which client has which chunk.
   - Handles peer requests for chunk locations.
   - Runs on a fixed IP and port (default: `localhost:5100`).
   
2. **Clients (Peers)**:
   - Start by registering their available chunks with the tracker.
   - Request missing chunks from peers when needed.
   - Respond to requests from other clients by sending chunks.

## Setup Instructions

### 1. Clone the Repository

### 2. Start the Tracker
Run the tracker first, as it needs to be online before clients can connect:
```bash
python tracker.py
```

### 3. Prepare Client Folders and Files
Each client needs a folder containing the chunks they own. Follow these steps:

#### a) Create a Folder for the Client
```bash
mkdir client1_chunks
cd client1_chunks
```

#### b) Create a `local_chunks.txt` File
This file lists the chunks available for this client.

**Example Format (local_chunks.txt)**:
```
1,chunk_1
2,chunk_2
3,chunk_3
4,LASTCHUNK
```
- Each line represents a chunk number and its filename.
- The last line must contain `LASTCHUNK` to indicate the total number of chunks.

#### c) Place Chunk Files in the Folder
Ensure that the chunk files exist in the folder and match the names in `local_chunks.txt`. Example:
```bash
touch chunk_1 chunk_2 chunk_3
```

### 4. Start a Client
Run a client with the necessary parameters:
```bash
python client.py -folder client1_chunks -transfer_port 6000 -name client1
```
- `-folder` specifies the directory where chunks are stored.
- `-transfer_port` is the port for peer-to-peer communication.
- `-name` is the identifier for the client.

### 5. Add More Clients
Repeat steps 3 and 4 for additional clients, using unique folder names and ports.

## How Clients Share and Request Chunks
1. Clients first inform the tracker about their available chunks.
2. If a client is missing chunks, it requests their locations from the tracker.
3. The client then connects to peers and requests the needed chunks.
4. Once a chunk is received, the client updates the tracker.

## Logging
Logs are stored in `logger.log` to track:
- Chunk requests
- Chunk locations
- Peer connections

## Example Workflow
1. **Client 1** starts with chunks 1 and 2.
2. **Client 2** starts with chunks 3 and 4.
3. **Client 1** requests chunk 3 from the tracker.
4. The tracker informs Client 1 that Client 2 has chunk 3.
5. Client 1 connects to Client 2 and downloads chunk 3.
6. Client 1 informs the tracker that it now has chunk 3.

## Notes
- Ensure all clients use the same tracker IP and port.
- Clients must have proper read/write permissions for chunk files.

This system enables efficient decentralized file sharing through peer-to-peer communication!

