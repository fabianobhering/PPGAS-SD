# clock-sync/1_os_clocks.py
import time

def demonstrate_clocks():
    print("=== Demonstration: time.time() vs time.monotonic() ===")
    
    # Initial measurements
    wall_start = time.time()
    mono_start = time.monotonic()
    
    print(f"Initial Wall-clock (Unix Epoch): {wall_start:.6f} s")
    print(f"Initial Monotonic clock:         {mono_start:.6f} s")
    print("Sleeping for 1.5 seconds...\n")
    
    time.sleep(1.5)
    
    # Final measurements
    wall_end = time.time()
    mono_end = time.monotonic()
    
    delta_wall = wall_end - wall_start
    delta_mono = mono_end - mono_start
    
    print(f"Elapsed time via time.time():      {delta_wall:.6f} s")
    print(f"Elapsed time via time.monotonic(): {delta_mono:.6f} s")
    
    # Summary
    print("\n[Observations]")
    print("- time.time() reflects absolute real-world time (susceptible to step adjustments via NTP).")
    print("- time.monotonic() is strictly increasing; it must be used for local interval measurements.")

if __name__ == "__main__":
    demonstrate_clocks()