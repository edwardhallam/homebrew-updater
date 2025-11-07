#!/usr/bin/env python3
"""
Unit tests for homebrew_updater.py
Run with: python3 -m pytest tests/test_homebrew_updater.py -v
Or: python3 tests/test_homebrew_updater.py
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from io import StringIO

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import homebrew_updater


class TestWebhookNotifications(unittest.TestCase):
    """Test webhook notification functionality (Discord & Slack)"""

    @patch('homebrew_updater.urllib.request.urlopen')
    def test_send_discord_helper_success(self, mock_urlopen):
        """Test successful Discord notification via _send_discord"""
        # Save original and set test webhook
        original_webhook = homebrew_updater.DISCORD_WEBHOOK_URL
        homebrew_updater.DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/test/test"

        mock_response = MagicMock()
        mock_response.status = 204
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = homebrew_updater._send_discord("Test message")
        self.assertTrue(result)
        self.assertTrue(mock_urlopen.called)

        # Restore original
        homebrew_updater.DISCORD_WEBHOOK_URL = original_webhook

    @patch('homebrew_updater.urllib.request.urlopen')
    def test_send_slack_helper_success(self, mock_urlopen):
        """Test successful Slack notification via _send_slack"""
        # Save original and set test webhook
        original_webhook = homebrew_updater.SLACK_WEBHOOK_URL
        homebrew_updater.SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/test/test/test"

        mock_response = MagicMock()
        mock_response.status = 200  # Slack returns 200, not 204
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = homebrew_updater._send_slack("Test message")
        self.assertTrue(result)
        self.assertTrue(mock_urlopen.called)

        # Restore original
        homebrew_updater.SLACK_WEBHOOK_URL = original_webhook

    def test_send_discord_helper_no_webhook(self):
        """Test _send_discord when webhook is not configured"""
        original_webhook = homebrew_updater.DISCORD_WEBHOOK_URL
        homebrew_updater.DISCORD_WEBHOOK_URL = ""

        result = homebrew_updater._send_discord("Test message")
        self.assertFalse(result)

        # Restore original
        homebrew_updater.DISCORD_WEBHOOK_URL = original_webhook

    def test_send_slack_helper_no_webhook(self):
        """Test _send_slack when webhook is not configured"""
        original_webhook = homebrew_updater.SLACK_WEBHOOK_URL
        homebrew_updater.SLACK_WEBHOOK_URL = ""

        result = homebrew_updater._send_slack("Test message")
        self.assertFalse(result)

        # Restore original
        homebrew_updater.SLACK_WEBHOOK_URL = original_webhook

    @patch('homebrew_updater.send_macos_notification')
    @patch('homebrew_updater._send_discord')
    def test_send_notification_discord_platform(self, mock_discord, mock_macos):
        """Test send_notification with Discord platform"""
        original_platform = homebrew_updater.NOTIFICATION_PLATFORM
        homebrew_updater.NOTIFICATION_PLATFORM = "discord"
        mock_discord.return_value = True

        homebrew_updater.send_notification("Test message")

        mock_discord.assert_called_once()
        mock_macos.assert_called_once()

        # Restore original
        homebrew_updater.NOTIFICATION_PLATFORM = original_platform

    @patch('homebrew_updater.send_macos_notification')
    @patch('homebrew_updater._send_slack')
    def test_send_notification_slack_platform(self, mock_slack, mock_macos):
        """Test send_notification with Slack platform"""
        original_platform = homebrew_updater.NOTIFICATION_PLATFORM
        homebrew_updater.NOTIFICATION_PLATFORM = "slack"
        mock_slack.return_value = True

        homebrew_updater.send_notification("Test message")

        mock_slack.assert_called_once()
        mock_macos.assert_called_once()

        # Restore original
        homebrew_updater.NOTIFICATION_PLATFORM = original_platform

    @patch('homebrew_updater.send_macos_notification')
    @patch('homebrew_updater._send_discord')
    @patch('homebrew_updater._send_slack')
    def test_send_notification_both_platforms(self, mock_slack, mock_discord, mock_macos):
        """Test send_notification with both platforms"""
        original_platform = homebrew_updater.NOTIFICATION_PLATFORM
        homebrew_updater.NOTIFICATION_PLATFORM = "both"
        mock_discord.return_value = True
        mock_slack.return_value = True

        homebrew_updater.send_notification("Test message")

        mock_discord.assert_called_once()
        mock_slack.assert_called_once()
        mock_macos.assert_called_once()

        # Restore original
        homebrew_updater.NOTIFICATION_PLATFORM = original_platform

    @patch('homebrew_updater.urllib.request.urlopen')
    def test_send_discord_notification_success(self, mock_urlopen):
        """Test successful Discord notification (backwards compatibility)"""
        mock_response = MagicMock()
        mock_response.status = 204
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Should not raise exception
        homebrew_updater.send_discord_notification("Test message")

        # Verify urlopen was called
        self.assertTrue(mock_urlopen.called)

    @patch('homebrew_updater.urllib.request.urlopen')
    def test_send_discord_notification_error(self, mock_urlopen):
        """Test Discord notification with error response"""
        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Should not raise exception (errors are logged)
        homebrew_updater.send_discord_notification("Test message")

    @patch('homebrew_updater.urllib.request.urlopen')
    def test_send_discord_notification_timeout(self, mock_urlopen):
        """Test Discord notification with timeout"""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Timeout")

        # Should not raise exception (errors are logged)
        homebrew_updater.send_discord_notification("Test message")

    @patch('homebrew_updater.send_macos_notification')
    def test_send_discord_notification_no_webhook(self, mock_macos):
        """Test Discord notification when webhook is not configured"""
        original_webhook = homebrew_updater.DISCORD_WEBHOOK_URL
        homebrew_updater.DISCORD_WEBHOOK_URL = ""

        # Should not raise exception and should send macOS notification
        homebrew_updater.send_discord_notification("Test message")
        mock_macos.assert_called_once()

        # Restore original
        homebrew_updater.DISCORD_WEBHOOK_URL = original_webhook


class TestBrewCommands(unittest.TestCase):
    """Test Homebrew command execution"""

    @patch('homebrew_updater.subprocess.run')
    def test_run_brew_command_success(self, mock_run):
        """Test successful brew command"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Success",
            stderr=""
        )

        success, output = homebrew_updater.run_brew_command(["update"])
        self.assertTrue(success)
        self.assertEqual(output, "Success")

    @patch('homebrew_updater.subprocess.run')
    def test_run_brew_command_failure(self, mock_run):
        """Test failed brew command"""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error occurred"
        )

        success, output = homebrew_updater.run_brew_command(["update"])
        self.assertFalse(success)
        self.assertIn("Error occurred", output)

    @patch('homebrew_updater.subprocess.run')
    def test_run_brew_command_timeout(self, mock_run):
        """Test brew command timeout"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("brew", 10)

        success, output = homebrew_updater.run_brew_command(["update"])
        self.assertFalse(success)
        self.assertIn("timed out", output.lower())

    @patch('homebrew_updater.run_brew_command')
    def test_brew_update_success(self, mock_run_brew):
        """Test brew update success"""
        mock_run_brew.return_value = (True, "Updated")

        result = homebrew_updater.brew_update()
        self.assertTrue(result)

    @patch('homebrew_updater.run_brew_command')
    def test_brew_upgrade_formulae_success(self, mock_run_brew):
        """Test brew upgrade formulae"""
        # Mock outdated check
        mock_run_brew.side_effect = [
            (True, "package1\npackage2\npackage3"),  # outdated
            (True, "Upgraded")  # upgrade
        ]

        success, packages = homebrew_updater.brew_upgrade_formulae()
        self.assertTrue(success)
        self.assertEqual(len(packages), 3)
        self.assertIn("package1", packages)

    @patch('homebrew_updater.run_brew_command')
    def test_brew_upgrade_formulae_none_outdated(self, mock_run_brew):
        """Test brew upgrade when no formulae are outdated"""
        mock_run_brew.return_value = (True, "")

        success, packages = homebrew_updater.brew_upgrade_formulae()
        self.assertTrue(success)
        self.assertEqual(packages, [])

    @patch('homebrew_updater.run_brew_command')
    def test_brew_upgrade_casks_success(self, mock_run_brew):
        """Test brew upgrade casks with successful upgrades"""
        mock_run_brew.side_effect = [
            (True, "cask1\ncask2"),  # outdated
            (True, "✔︎ Cask cask1 (1.0.0)\n✔︎ Cask cask2 (2.0.0)")  # upgrade with success indicators
        ]

        success, casks, warnings = homebrew_updater.brew_upgrade_casks()
        self.assertTrue(success)
        self.assertEqual(len(casks), 2)
        self.assertIn("cask1", casks)
        self.assertIn("cask2", casks)
        self.assertEqual(len(warnings), 0)  # No warnings when all casks upgrade cleanly

    @patch('homebrew_updater.run_brew_command')
    def test_brew_upgrade_casks_with_warnings(self, mock_run_brew):
        """Test brew upgrade casks with partial success (some cleanup warnings)"""
        mock_run_brew.side_effect = [
            (True, "cask1\ncask2\ncask3"),  # 3 outdated casks
            (False, "✔︎ Cask cask1 (1.0.0)\n✔︎ Cask cask2 (2.0.0)\nError: cask3 cleanup failed")  # 2 succeed, 1 has warnings
        ]

        success, casks, warnings = homebrew_updater.brew_upgrade_casks()
        self.assertTrue(success)  # Overall success because some casks upgraded
        self.assertEqual(len(casks), 2)  # Two casks upgraded successfully
        self.assertIn("cask1", casks)
        self.assertIn("cask2", casks)
        self.assertEqual(len(warnings), 1)  # One cask had warnings
        self.assertIn("cask3", warnings)


class TestGhostCaskHealing(unittest.TestCase):
    """Test ghost cask healing functionality"""

    @patch('homebrew_updater.subprocess.run')
    @patch('homebrew_updater.run_brew_command')
    @patch('homebrew_updater.get_caskroom_path')
    @patch('homebrew_updater.Path')
    def test_heal_ghost_casks_missing_dir(self, mock_path_class, mock_get_caskroom,
                                          mock_run_brew, mock_subprocess):
        """Test healing when cask directory doesn't exist"""
        # Mock the caskroom path
        mock_caskroom = MagicMock()
        mock_get_caskroom.return_value = mock_caskroom

        # Mock cask directory doesn't exist
        mock_cask_dir = MagicMock()
        mock_cask_dir.exists.return_value = False
        mock_caskroom.__truediv__.return_value = mock_cask_dir

        # Mock brew list casks
        mock_run_brew.side_effect = [
            (True, "ghost-cask"),  # list casks
            (True, "Uninstalled")  # uninstall
        ]

        removed = homebrew_updater.heal_ghost_casks()

        # Should identify and remove the ghost cask
        self.assertEqual(len(removed), 1)
        self.assertIn("ghost-cask", removed)


