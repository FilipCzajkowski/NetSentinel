"""
Network Checker Module
Asynchronous network diagnostics, latency measurement, and TCP port scanner.
"""

import asyncio
from dataclasses import dataclass
import socket
import time
from typing import Dict, List, Optional, Tuple

COMMON_PORT_SERVICES = {
    21: "FTP (File Transfer)",
    22: "SSH (Secure Shell)",
    23: "Telnet (Unencrypted - Insecure!)",
    25: "SMTP (Mail)",
    53: "DNS (Domain Name Service)",
    80: "HTTP (Web)",
    110: "POP3 (Mail)",
    143: "IMAP (Mail)",
    443: "HTTPS (Secure Web)",
    445: "SMB (Direct Host - High Risk!)",
    1433: "MSSQL Server",
    3306: "MySQL Database",
    3389: "RDP (Remote Desktop - High Risk!)",
    5432: "PostgreSQL Database",
    8080: "HTTP Alternate / Proxy",
}


@dataclass
class HostPingResult:
    host: str
    ip: Optional[str]
    is_reachable: bool
    latency_ms: Optional[float]
    error_message: Optional[str] = None


@dataclass
class PortScanResult:
    port: int
    service_name: str
    is_open: bool
    is_security_concern: bool


async def check_tcp_port(
    host: str, port: int, timeout: float = 1.0
) -> PortScanResult:
    """Asynchronously checks if a specific TCP port is open on the target host."""
    service = COMMON_PORT_SERVICES.get(port, "Custom/Unknown Service")
    is_security_risk = port in (21, 23, 445, 3389)

    try:
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return PortScanResult(
            port=port,
            service_name=service,
            is_open=True,
            is_security_concern=is_security_risk,
        )
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return PortScanResult(
            port=port,
            service_name=service,
            is_open=False,
            is_security_concern=False,
        )


async def check_host_connectivity(
    host: str, test_port: int = 53, timeout: float = 2.0
) -> HostPingResult:
    """
    Checks if a host resolves via DNS and is reachable over TCP.
    Default port 53 works great for DNS servers (8.8.8.8, 1.1.1.1).
    For web domains (e.g. google.com), checks port 443.
    """
    port_to_test = test_port if host.replace(".", "").isdigit() else 443

    # Step 1: DNS Resolution
    start_time = time.perf_counter()
    try:
        resolved_ip = socket.gethostbyname(host)
    except socket.gaierror as e:
        return HostPingResult(
            host=host,
            ip=None,
            is_reachable=False,
            latency_ms=None,
            error_message="DNS Resolution Failed",
        )

    # Step 2: Connection latency
    try:
        conn = asyncio.open_connection(resolved_ip, port_to_test)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        writer.close()
        await writer.wait_closed()
        return HostPingResult(
            host=host,
            ip=resolved_ip,
            is_reachable=True,
            latency_ms=latency,
            error_message=None,
        )
    except Exception as e:
        return HostPingResult(
            host=host,
            ip=resolved_ip,
            is_reachable=False,
            latency_ms=None,
            error_message=str(e),
        )


async def scan_target_ports(
    target_host: str, ports: List[int], timeout: float = 1.0
) -> List[PortScanResult]:
    """Scans multiple ports concurrently using asyncio.gather."""
    tasks = [check_tcp_port(target_host, port, timeout) for port in ports]
    return await asyncio.gather(*tasks)


async def diagnose_critical_endpoints(
    endpoints: Optional[List[str]] = None,
) -> List[HostPingResult]:
    """Diagnoses connectivity to primary public and DNS services."""
    if endpoints is None:
        endpoints = [
            "8.8.8.8",        # Google Public DNS
            "1.1.1.1",        # Cloudflare DNS
            "google.com",     # Public Web Connectivity
            "github.com",     # Developer / Git Access
        ]

    tasks = [check_host_connectivity(ep) for ep in endpoints]
    return await asyncio.gather(*tasks)
