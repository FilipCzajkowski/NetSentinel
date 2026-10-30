"""
Reporter Module
Formats and renders diagnostic results to the console (rich tables) and exports to JSON.
"""

from dataclasses import asdict
from datetime import datetime
import json
from typing import Any, Dict, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    Console = None

from .system_monitor import SystemHealthReport
from .network_checker import HostPingResult, PortScanResult


def render_terminal_dashboard(
    system_report: Optional[SystemHealthReport],
    network_endpoints: Optional[List[HostPingResult]],
    port_scan_results: Optional[List[PortScanResult]],
    target_host: Optional[str] = None,
) -> None:
    """Renders high-visibility terminal panels and tables with Rich."""
    if not Console:
        print("=== NetSentinel Diagnostic Report ===")
        if system_report:
            print(f"OS: {system_report.os_name} {system_report.os_version}")
            print(f"CPU Usage: {system_report.cpu_percent}% | RAM: {system_report.ram_percent}%")
            print(f"Overall Status: {system_report.overall_status}")
        return

    console = Console()

    # Title Banner
    console.print()
    console.print(
        Panel(
            Text("🛡️ NetSentinel - Workstation & Network Health Diagnostics", style="bold cyan", justify="center"),
            subtitle=f"[dim]Run timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            border_style="bright_blue",
        )
    )

    # 1. System Health Table
    if system_report:
        sys_table = Table(title="💻 System Resource Utilization", title_style="bold green")
        sys_table.add_column("Metric", style="bold white")
        sys_table.add_column("Value", style="cyan")
        sys_table.add_column("Status", justify="center")

        status_color = "green" if system_report.overall_status == "HEALTHY" else "yellow" if system_report.overall_status == "WARNING" else "red"
        sys_table.add_row("Operating System", f"{system_report.os_name} {system_report.os_version} ({system_report.architecture})", "[green]OK[/green]")
        sys_table.add_row("System Uptime", system_report.uptime, "[green]OK[/green]")

        cpu_color = "green" if system_report.cpu_percent < 75 else "red"
        sys_table.add_row("CPU Load", f"{system_report.cpu_percent}% ({system_report.cpu_cores_logical} logical cores)", f"[{cpu_color}]{system_report.cpu_percent}%[/{cpu_color}]")

        ram_color = "green" if system_report.ram_percent < 80 else "red"
        sys_table.add_row("RAM Memory", f"{system_report.ram_used_gb} GB / {system_report.ram_total_gb} GB ({system_report.ram_percent}%)", f"[{ram_color}]{system_report.ram_percent}%[/{ram_color}]")

        for d in system_report.disks:
            d_color = "red" if d.is_warning else "green"
            d_status = "[red]ALERT (>85%)[/red]" if d.is_warning else "[green]OK[/green]"
            sys_table.add_row(f"Disk ({d.mountpoint})", f"{d.used_gb} GB / {d.total_gb} GB used ({d.percent_used}%)", d_status)

        console.print(sys_table)
        console.print()

    # 2. Network Connectivity Table
    if network_endpoints:
        net_table = Table(title="🌐 Network & DNS Connectivity", title_style="bold blue")
        net_table.add_column("Endpoint", style="bold white")
        net_table.add_column("Resolved IP", style="cyan")
        net_table.add_column("Latency (ms)", justify="right")
        net_table.add_column("Status", justify="center")

        for ep in network_endpoints:
            if ep.is_reachable:
                lat_style = "green" if (ep.latency_ms or 0) < 60 else "yellow"
                net_table.add_row(
                    ep.host,
                    ep.ip or "N/A",
                    f"[{lat_style}]{ep.latency_ms} ms[/{lat_style}]",
                    "[bold green]ONLINE[/bold green]",
                )
            else:
                net_table.add_row(
                    ep.host,
                    ep.ip or "Failed",
                    "-",
                    f"[bold red]OFFLINE ({ep.error_message or 'Unreachable'})[/bold red]",
                )

        console.print(net_table)
        console.print()

    # 3. Port Scan Table
    if port_scan_results:
        target_name = target_host or "Localhost / Target"
        port_table = Table(title=f"🔍 Security & Port Audit for: [bold yellow]{target_name}[/bold yellow]", title_style="bold magenta")
        port_table.add_column("Port", justify="right", style="bold cyan")
        port_table.add_column("Service Name", style="white")
        port_table.add_column("State", justify="center")
        port_table.add_column("Security Assessment", style="italic")

        for p in port_scan_results:
            if p.is_open:
                state_str = "[bold green]OPEN[/bold green]"
                if p.is_security_concern:
                    assessment = "[bold red]⚠️ Attention: Sensitive service exposed![/bold red]"
                else:
                    assessment = "[green]Normal open service[/green]"
            else:
                state_str = "[dim]CLOSED[/dim]"
                assessment = "[dim]Safe / Not listening[/dim]"

            port_table.add_row(str(p.port), p.service_name, state_str, assessment)

        console.print(port_table)
        console.print()


def export_report_to_json(
    filepath: str,
    system_report: Optional[SystemHealthReport],
    network_endpoints: Optional[List[HostPingResult]],
    port_scan_results: Optional[List[PortScanResult]],
) -> None:
    """Serializes the health check results into a structured JSON file."""
    data: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "system": asdict(system_report) if system_report else None,
        "network": [asdict(ep) for ep in network_endpoints] if network_endpoints else [],
        "ports": [asdict(p) for p in port_scan_results] if port_scan_results else [],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