class TestLogging(unittest.TestCase):
    """Test logging functionality"""

    @patch('homebrew_updater.LOG_DIR')
    def test_cleanup_old_logs(self, mock_log_dir):
        """Test that old log files are removed"""
        # Create 15 mock log files with proper comparison support
        mock_logs = []
        for i in range(15):
            mock_log = MagicMock()
            mock_log.name = f"homebrew-updater-{i:03d}.log"
            mock_log.__lt__ = lambda self, other: self.name < other.name
            mock_log.__gt__ = lambda self, other: self.name > other.name
            mock_logs.append(mock_log)

        # Sort them so newest (highest number) is first when reversed
        mock_logs.sort(key=lambda x: x.name, reverse=True)
        mock_log_dir.glob.return_value = mock_logs

        homebrew_updater.cleanup_old_logs()

        # Should keep 10, remove 5 oldest
        self.assertEqual(sum(1 for log in mock_logs if log.unlink.called), 5)

    def test_log_function(self):
        """Test that log function writes to file and stdout"""
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('sys.stdout', new_callable=StringIO):
                homebrew_updater.log("Test message", "INFO")

                # Verify file was written to
                mock_file.assert_called()


class TestMainFlow(unittest.TestCase):
    """Test main execution flow"""

    @patch('homebrew_updater.cleanup_old_logs')
    @patch('homebrew_updater.send_notification')
    @patch('homebrew_updater.brew_update')
    @patch('homebrew_updater.heal_ghost_casks')
    @patch('homebrew_updater.brew_upgrade_formulae')
    @patch('homebrew_updater.brew_upgrade_casks')
    @patch('homebrew_updater.brew_cleanup')
    @patch('homebrew_updater.brew_doctor')
    def test_main_success(self, mock_doctor, mock_cleanup, mock_upgrade_casks,
                          mock_upgrade_formulae, mock_heal, mock_update,
                          mock_notification, mock_cleanup_logs):
        """Test main flow when all operations succeed"""
        mock_update.return_value = True
        mock_heal.return_value = ["ghost-cask"]
        mock_upgrade_formulae.return_value = (True, ["pkg1", "pkg2", "pkg3", "pkg4", "pkg5"])
        mock_upgrade_casks.return_value = (True, ["cask1", "cask2", "cask3"], [])  # No warnings

        result = homebrew_updater.main()

        self.assertEqual(result, 0)
        # Verify all operations were called
        mock_update.assert_called_once()
        mock_heal.assert_called_once()
        mock_upgrade_formulae.assert_called_once()
        mock_upgrade_casks.assert_called_once()
        mock_cleanup.assert_called_once()

    @patch('homebrew_updater.cleanup_old_logs')
    @patch('homebrew_updater.send_notification')
    @patch('homebrew_updater.brew_update')
    def test_main_update_failure(self, mock_update, mock_notification, mock_cleanup_logs):
        """Test main flow when brew update fails"""
        mock_update.return_value = False

        result = homebrew_updater.main()

        self.assertEqual(result, 1)
        # Verify error notification was sent (check kwargs for error=True)
        self.assertTrue(any(
            call.kwargs.get('error', False)
            for call in mock_notification.call_args_list
        ))


