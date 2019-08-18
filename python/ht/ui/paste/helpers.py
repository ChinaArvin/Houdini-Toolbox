"""Custom source helper widgets for copying/pasting sources."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Third Party Imports
from PySide2 import QtCore, QtWidgets

# Houdini Toolbox Imports
from ht.ui.paste import widgets


# ==============================================================================
# CLASSES
# ==============================================================================

class _BaseCopyHelperWidget(QtWidgets.QWidget):
    """A default widget for additional copy related options."""

    def __init__(self, source, context, parent=None):
        super(_BaseCopyHelperWidget, self).__init__(parent)

        self.context = context
        self.source = source

    def get_source(self):
        """Get the source item."""
        pass


class _BasePasteHelperWidget(QtWidgets.QWidget):
    """A default widget for additional paste related options."""

    def __init__(self, source, context, parent=None):
        super(_BasePasteHelperWidget, self).__init__(parent)

        self.context = context
        self.source = source

    def get_sources(self):
        """Get sources."""
        pass


class HomeToolDirItemsCopyHelperWidget(_BaseCopyHelperWidget):
    """Widget for copying items to the ~/tooldev folder."""

    valid_source_signal = QtCore.Signal(bool)

    def __init__(self, source, context, parent=None):
        super(HomeToolDirItemsCopyHelperWidget, self).__init__(source, context, parent)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.new_or_existing = widgets.NewOrExistingWidget()
        layout.addWidget(self.new_or_existing)

        invalid_names = [item.name for item in source.get_sources(context)]

        self.name_widget = widgets.CopyItemNameWidget(invalid_names=invalid_names)
        layout.addWidget(self.name_widget)

        self.table = widgets.BasicSourceItemTable(source, context)
        layout.addWidget(self.table)

        self.new_or_existing.currentIndexChanged.connect(self._mode_changed)

        self._mode_changed(0)

        self.name_widget.valid_source_signal.connect(self.valid_source_signal.emit)
        self.table.valid_sources_signal.connect(self.valid_source_signal.emit)

    def _mode_changed(self, index):
        """Handle the NewOrExisting widget being changed."""
        if index == 0:
            self.table.setEnabled(False)
            self.table.clearSelection()
            self.name_widget.setEnabled(True)
            self.name_widget.validate_name()

        else:
            self.table.setEnabled(True)
            self.name_widget.setEnabled(False)

            self.valid_source_signal.emit(False)

    def get_source(self):
        """Get the selected source."""
        mode = self.new_or_existing.currentIndex()

        if mode == 0:
            name = self.name_widget.name.text()

            description = self.name_widget.description.text()
            if not description:
                description = None

            return self.source.create_source(self.context, name, description)

        else:
            sources = self.table.get_selected_sources()

            return sources[0]


class HomeToolDirItemsPasteHelperWidget(_BasePasteHelperWidget):
    """Widget for pasting items from the ~/tooldev folder."""

    perform_operation_signal = QtCore.Signal()
    valid_sources_signal = QtCore.Signal(bool)

    def __init__(self, source, context, parent=None):
        super(HomeToolDirItemsPasteHelperWidget, self).__init__(source, context, parent)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # We want to be able to multi-select, delete and double click on items.
        self.table = widgets.BasicSourceItemTable(
            source,
            context,
            selection_mode=QtWidgets.QAbstractItemView.ExtendedSelection,
            allow_delete=True,
            allow_double_click=True
        )
        layout.addWidget(self.table)

        self.table.perform_operation_signal.connect(self.perform_operation_signal.emit)
        self.table.valid_sources_signal.connect(self.valid_sources_signal.emit)

    def get_sources(self):
        """Get a list of selected sources to operate on."""
        return self.table.get_selected_sources()

