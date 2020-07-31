import pymel.core as pm
import json
from PySide2 import QtWidgets
from PySide2 import QtCore
from dsWorkspaceToggle import toggleFn


class Dialog(QtWidgets.QDialog):

    WINDOW_TITLE = "Workspace toggle settings"
    OPTION_VAR = "dsWorkspaceToggle"
    DEFAULTS = {"workspaces": [],
                "hotkey": {"key": "w",
                           "shift": False,
                           "ctl": True,
                           "alt": False}
                }
    dialog_instance = None

    @classmethod
    def display(cls):
        if not cls.dialog_instance:
            cls.dialog_instance = Dialog()
        if cls.dialog_instance.isHidden():
            cls.dialog_instance.show()
        else:
            cls.dialog_instance.raise_()
            cls.dialog_instance.activateWindow()

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(400, 300)
        if pm.about(ntOS=1):
            self.setWindowFlags(self.windowFlags ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif pm.about(macOS=1):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.geometry = None

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    # Events
    def closeEvent(self, event):
        if isinstance(self, Dialog):
            super(Dialog, self).closeEvent(event)
            self.geometry = self.saveGeometry()

    def showEvent(self, event):
        super(Dialog, self).showEvent(event)
        if self.geometry:
            self.restoreGeometry(self.geometry)
        self.load_options()

    def create_widgets(self):
        self.all_workspaces = AllWorkspacesWidget()
        self.active_workspaces = ActiveWorkspacesWidget()
        self.splitter_lists = QtWidgets.QSplitter()
        self.splitter_lists.setHandleWidth(40)

        self.splitter_add_btn = QtWidgets.QPushButton()
        self.splitter_add_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.splitter_remove_btn = QtWidgets.QPushButton()
        self.splitter_remove_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_LineEditClearButton))
        self.splitter_lists.addWidget(self.all_workspaces)
        self.splitter_lists.addWidget(self.active_workspaces)

        self.hotkey_grp = QtWidgets.QGroupBox("Hotkey")
        self.hotkey_field = QtWidgets.QLineEdit()
        self.hotkey_set_btn = QtWidgets.QPushButton("Set...")
        self.hotkey_ctl_checkbox = QtWidgets.QCheckBox("Ctl")
        self.hotkey_alt_checkbox = QtWidgets.QCheckBox("Atl")
        self.hotkey_shift_checkbox = QtWidgets.QCheckBox("Shift")

        self.save_btn = QtWidgets.QPushButton("Save")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

    def create_layouts(self):
        self.splitter_bnt_layout = QtWidgets.QVBoxLayout()
        self.splitter_bnt_layout.addWidget(self.splitter_add_btn)
        self.splitter_bnt_layout.addWidget(self.splitter_remove_btn)
        self.splitter_lists.handle(1).setLayout(self.splitter_bnt_layout)
        self.splitter_lists.setStyleSheet("QSplitter::handle { image: none; }")

        self.hotkey_layout = QtWidgets.QHBoxLayout()
        self.hotkey_grp.setLayout(self.hotkey_layout)
        self.hotkey_layout.addWidget(self.hotkey_field)
        self.hotkey_layout.addWidget(self.hotkey_ctl_checkbox)
        self.hotkey_layout.addWidget(self.hotkey_alt_checkbox)
        self.hotkey_layout.addWidget(self.hotkey_shift_checkbox)
        self.hotkey_layout.addStretch()

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.save_btn)
        self.buttons_layout.addWidget(self.cancel_btn)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.hotkey_grp)
        self.main_layout.addWidget(self.splitter_lists)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.buttons_layout)
        self.setLayout(self.main_layout)

    def create_connections(self):
        # Hotkey
        self.hotkey_field.textChanged.connect(self.check_hotkey_existance)
        self.hotkey_field.textChanged.connect(self.make_lowercase)
        self.hotkey_field.textChanged.connect(self.update_save_button)
        self.hotkey_ctl_checkbox.toggled.connect(self.check_hotkey_existance)
        self.hotkey_alt_checkbox.toggled.connect(self.check_hotkey_existance)
        self.hotkey_shift_checkbox.toggled.connect(self.check_hotkey_existance)

        # Splitter buttons
        self.splitter_add_btn.clicked.connect(self.add_to_toggle_list)
        self.splitter_remove_btn.clicked.connect(self.remove_from_toggle_list)

        # Buttons
        self.save_btn.clicked.connect(self.save_options)
        self.cancel_btn.clicked.connect(self.close)

    def load_options(self):
        options = pm.optionVar.get(self.OPTION_VAR, default=self.DEFAULTS)
        if isinstance(options, basestring):
            options = json.loads(options)

        # Hotkey
        hotkey = options.get("hotkey")  # type:dict
        self.hotkey_field.setText(hotkey.get("key"))
        self.hotkey_ctl_checkbox.setChecked(hotkey.get("ctl"))
        self.hotkey_alt_checkbox.setChecked(hotkey.get("alt"))
        self.hotkey_shift_checkbox.setChecked(hotkey.get("shift"))

        # Workspaces
        self.active_workspaces.list.clear()
        for workspace_name in options.get("workspaces"):
            active_item = QtWidgets.QListWidgetItem()
            active_item.setData(0, workspace_name)
            self.active_workspaces.list.addItem(active_item)

    def save_options(self):
        # Option var
        workspaces = []
        hotkey = {"key": self.hotkey_field.text(),
                  "ctl": self.hotkey_ctl_checkbox.isChecked(),
                  "alt": self.hotkey_alt_checkbox.isChecked(),
                  "shift": self.hotkey_shift_checkbox.isChecked()}

        for index in range(self.active_workspaces.list.count()):
            workspaces.append(self.active_workspaces.list.item(index).data(0))
        options = {"workspaces": workspaces,
                   "hotkey": hotkey}
        pm.optionVar[self.OPTION_VAR] = json.dumps(options)

        # Setup hotkey
        self.save_hotkey()
        self.close()

    def add_to_toggle_list(self):
        for item in self.all_workspaces.list.selectedItems():
            active_item = QtWidgets.QListWidgetItem()
            active_item.setData(0, item.data(0))
            self.active_workspaces.list.addItem(active_item)

    def remove_from_toggle_list(self):
        for item in self.active_workspaces.list.selectedItems():
            self.active_workspaces.list.takeItem(self.active_workspaces.list.row(item))

    def check_hotkey_existance(self, text):
        key = self.hotkey_field.text()
        if not key:
            return

        # !No shift check avalailabe?
        conflict_key = pm.hotkeyCheck(k=key, ctl=self.hotkey_ctl_checkbox.isChecked(), alt=self.hotkey_alt_checkbox.isChecked())
        if conflict_key:
            self.hotkey_field.setToolTip(conflict_key)
            self.hotkey_field.setStyleSheet("background:#DC143C;")
        else:
            self.hotkey_field.setToolTip("Hotkey available")
            self.hotkey_field.setStyleSheet("background:##484848;")

    def update_save_button(self, text):
        self.save_btn.setEnabled(bool(text.strip()))

    def make_lowercase(self, text):
        self.hotkey_field.setText(text.lower())

    def save_hotkey(self):
        namedCommand = pm.nameCommand("dsToggle_workspaces",
                                      ann="Toggle favorited workspaces",
                                      command='python("dsWorkspaceToggle.toggleFn.toggleWorkspace()")',
                                      stp="mel")
        # toggleFn.delete_old_hotkey(namedCommand) # ?Doesn't seem to work as Maya overrides mel file on exit
        hotkey = pm.hotkey(k=self.hotkey_field.text(),
                           ctl=self.hotkey_ctl_checkbox.isChecked(),
                           alt=self.hotkey_alt_checkbox.isChecked(),
                           sht=self.hotkey_shift_checkbox.isChecked(),
                           name=namedCommand)


class AllWorkspacesWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AllWorkspacesWidget, self).__init__(parent)
        self.label = QtWidgets.QLabel("All workspaces:")
        self.list = QtWidgets.QListWidget()
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.refresh_btn = QtWidgets.QPushButton("Refresh")

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.list)
        self.main_layout.addWidget(self.refresh_btn)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.refresh_btn.clicked.connect(self.update_available_workspaces)

    def update_available_workspaces(self):
        self.list.clear()
        for ws in pm.workspaceLayoutManager(ll=1):
            item = QtWidgets.QListWidgetItem()
            item.setData(0, ws)
            self.list.addItem(item)

    def showEvent(self, event):
        super(AllWorkspacesWidget, self).showEvent(event)
        self.update_available_workspaces()


class ActiveWorkspacesWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(ActiveWorkspacesWidget, self).__init__(parent)
        self.label = QtWidgets.QLabel("Toggle list:")
        self.list = QtWidgets.QListWidget()
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.list)
        self.main_layout.setContentsMargins(0, 0, 0, 0)


if __name__ == "__main__":
    try:
        workspace_dialog.close()  # noqa: F821
        workspace_dialog.deleteLater()  # noqa: F821
    except BaseException:
        pass

    workspace_dialog = Dialog()
    workspace_dialog.show()
