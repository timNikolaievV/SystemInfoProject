from __future__ import annotations
import platform, socket, time, json, subprocess
from datetime import datetime
from typing import Any, Dict, List
import psutil

def _safe_run(cmd: List[str], timeout: int = 3):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def get_os_info():
    return {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }

def get_uptime():
    boot_ts = psutil.boot_time()
    now = time.time()
    seconds = int(now - boot_ts)
    return {
        "boot_time_iso": datetime.fromtimestamp(boot_ts).isoformat(),
        "uptime_seconds": seconds,
        "uptime_human": f"{seconds//3600}h {(seconds%3600)//60}m"
    }

def get_cpu_info():
    loadavg = None
    try:
        l1, l5, l15 = psutil.getloadavg()
        loadavg = {"1min": l1, "5min": l5, "15min": l15}
    except:
        pass
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "freq_mhz": getattr(psutil.cpu_freq(), "current", None),
        "percent": psutil.cpu_percent(interval=0.7),
        "loadavg": loadavg
    }

def get_memory_info():
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()
    return {
        "ram": {
            "total": vm.total,
            "available": vm.available,
            "used": vm.used,
            "percent": vm.percent,
        },
        "swap": {
            "total": sm.total,
            "used": sm.used,
            "percent": sm.percent,
        }
    }

def get_disks_info():
    disks = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        disks.append({
            "device": part.device,
            "mountpoint": part.mountpoint,
            "fstype": part.fstype,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent
        })
    return disks

def get_network_info():
    interfaces = {}
    addrs = psutil.net_if_addrs()
    io = psutil.net_io_counters(pernic=True)

    for nic, addr_list in addrs.items():
        ips = []
        for a in addr_list:
            if a.family.name in ("AF_INET", "AF_INET6"):
                ips.append({"family": a.family.name, "address": a.address})
        interfaces[nic] = {
            "ips": ips,
            "bytes_sent": getattr(io.get(nic), "bytes_sent", None),
            "bytes_recv": getattr(io.get(nic), "bytes_recv", None),
        }

    host = "8.8.8.8"
    cmd = ["ping", "-n", "1", host] if platform.system()=="Windows" else ["ping","-c","1",host]
    code, out, err = _safe_run(cmd)

    return {
        "interfaces": interfaces,
        "ping_ok": code == 0,
        "ping_stdout": out,
        "ping_stderr": err
    }

def get_top_processes(n=10):
    procs = []
    for p in psutil.process_iter(["pid","name","username","cpu_percent","memory_percent"]):
        procs.append(p.info)
    procs.sort(key=lambda x: x.get("cpu_percent") or 0, reverse=True)
    return procs[:n]

def collect_all(top_n=10):
    return {
        "timestamp": datetime.utcnow().isoformat()+"Z",
        "os": get_os_info(),
        "uptime": get_uptime(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disks": get_disks_info(),
        "network": get_network_info(),
        "top_processes": get_top_processes(top_n),
    }