# clock-sync/time_client.py
import socket
import struct
import time

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999

def synchronize():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)

    # t1: Client transmission timestamp
    t1 = time.time()
    message = struct.pack("!d", t1)
    sock.sendto(message, (SERVER_HOST, SERVER_PORT))

    try:
        data, _ = sock.recvfrom(1024)
        # t4: Client reception timestamp
        t4 = time.time()
        
        # Unpack server timestamps
        t1_resp, t2, t3 = struct.unpack("!ddd", data)

        # 1. Round-Trip Delay (RTT): delta = (t4 - t1) - (t3 - t2)
        delta = (t4 - t1) - (t3 - t2)
        
        # 2. Clock Skew: theta = ((t2 - t1) + (t3 - t4)) / 2
        theta = ((t2 - t1) + (t3 - t4)) / 2.0
        
        # Estimated true physical time at arrival
        estimated_time = t4 + theta

        print("=== Synchronization Results ===")
        print(f"t1 (Client departure):  {t1:.6f} s")
        print(f"t2 (Server arrival):    {t2:.6f} s")
        print(f"t3 (Server departure):  {t3:.6f} s")
        print(f"t4 (Client arrival):    {t4:.6f} s")
        print("-------------------------------")
        print(f"Round-Trip Delay (RTT): {delta * 1000:.3f} ms")
        print(f"Clock Skew (theta):     {theta:.6f} s")
        print(f"Local System Time (t4): {time.ctime(t4)}")
        print(f"Estimated Correct Time: {time.ctime(estimated_time)}")

        # Recommended correction strategy
        if abs(theta) < 0.125:
            print("[Action] Slew recommended: apply gradual frequency adjustment.")
        else:
            print("[Action] Step recommended: large offset detected; step clock directly.")

    except socket.timeout:
        print("[Error] Request timed out while waiting for the time server.")
    finally:
        sock.close()

if __name__ == "__main__":
    synchronize()