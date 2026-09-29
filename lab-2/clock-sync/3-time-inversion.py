# clock-sync/3_causality_inversion.py
import time

class Node:
    def __init__(self, name: str, clock_skew_seconds: float):
        self.name = name
        self.clock_skew = clock_skew_seconds  # Physical clock discrepancy

    def get_physical_time(self) -> float:
        # Return physical timestamp with the node's local skew
        return time.time() + self.clock_skew

def simulate_causality_violation():
    print("=== Simulation: Causal Inversion with Physical Timestamps ===")
    
    # Node A is running 2.0 seconds ahead
    # Node B is running 1.0 second behind
    node_a = Node("Node A", clock_skew_seconds=2.0)
    node_b = Node("Node B", clock_skew_seconds=-1.0)
    
    messages = []

    # 1. Node A publishes a question
    t_send_a = node_a.get_physical_time()
    msg_a = {
        "author": node_a.name,
        "content": "Is the moon made of cheese?",
        "timestamp": t_send_a
    }
    messages.append(msg_a)
    print(f"1. [{node_a.name}] posted at {t_send_a:.3f}: '{msg_a['content']}'")

    # Simulate network latency and time taken by Node B to read and answer
    time.sleep(0.5)

    # 2. Node B reads the question and answers (B was caused by A: A -> B)
    t_send_b = node_b.get_physical_time()
    msg_b = {
        "author": node_b.name,
        "content": "No, it is definitely not!",
        "timestamp": t_send_b
    }
    messages.append(msg_b)
    print(f"2. [{node_b.name}] replied at {t_send_b:.3f}: '{msg_b['content']}'")

    print("\n--- Real Order of Occurrence ---")
    print("Actual causality: Event 1 (Node A's question) -> Event 2 (Node B's reply)")

    print("\n--- Logs Ordered Exclusively by Physical Timestamp ---")
    sorted_messages = sorted(messages, key=lambda m: m["timestamp"])
    
    for idx, msg in enumerate(sorted_messages, start=1):
        print(f"{idx}. [{msg['author']}] (ts: {msg['timestamp']:.3f}): {msg['content']}")

    print("\n[Analysis]")
    if sorted_messages[0]["author"] == "Node B":
        print("WARNING: Causal violation detected!")
        print("Node B's answer appears BEFORE Node A's question due to clock skew.")
        print("Distributed solution: use Logical Clocks (Lamport/Vector) or Google TrueTime API.")

if __name__ == "__main__":
    simulate_causality_violation()