class TestMonthlyReminder(unittest.TestCase):
    """Test monthly cleanup reminder functionality"""

    @patch('homebrew_updater.datetime')
    @patch('homebrew_updater.MONTHLY_CLEANUP_REMINDER_DAY', 15)
    @patch('homebrew_updater.ENABLE_MONTHLY_CLEANUP_REMINDER', True)
    @patch('homebrew_updater.get_last_reminder_date')
    def test_should_send_reminder_on_reminder_day(self, mock_get_last, mock_datetime_module):
        """Test that reminder should be sent on the 15th"""
        from datetime import datetime
        # Mock today as the 15th
        mock_now = Mock()
        mock_now.day = 15
        mock_now.year = 2025
        mock_now.month = 11
        mock_datetime_module.now.return_value = mock_now

        # Mock strptime to return a datetime object for last month's reminder
        mock_last_date = datetime(2025, 10, 15)
        mock_datetime_module.strptime.return_value = mock_last_date

        # No previous reminder this month
        mock_get_last.return_value = "2025-10-15"  # Last month

        result = homebrew_updater.should_send_monthly_reminder()
        self.assertTrue(result)

    @patch('homebrew_updater.datetime')
    @patch('homebrew_updater.MONTHLY_CLEANUP_REMINDER_DAY', 15)
    @patch('homebrew_updater.ENABLE_MONTHLY_CLEANUP_REMINDER', True)
    @patch('homebrew_updater.get_last_reminder_date')
    def test_should_not_send_reminder_on_wrong_day(self, mock_get_last, mock_datetime_module):
        """Test that reminder is not sent on other days"""
        from datetime import datetime
        # Mock today as the 14th
        mock_now = Mock()
        mock_now.day = 14
        mock_now.year = 2025
        mock_now.month = 11
        mock_datetime_module.now.return_value = mock_now

        result = homebrew_updater.should_send_monthly_reminder()
        self.assertFalse(result)

    @patch('homebrew_updater.datetime')
    @patch('homebrew_updater.MONTHLY_CLEANUP_REMINDER_DAY', 15)
    @patch('homebrew_updater.ENABLE_MONTHLY_CLEANUP_REMINDER', True)
    @patch('homebrew_updater.get_last_reminder_date')
    def test_should_not_send_reminder_twice_same_month(self, mock_get_last, mock_datetime_module):
        """Test that reminder is not sent twice in the same month"""
        from datetime import datetime
        # Mock today as the 15th
        mock_now = Mock()
        mock_now.day = 15
        mock_now.year = 2025
        mock_now.month = 11
        mock_datetime_module.now.return_value = mock_now

        # Mock strptime to return a datetime object for the last reminder date
        mock_last_date = datetime(2025, 11, 15)
        mock_datetime_module.strptime.return_value = mock_last_date

        # Already sent reminder this month
        mock_get_last.return_value = "2025-11-15"

        result = homebrew_updater.should_send_monthly_reminder()
        self.assertFalse(result)

    @patch('homebrew_updater.ENABLE_MONTHLY_CLEANUP_REMINDER', False)
    def test_should_not_send_when_disabled(self):
        """Test that reminder is not sent when disabled"""
        result = homebrew_updater.should_send_monthly_reminder()
        self.assertFalse(result)

    @patch('homebrew_updater.subprocess.run')
    @patch('homebrew_updater.send_notification')
    @patch('homebrew_updater.save_last_reminder_date')
    @patch('homebrew_updater.datetime')
    def test_send_monthly_cleanup_reminder(self, mock_datetime_module, mock_save, mock_notification, mock_subprocess):
        """Test sending monthly cleanup reminder"""
        from datetime import datetime
        # Mock subprocess to return cache size
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "1.5G\t/opt/homebrew/Library/Caches/Homebrew"
        mock_subprocess.return_value = mock_result

        # Mock datetime for saving
        mock_now = datetime(2025, 11, 15, 10, 0, 0)
        mock_datetime_module.now.return_value = mock_now

        homebrew_updater.send_monthly_cleanup_reminder()

        # Verify notification was sent with correct content
        mock_notification.assert_called_once()
        notification_msg = mock_notification.call_args[0][0]
        self.assertIn("Monthly Homebrew Cleanup Reminder", notification_msg)
        self.assertIn("1.5G", notification_msg)
        self.assertIn("brew cleanup --prune=all", notification_msg)

        # Verify date was saved
        mock_save.assert_called_once_with("2025-11-15")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
