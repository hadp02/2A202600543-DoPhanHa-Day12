import os
import sys
import subprocess
import time
import signal
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [manager] %(message)s")

# Ensure the root directory is in PYTHONPATH so `agents` can be imported
os.environ["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))

processes = []

def start_process(name, cmd, port):
    logging.info(f"Starting {name} on port {port}...")
    # Thêm môi trường để log không bị buffer, in ra ngay
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    p = subprocess.Popen(
        cmd, 
        env=env,
        stdout=sys.stdout, 
        stderr=sys.stderr
    )
    processes.append((name, p))
    time.sleep(2)  # Đợi service khởi động

def signal_handler(sig, frame):
    logging.info("Shutting down all agents...")
    for name, p in processes:
        logging.info(f"Terminating {name}...")
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logging.info("Starting Multi-Agent System...")

    # 1. Start Registry
    start_process("Registry", [sys.executable, "-m", "agents.registry"], 10000)

    # 2. Start Sub-agents (Tax & Compliance)
    start_process("Tax Agent", [sys.executable, "-m", "agents.tax_agent"], 10102)
    start_process("Compliance Agent", [sys.executable, "-m", "agents.compliance_agent"], 10103)

    # 3. Start Law Agent (Orchestrator)
    start_process("Law Agent", [sys.executable, "-m", "agents.law_agent"], 10101)

    # 4. Start Customer Agent (Entry point)
    start_process("Customer Agent", [sys.executable, "-m", "agents.customer_agent"], 10100)

    logging.info("All agents started. Waiting for connections...")
    
    # Wait for all processes to finish (which should be never unless error)
    for name, p in processes:
        p.wait()
