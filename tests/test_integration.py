def test_collector_runs():
    import subprocess
    r = subprocess.run(["python","collector.py"], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0
