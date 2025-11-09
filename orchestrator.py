#!/usr/bin/env python3
"""
Simple orchestrator to run collector then decitor (for testing).
In production, cron jobs run them individually.
"""
import time
import subprocess

def run_collector():
    subprocess.run(["python","collector.py"])

def run_decitor():
    subprocess.run(["python","decitor.py"])

if __name__=="__main__":
    run_collector()
    # wait a couple seconds (simulate)
    time.sleep(2)
    run_decitor()
