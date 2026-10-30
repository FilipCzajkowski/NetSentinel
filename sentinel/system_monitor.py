"""
System Monitor Module
Collects workstation hardware and OS health metrics using psutil.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
import platform
import time
from typing import Dict, List, Any

try:
    import psutil
except ImportError:
    psutil = None


@dataclass
class DiskPartitionInfo:
    mountpoint: str
    filesystem: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float
    is_warning: bool


@dataclass
class SystemHealthReport:
    os_name: str
    os_version: str
    architecture: str
    uptime: str
    cpu_percent: float
    cpu_cores_logical: int
    cpu_cores_physical: int
    ram_total_gb: float
    ram_used_gb: float
    ram_percent: float
    disks: List[DiskPartitionInfo]
    overall_status: str  # OK, WARNING, CRITICAL


def get_uptime_string() -> str:
    """Calculates human-readable system uptime."""
    if psutil:
        boot_timestamp = psutil.boot_time()
        uptime_seconds = time.time() - boot_timestamp
        uptime_delta = timedelta(seconds=int(uptime_seconds))
        return str(uptime_delta)
    return "N/A"


def inspect_system_health() -> SystemHealthReport:
    """Gathers comprehensive workstation performance and storage statistics."""
    os_name = platform.system()
    os_version = platform.release()
    arch = platform.machine()
    uptime = get_uptime_string()

    if not psutil:
        return SystemHealthReport(
            os_name=os_name,
            os_version=os_version,
            architecture=arch,
            uptime=uptime,
            cpu_percent=0.0,
            cpu_cores_logical=1,
            cpu_cores_physical=1,
            ram_total_gb=0.0,
            ram_used_gb=0.0,
            ram_percent=0.0,
            disks=[],
            overall_status="UNKNOWN (psutil missing)",
        )

    # CPU metrics
    cpu_percent = psutil.cpu_percent(interval=0.5)
    logical_cores = psutil.cpu_count(logical=True) or 1
    physical_cores = psutil.cpu_count(logical=False) or logical_cores

    # Memory metrics
    vm = psutil.virtual_memory()
    ram_total_gb = round(vm.total / (1024 ** 3), 2)
    ram_used_gb = round(vm.used / (1024 ** 3), 2)
    ram_percent = vm.percent

    # Disk metrics
    disks: List[DiskPartitionInfo] = []
    has_disk_warning = False

    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            pct = usage.percent
            is_warning = pct >= 85.0
            if is_warning:
                has_disk_warning = True

            disks.append(
                DiskPartitionInfo(
                    mountpoint=part.mountpoint,
                    filesystem=part.fstype,
                    total_gb=round(usage.total / (1024 ** 3), 2),
                    used_gb=round(usage.used / (1024 ** 3), 2),
                    free_gb=round(usage.free / (1024 ** 3), 2),
                    percent_used=pct,
                    is_warning=is_warning,
                )
            )
        except (PermissionError, OSError):
            continue

    # Determine overall status
    if cpu_percent >= 90.0 or ram_percent >= 90.0:
        overall_status = "CRITICAL"
    elif cpu_percent >= 75.0 or ram_percent >= 80.0 or has_disk_warning:
        overall_status = "WARNING"
    else:
        overall_status = "HEALTHY"

    return SystemHealthReport(
        os_name=os_name,
        os_version=os_version,
        architecture=arch,
        uptime=uptime,
        cpu_percent=cpu_percent,
        cpu_cores_logical=logical_cores,
        cpu_cores_physical=physical_cores,
        ram_total_gb=ram_total_gb,
        ram_used_gb=ram_used_gb,
        ram_percent=ram_percent,
        disks=disks,
        overall_status=overall_status,
    )
