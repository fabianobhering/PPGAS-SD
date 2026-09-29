# clock-sync/time_server.py
import socket
import struct
import time

HOST = "127.0.0.1"
PORT = 9999
# Artificial clock skew in seconds to simulate an out-of-sync node
SIMULATED_SKEW = 10.0  

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[Time Server] Listening on {HOST}:{PORT}...")
    print(f"[Time Server] Injected artificial skew: {SIMULATED_SKEW} s")

    while True:
        # Receive t1 packed as a double-precision float (8 bytes)
        data, client_addr = sock.recvfrom(1024)
        t2 = time.time() + SIMULATED_SKEW  # Arrival timestamp at server

        t1 = struct.unpack("!d", data)[0]

        # Simulate brief internal processing delay
        time.sleep(0.005)
        t3 = time.time() + SIMULATED_SKEW  # Departure timestamp from server

        # Reply with the tuple (t1, t2, t3)
        response = struct.pack("!ddd", t1, t2, t3)
        sock.sendto(response, client_addr)
        print(f"[Server] Handled request from {client_addr} | t1={t1:.4f}, t2={t2:.4f}, t3={t3:.4f}")

if __name__ == "__main__":
    main()