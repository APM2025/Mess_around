"""
User activity logging module for tracking database operations.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict


class UserActivityLogger:
    """Logs all user actions to a file for audit trail."""

    def __init__(self, log_file: Path = None):
        """
        Initialize activity logger.

        Args:
            log_file: Path to log file (default: logs/user_activity.log)
        """
        if log_file is None:
            log_file = Path("logs") / "user_activity.log"

        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_action(
        self,
        action_type: str,
        operation: str,
        details: str = ""
    ) -> None:
        """
        Log a user action.

        Args:
            action_type: Type of action (query, create, update, delete, export)
            operation: Specific operation performed
            details: Additional details about the action
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {action_type.upper()}: {operation}"

        if details:
            log_entry += f" | {details}"

        log_entry += "\n"

        # Append to log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def get_recent_logs(self, n: int = 10) -> List[str]:
        """
        Get the N most recent log entries.

        Args:
            n: Number of entries to retrieve

        Returns:
            List of log entries (most recent first)
        """
        if not self.log_file.exists():
            return []

        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Return last n lines in reverse order
        return [line.strip() for line in reversed(lines[-n:])]

    def get_logs_by_type(self, action_type: str) -> List[str]:
        """
        Get all logs of a specific action type.

        Args:
            action_type: Type to filter by (query, create, update, delete, export)

        Returns:
            List of matching log entries
        """
        if not self.log_file.exists():
            return []

        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        action_upper = action_type.upper()
        return [line.strip() for line in lines if action_upper in line]

    def get_all_logs(self) -> List[str]:
        """
        Get all log entries.

        Returns:
            List of all log entries
        """
        if not self.log_file.exists():
            return []

        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        return [line.strip() for line in lines]

    def get_log_summary(self) -> Dict[str, int]:
        """
        Get summary statistics of logged actions.

        Returns:
            Dict with counts by action type
        """
        if not self.log_file.exists():
            return {'total': 0}

        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        summary = {'total': len(lines)}

        # Count each action type
        action_types = ['query', 'create', 'update', 'delete', 'export']
        for action_type in action_types:
            action_upper = action_type.upper()
            count = sum(1 for line in lines if action_upper in line)
            if count > 0:
                summary[action_type] = count

        return summary
