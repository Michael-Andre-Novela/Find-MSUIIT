"""Activity log view widget."""

from typing import Optional, List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QPushButton, QTextEdit


class ActivityLogView(QWidget):
	def __init__(self, parent: Optional[QWidget] = None):
		super().__init__(parent)

		# 1. Main vertical backbone
		self.main_layout = QVBoxLayout(self)
		self.main_layout.setContentsMargins(20, 20, 20, 20)
		self.main_layout.setSpacing(15)

		# 2. Header
		header_layout = QHBoxLayout()

		self.lbl_title = QLabel("System Activity Log", self)
		self.lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1A1A1A;")

		self.btn_refresh = QPushButton("Refresh Logs", self)
		self.btn_refresh.setObjectName("refreshButton")

		header_layout.addWidget(self.lbl_title)
		header_layout.addStretch()
		header_layout.addWidget(self.btn_refresh)

		self.main_layout.addLayout(header_layout)

		# 3. Filter controls
		filter_layout = QHBoxLayout()
		filter_layout.setSpacing(8)

		self.lbl_filter = QLabel("Filter by Type:", self)
		self.lbl_filter.setStyleSheet("font-size: 13px; color: #555555;")

		self.combo_filter = QComboBox(self)
		self.combo_filter.addItems([
			"All Activity",
			"Items Registration",
			"Claims Processed",
			"System Alerts",
		])
		self.combo_filter.setFixedWidth(180)

		filter_layout.addWidget(self.lbl_filter)
		filter_layout.addWidget(self.combo_filter)
		filter_layout.addStretch()

		self.main_layout.addLayout(filter_layout)

		# 4. Large monitor layout block
		self.log_display = QTextEdit(self)
		self.log_display.setReadOnly(True)
		self.log_display.setPlaceholderText("Retrieving historical application timeline sequences...")
		self.log_display.setStyleSheet("font-family: 'Courier New', monospace; font-size: 12px; color: #1A1A1A;")

		self.main_layout.addWidget(self.log_display)

	# =========================================================================
	# PUBLIC INTERFACE METHODS (The channels that Presenter uses to control the UI)
	# =========================================================================

	def show_logs(self, log_entries: List[str]) -> None:
		"""Flushes the central area and appends raw timeline text strings."""
		self.log_display.clear()

		if not log_entries:
			self.log_display.setPlaceholderText("No system log records match the current criteria filter.")
			return
		for entry in log_entries:
			self.log_display.append(entry)

