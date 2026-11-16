import random
import time
import ipaddress
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:8000/api/products"

TOTAL_VISITORS = 100
TOTAL_ROUNDS = 3


def generate_public_ip():
    while True:
        ip = ipaddress.IPv4Address(random.getrandbits(32))

        # Exclude private, reserved, multicast and other
        # non-public address ranges.
        if ip.is_global:
            return str(ip)


# Generate 100 different simulated public IPs
SIMULATED_IPS = list({generate_public_ip() for _ in range(TOTAL_VISITORS)})

print(f"Generated {len(SIMULATED_IPS)} simulated visitors")

for round_number in range(1, TOTAL_ROUNDS + 1):

    print(f"\nStarting round {round_number}")

    visitors = SIMULATED_IPS.copy()
    random.shuffle(visitors)

    for ip in visitors:

        request = Request(BASE_URL, headers={"X-Simulated-IP": ip})

        try:
            with urlopen(request, timeout=10) as response:
                print(f"{ip} -> Status: {response.status}")

        except Exception as error:
            print(f"{ip} -> Error: {error}")

        time.sleep(random.uniform(0.2, 0.8))

print("\nTraffic simulation completed.")
