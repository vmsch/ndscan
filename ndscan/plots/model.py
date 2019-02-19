from typing import Any, Callable, Dict, Union
from quamash import QtCore


class Context(QtCore.QObject):
    title_changed = QtCore.pyqtSignal(str)

    def __init__(self, set_dataset: Callable[[str, Any], None] = None):
        super().__init__()
        self.set_dataset = set_dataset
        self.title = ""

    def set_title(self, title: str) -> None:
        if title != self.title:
            self.title = title
            self.title_changed.emit(title)

    def is_online_master(self) -> bool:
        return self.set_dataset is not None

    def set_dataset(self, key: str, value: Any) -> None:
        self.set_dataset(key, value)


class ContinuousScanModel(QtCore.QObject):
    channel_schemata_changed = QtCore.pyqtSignal(dict)
    new_point_complete = QtCore.pyqtSignal(dict)

    def __init__(self, context: Context):
        super().__init__()
        self.context = context

    def get_channel_schemata(self) -> Dict[str, Any]:
        raise NotImplementedError

    def get_current_point(self) -> Dict[str, Any]:
        raise NotImplementedError


class DimensionalScanModel(QtCore.QObject):
    channel_schemata_changed = QtCore.pyqtSignal(dict)
    points_rewritten = QtCore.pyqtSignal(dict)
    points_appended = QtCore.pyqtSignal(dict)

    def __init__(self, axes: list, context: Context):
        super().__init__()
        self.axes = axes
        self.context = context

    def get_channel_schemata(self) -> Dict[str, Any]:
        raise NotImplementedError

    def get_points(self) -> Dict[str, Any]:
        raise NotImplementedError


class Root(QtCore.QObject):
    model_changed = QtCore.pyqtSignal()

    def get_model(self) -> Union[ContinuousScanModel, DimensionalScanModel]:
        raise NotImplementedError