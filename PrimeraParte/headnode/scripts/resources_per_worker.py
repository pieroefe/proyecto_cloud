#!/usr/bin/env python3

import subprocess

WORKERS = ["worker1", "worker2", "worker3"]

def get_meminfo(worker):
    try:
        cmd = f"ssh {worker} \"grep -E 'MemTotal|MemAvailable' /proc/meminfo\""
        output = subprocess.check_output(cmd, shell=True, text=True).strip()
        lines = output.splitlines()

        mem_total_kb = int(lines[0].split()[1])
        mem_available_kb = int(lines[1].split()[1])
        mem_used_kb = mem_total_kb - mem_available_kb

        return {
            "total": mem_total_kb // 1024,
            "used": mem_used_kb // 1024,
            "free": mem_available_kb // 1024
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    print("📊 Estado de memoria por worker:\n")
    for worker in WORKERS:
        mem = get_meminfo(worker)
        if "error" in mem:
            print(f"🔴 {worker} → Error: {mem['error']}")
        else:
            print(f"🟢 {worker} → Total: {mem['total']} MB | Usada: {mem['used']} MB | Libre: {mem['free']} MB")

if __name__ == "__main__":
    main()
