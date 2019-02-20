import numpy as np
import pyqtgraph
from quamash import QtWidgets, QtCore

from .model import SinglePointModel
from .utils import extract_scalar_channels, setup_axis_item, SERIES_COLORS


class _Series:
    def __init__(self, plot, data_name, data_item, error_bar_name, error_bar_item,
                 history_length):
        self.plot = plot
        self.data_item = data_item
        self.data_name = data_name
        self.error_bar_item = error_bar_item
        self.error_bar_name = error_bar_name

        self.values = np.array([]).reshape((0, 2))
        self.set_history_length(history_length)

    def append(self, data):
        new_data = data[self.data_name]
        if self.error_bar_item:
            new_error_bar = data[self.error_bar_name]

        p = [new_data, 2 * new_error_bar] if self.error_bar_item else [new_data]

        is_first = (self.values.shape[0] == 0)
        if is_first:
            self.values = np.array([p])
        else:
            if self.values.shape[0] == len(self.x_indices):
                self.values = np.roll(self.values, -1, axis=0)
                self.values[-1, :] = p
            else:
                self.values = np.vstack((self.values, p))

        num_to_show = self.values.shape[0]
        self.data_item.setData(self.x_indices[-num_to_show:], self.values[:, 0].T)
        if self.error_bar_item:
            self.error_bar_item.setData(
                x=self.x_indices[-num_to_show:],
                y=self.values[:, 0].T,
                height=self.values[:, 1].T)

        if is_first:
            self.plot.addItem(self.data_item)
            if self.error_bar_item:
                self.plot.addItem(self.error_bar_item)

    def remove_items(self):
        if self.values.shape[0] == 0:
            return
        self.plot.removeItem(self.data_item)
        if self.error_bar_item:
            self.plot.removeItem(self.error_bar_item)

    def set_history_length(self, n):
        assert n > 0, "Invalid history length"
        self.x_indices = np.arange(-n, 0)
        if self.values.shape[0] > n:
            self.values = self.values[-n:, :]


class Rolling1DPlotWidget(pyqtgraph.PlotWidget):
    error = QtCore.pyqtSignal(str)
    ready = QtCore.pyqtSignal()

    def __init__(self, model: SinglePointModel):
        super().__init__()

        self.model = model
        self.model.channel_schemata_changed.connect(self._initialise_series)
        self.model.point_changed.connect(self._append_point)

        self.series = []
        self.num_history_box = None

        self.showGrid(x=True, y=True)

        self._install_context_menu()

    def _initialise_series(self):
        for s in self.series:
            s.remove_items()
        self.series.clear()

        channels = self.model.get_channel_schemata()
        try:
            data_names, error_bar_names = extract_scalar_channels(channels)
        except ValueError as e:
            self.error.emit(str(e))
            return

        colors = [SERIES_COLORS[i % len(SERIES_COLORS)] for i in range(len(data_names))]
        for i, (data_name, color) in enumerate(zip(data_names, colors)):
            data_item = pyqtgraph.ScatterPlotItem(pen=None, brush=color)

            error_bar_name = error_bar_names.get(data_name, None)
            error_bar_item = pyqtgraph.ErrorBarItem(
                pen=color) if error_bar_name else None

            history_length = 1024
            if self.num_history_box:
                history_length = self.num_history_box.value()
            self.series.append(
                _Series(self, data_name, data_item, error_bar_name, error_bar_item,
                        history_length))

        def axis_info(i):
            # If there is only one series, set label/scaling accordingly.
            # TODO: Add multiple y axis for additional channels.
            c = channels[data_names[i]]
            label = c["description"]
            if not label:
                label = c["path"].split("/")[-1]
            return label, c["path"], colors[i], c

        setup_axis_item(
            self.getAxis("left"), [axis_info(i) for i in range(len(data_names))])

        self.ready.emit()

    def _append_point(self, point):
        for s in self.series:
            s.append(point)

    def set_history_length(self, n):
        for s in self.series:
            s.set_history_length(n)

    def _install_context_menu(self):
        if not self.model.context.is_online_master():
            # If no new data points are coming in, setting the history size wouldn't do
            # anything.
            # TODO: is_online_master() should really be something like
            # SinglePointModel.ever_updates().
            return
        self.num_history_box = QtWidgets.QSpinBox()
        self.num_history_box.setMinimum(1)
        self.num_history_box.setMaximum(2**16)
        self.num_history_box.setValue(100)
        self.num_history_box.valueChanged.connect(self.set_history_length)

        container = QtWidgets.QWidget()

        layout = QtWidgets.QHBoxLayout()
        container.setLayout(layout)

        label = QtWidgets.QLabel("N: ")
        layout.addWidget(label)

        layout.addWidget(self.num_history_box)

        action = QtWidgets.QWidgetAction(self)
        action.setDefaultWidget(container)

        separator = QtWidgets.QAction("", self)
        separator.setSeparator(True)
        entries = [action, separator]
        self.plotItem.getContextMenus = lambda ev: entries
