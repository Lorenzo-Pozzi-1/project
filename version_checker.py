"""
Version checking module for the Pesticide App.

This module handles checking for new versions from SharePoint and notifying users.
"""

import requests
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QThread, Signal
from common import get_medium_font

# App version - update this for each release
APP_VERSION = "0.1.0"

# SharePoint URL for version file - update this with your actual SharePoint direct link
VERSION_URL = "link to sharepoint here"

class VersionChecker(QThread):
    """Background thread to check for version updates."""
    
    version_checked = Signal(str, str)  # Signal: (remote_version, download_url)
    check_failed = Signal(str)  # Signal: error_message
    
    def __init__(self, version_url=VERSION_URL):
        super().__init__()
        self.version_url = version_url
        
    def run(self):
        """Check for new version in background thread."""
        try:
            # Timeout after 5 seconds to avoid hanging
            response = requests.get(self.version_url, timeout=5)
            response.raise_for_status()
            
            # Parse response - expect format like "0.2.0|https://sharepoint.com/download/link"
            content = response.text.strip()
            if '|' in content:
                remote_version, download_url = content.split('|', 1)
            else:
                # Fallback: just version number, no download link
                remote_version = content
                download_url = ""
                
            self.version_checked.emit(remote_version.strip(), download_url.strip())
            
        except requests.RequestException as e:
            self.check_failed.emit(f"Network error: {str(e)}")
        except Exception as e:
            self.check_failed.emit(f"Unexpected error: {str(e)}")

def compare_versions(current, remote):
    """Compare version strings. Returns True if remote is newer."""
    try:
        # Simple version comparison for x.y.z format
        current_parts = [int(x) for x in current.split('.')]
        remote_parts = [int(x) for x in remote.split('.')]
        
        # Pad shorter version with zeros
        max_length = max(len(current_parts), len(remote_parts))
        current_parts.extend([0] * (max_length - len(current_parts)))
        remote_parts.extend([0] * (max_length - len(remote_parts)))
        
        return remote_parts > current_parts
    except ValueError:
        # If version parsing fails, assume no update needed
        return False

def show_update_dialog(parent, remote_version, download_url=""):
    """Show dialog notifying user of available update."""
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle("Update Available")
    
    if download_url:
        msg_box.setText(f"Version {remote_version} is available!\n\nClick 'Download' to get the latest version.")
        msg_box.setInformativeText("Your current version will continue to work.")
        
        download_button = msg_box.addButton("Download", QMessageBox.AcceptRole)
        later_button = msg_box.addButton("Later", QMessageBox.RejectRole)
        
        msg_box.setDefaultButton(download_button)
    else:
        msg_box.setText(f"Version {remote_version} is available!\n\nCheck SharePoint for the latest version.")
        msg_box.addButton("OK", QMessageBox.AcceptRole)
    
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setFont(get_medium_font())
    
    result = msg_box.exec()
    
    # If download button was clicked and we have a URL
    if download_url and msg_box.clickedButton().text() == "Download":
        import webbrowser
        webbrowser.open(download_url)

class VersionManager:
    """Manages version checking for the application."""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.checker = None
        
        # Signals to update UI
        from PySide6.QtCore import QObject, Signal
        
        class SignalEmitter(QObject):
            checker_created = Signal()
            version_result = Signal(bool, str)  # has_update, remote_version
            check_error = Signal(str)  # error_message
        
        self.signals = SignalEmitter()
        
    @property
    def checker_created(self):
        return self.signals.checker_created
        
    @property 
    def version_result(self):
        return self.signals.version_result
        
    @property
    def check_error(self):
        return self.signals.check_error
        
    def check_for_updates(self, silent=False):
        """
        Check for updates.
        
        Args:
            silent: If True, don't show dialogs for errors or "no updates"
        """
        if self.checker and self.checker.isRunning():
            return  # Already checking
            
        self.signals.checker_created.emit()
        
        self.checker = VersionChecker()
        self.checker.version_checked.connect(
            lambda remote_ver, download_url: self._handle_version_result(remote_ver, download_url, silent)
        )
        self.checker.check_failed.connect(
            lambda error: self._handle_check_failed(error, silent)
        )
        self.checker.start()
        
    def _handle_version_result(self, remote_version, download_url, silent):
        """Handle successful version check result."""
        has_update = compare_versions(APP_VERSION, remote_version)
        self.signals.version_result.emit(has_update, remote_version)
        
        if has_update:
            # New version available
            show_update_dialog(self.parent, remote_version, download_url)
        elif not silent:
            # No update needed - only show if not silent
            self._show_no_update_dialog()
            
    def _handle_check_failed(self, error_message, silent):
        """Handle failed version check."""
        self.signals.check_error.emit(error_message)
        
        if not silent:
            msg_box = QMessageBox(self.parent)
            msg_box.setWindowTitle("Update Check Failed")
            msg_box.setText("Could not check for updates.")
            msg_box.setInformativeText(error_message)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setFont(get_medium_font())
            msg_box.exec()
            
    def _show_no_update_dialog(self):
        """Show dialog when no update is available."""
        msg_box = QMessageBox(self.parent)
        msg_box.setWindowTitle("No Updates")
        msg_box.setText(f"You have the latest version ({APP_VERSION}).")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setFont(get_medium_font())
        msg_box.exec()