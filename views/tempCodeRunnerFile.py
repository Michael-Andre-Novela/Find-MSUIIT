def _build_sidebar_layout(self) -> None:
        """Assembles the internal vertical menu layout inside the sidebar."""
        sidebar_layout = QVBoxLayout(self._sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(4)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        brand_label = QLabel("Find-MSUIIT", self._sidebar)
        brand_label.setObjectName("brandLabel")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(brand_label)
        sidebar_layout.addSpacing(15)

        self._add_sidebar_action(sidebar_layout, "dashboard", "📊  Dashboard")
        self._add_sidebar_action(sidebar_layout, "items", "📦  Items")
        self._add_sidebar_action(sidebar_layout, "claims", "🗂️  Manage Claims")
        self._add_sidebar_action(sidebar_layout, "report", "📝  Report Item")
        self._add_sidebar_action(sidebar_layout, "constituents", "👥  Constituents")
        self._add_sidebar_action(sidebar_layout, "activity", "📜  Activity Log")
        self._add_sidebar_action(sidebar_layout, "maintenance", "🛠️  Maintenance")

        vertical_spacer = QSpacerItem(20, 40, Q