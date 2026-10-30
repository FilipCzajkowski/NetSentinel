"""
Unit tests for NetSentinel
"""

import json
import os
import tempfile
import pytest

from sentinel.system_monitor import inspect_system_health, SystemHealthReport
from sentinel.reporter import export_report_to_json
from main import parse_ports


def test_parse_ports_valid():
    """Verify valid port string parsing."""
    result = parse_ports("80, 443, 8080")
    assert result == [80, 443, 8080]


def test_parse_ports_out_of_range():
    """Verify out of range ports are ignored."""
    result = parse_ports("80, 70000, 0, 443")
    assert result == [80, 443]


def test_system_health_inspection():
    """Verify system health report contains essential fields and types."""
    report = inspect_system_health()
    assert isinstance(report, SystemHealthReport)
    assert report.os_name is not None
    assert report.cpu_cores_logical >= 1
    assert 0.0 <= report.ram_percent <= 100.0
    assert report.overall_status in ("HEALTHY", "WARNING", "CRITICAL", "UNKNOWN (psutil missing)")


def test_json_export_structure():
    """Verify JSON export creates a valid JSON file with required keys."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        report = inspect_system_health()
        export_report_to_json(tmp_path, system_report=report, network_endpoints=[], port_scan_results=[])

        assert os.path.exists(tmp_path)
        with open(tmp_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "timestamp" in data
        assert "system" in data
        assert "network" in data
        assert "ports" in data
        assert data["system"]["os_name"] == report.os_name
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
