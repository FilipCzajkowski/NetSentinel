"""
NetSentinel - Main CLI Entry Point
Author: Filip Czajkowski
"""

import argparse
import asyncio
import sys
from typing import List

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

from sentinel.system_monitor import inspect_system_health, SystemHealthReport
from sentinel.network_checker import diagnose_critical_endpoints, scan_target_ports, HostPingResult, PortScanResult
from sentinel.reporter import render_terminal_dashboard, export_report_to_json


def parse_ports(port_string: str) -> List[int]:
    """Parses a comma-separated list of port numbers."""
    try:
        ports = [int(p.strip()) for p in port_string.split(",") if p.strip()]
        return [p for p in ports if 1 <= p <= 65535]
    except ValueError:
        print(f"Error: Invalid port specification: '{port_string}'. Please use numbers separated by commas (e.g. 80,443).")
        sys.exit(1)


async def async_run(args: argparse.Namespace) -> None:
    # 1. System health check
    system_report: SystemHealthReport | None = None
    if not args.skip_system:
        system_report = inspect_system_health()

    # 2. Network connectivity check
    network_endpoints: List[HostPingResult] | None = None
    if not args.skip_network:
        network_endpoints = await diagnose_critical_endpoints()

    # 3. Port scan check
    port_results: List[PortScanResult] | None = None
    if not args.skip_ports:
        target_ports = parse_ports(args.ports)
        port_results = await scan_target_ports(args.target, target_ports, timeout=args.timeout)

    # 4. Render terminal dashboard
    render_terminal_dashboard(
        system_report=system_report,
        network_endpoints=network_endpoints,
        port_scan_results=port_results,
        target_host=args.target,
    )

    # 5. Export JSON if requested
    if args.export:
        export_report_to_json(
            filepath=args.export,
            system_report=system_report,
            network_endpoints=network_endpoints,
            port_scan_results=port_results,
        )
        print(f"✅ Diagnostic report successfully exported to: {args.export}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="NetSentinel",
        description="🛡️ NetSentinel - Workstation & Network Health Diagnostics CLI Tool",
    )
    parser.add_argument(
        "-t", "--target",
        type=str,
        default="127.0.0.1",
        help="Target IP or hostname to audit open ports (default: 127.0.0.1)",
    )
    parser.add_argument(
        "-p", "--ports",
        type=str,
        default="21,22,23,80,443,445,3389,8080",
        help="Comma-separated list of ports to scan (default: 21,22,23,80,443,445,3389,8080)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="Timeout in seconds for network socket connection (default: 1.0s)",
    )
    parser.add_argument(
        "--skip-system",
        action="store_true",
        help="Skip gathering local hardware and system performance metrics",
    )
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="Skip checking connectivity to primary DNS and web services",
    )
    parser.add_argument(
        "--skip-ports",
        action="store_true",
        help="Skip target port scan",
    )
    parser.add_argument(
        "-e", "--export",
        type=str,
        help="Export full audit results to a JSON file (e.g. report.json)",
    )

    args = parser.parse_args()
    asyncio.run(async_run(args))


if __name__ == "__main__":
    main()
