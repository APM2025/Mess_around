"""
Tests for user activity logging module.
"""

import pytest
from pathlib import Path
from datetime import datetime
from src.layer2_business_logic.user_log import UserActivityLogger


@pytest.fixture
def log_file(tmp_path):
    """Create a temporary log file path."""
    return tmp_path / "test_activity.log"


@pytest.fixture
def logger(log_file):
    """Create logger instance."""
    return UserActivityLogger(log_file)


# Phase 1: Basic instantiation
def test_logger_can_be_created(logger, log_file):
    """Test that UserActivityLogger can be instantiated."""
    assert logger is not None
    assert logger.log_file == log_file


def test_logger_creates_log_file(logger, log_file):
    """Test that logger creates the log file."""
    # Log something to trigger file creation
    logger.log_action("test", "create", "testing")
    assert log_file.exists()


# Phase 2: Logging user actions
def test_log_query_action(logger, log_file):
    """Test logging a query action."""
    logger.log_action("query", "filter_data", "vaccine_code=MMR1")

    # Read log file
    content = log_file.read_text()
    assert "QUERY" in content
    assert "filter_data" in content
    assert "vaccine_code=MMR1" in content


def test_log_create_action(logger, log_file):
    """Test logging a create action."""
    logger.log_action("create", "geographic_area", "area_code=E99999999")

    content = log_file.read_text()
    assert "CREATE" in content
    assert "geographic_area" in content
    assert "area_code=E99999999" in content


def test_log_update_action(logger, log_file):
    """Test logging an update action."""
    logger.log_action("update", "vaccine", "vaccine_code=TEST1, vaccine_name=Updated")

    content = log_file.read_text()
    assert "UPDATE" in content
    assert "vaccine" in content


def test_log_delete_action(logger, log_file):
    """Test logging a delete action."""
    logger.log_action("delete", "coverage_record", "coverage_id=123")

    content = log_file.read_text()
    assert "DELETE" in content
    assert "coverage_record" in content


def test_log_export_action(logger, log_file):
    """Test logging an export action."""
    logger.log_action("export", "csv", "file=output.csv, rows=150")

    content = log_file.read_text()
    assert "EXPORT" in content
    assert "csv" in content


def test_log_includes_timestamp(logger, log_file):
    """Test that log entries include timestamps."""
    logger.log_action("test", "timestamp_check", "testing")

    content = log_file.read_text()
    # Check for date pattern (YYYY-MM-DD)
    assert content.count("-") >= 2  # At least two dashes in date


def test_multiple_log_entries(logger, log_file):
    """Test logging multiple actions."""
    logger.log_action("query", "action1", "test1")
    logger.log_action("create", "action2", "test2")
    logger.log_action("update", "action3", "test3")

    content = log_file.read_text()
    lines = content.strip().split('\n')
    assert len(lines) >= 3


# Phase 3: Reading and querying logs
def test_get_recent_logs(logger):
    """Test retrieving recent log entries."""
    logger.log_action("query", "test1", "data1")
    logger.log_action("create", "test2", "data2")
    logger.log_action("update", "test3", "data3")

    recent = logger.get_recent_logs(n=2)

    assert len(recent) == 2
    assert "test3" in recent[0]  # Most recent first
    assert "test2" in recent[1]


def test_get_logs_by_action_type(logger):
    """Test filtering logs by action type."""
    logger.log_action("query", "filter1", "data1")
    logger.log_action("create", "create1", "data2")
    logger.log_action("query", "filter2", "data3")
    logger.log_action("update", "update1", "data4")

    query_logs = logger.get_logs_by_type("query")

    assert len(query_logs) == 2
    assert all("QUERY" in log for log in query_logs)


def test_get_all_logs(logger):
    """Test retrieving all logs."""
    logger.log_action("query", "test1", "data1")
    logger.log_action("create", "test2", "data2")

    all_logs = logger.get_all_logs()

    assert len(all_logs) == 2


def test_get_log_summary(logger):
    """Test getting summary statistics of logs."""
    logger.log_action("query", "test1", "data1")
    logger.log_action("query", "test2", "data2")
    logger.log_action("create", "test3", "data3")
    logger.log_action("update", "test4", "data4")

    summary = logger.get_log_summary()

    assert summary['total'] == 4
    assert summary['query'] == 2
    assert summary['create'] == 1
    assert summary['update'] == 1
