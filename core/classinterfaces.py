# python3!

from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QVariant


# -----------------------------------------------------------------------------


class NClassesInterface(QObject):
    """docstring for NClassesInterface"""

    operation_puthigh_signal = pyqtSignal(str, QVariant)
    operation_putlow_signal = pyqtSignal(str, QVariant)

    # def __init__(self, parent=None):
    #     """ """
    #     super(NClassesInterface, self).__init__(parent)

    @staticmethod
    def connect(objects, singals_type):
        """"""
        if singals_type not in Qt.__dict__:
            return False

        i = 0
        while i < len(objects) - 1:
            #
            obj = objects[i]
            obj_next = objects[i+1]
            # --- connect obj signal to obj_next slot
            obj.operation_putlow_signal.connect(
                obj_next.operation_in_high_slot,
                type = Qt.__dict__[singals_type]
            )
            # --- connect obj_next signal to obj slot
            obj_next.operation_puthigh_signal.connect(
                obj.operation_in_low_slot,
                type = Qt.__dict__[singals_type]
            )
            i += 1

        return True

    def _operation_parse(self, opname, kwargs):
        """ """
        opname = '%s_op' % opname
        if opname in self.__dir__():
            method = getattr(self, opname)
            method( **kwargs )

    @pyqtSlot(str, QVariant)
    def operation_in_high_slot(self, opname, kwargs):
        """ """
        self._operation_parse(opname, kwargs)

    @pyqtSlot(str, QVariant)
    def operation_in_low_slot(self, opname, kwargs):
        """ """
        self._operation_parse(opname, kwargs)
