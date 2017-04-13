
import threading
import queue

try:
    from nmmp.logger import NLogger
except ImportError:
    # This part is only required to run
    # when the module itself is not installed.
    import os, sys
    cmd_subfolder = os.path.abspath(
        os.path.join( os.path.dirname( __file__ ), "../.." ) )
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    from nmmp.logger import NLogger

from nmmp.classinterfaces import NClassesInterface


class NHALExecutor(NClassesInterface):
    """docstring for NHALExecutor"""
    def __init__(self):
        """  """
        super(NHALExecutor, self).__init__()
        #
        self._taskqueue = queue.Queue()
        self.join = self._taskqueue.join
        #
        t = threading.Thread(target=self._worker)
        t.daemon = True
        t.start()

    # NClassesInterface ------------------------------------------------------

    @NLogger.wrap('DEBUG')
    def ex_start_op(self, **kwargs):
        """ """
        kwargs['task'] = 'create'
        self._taskqueue.put( kwargs )

    @NLogger.wrap('DEBUG')
    def ex_transaction_op(self, **kwargs):
        """  """
        kwargs['task'] = 'transaction'
        self._taskqueue.put( kwargs )

    @NLogger.wrap('DEBUG')
    def ex_recive_op(self, **kwargs):
        """ """
        kwargs['task'] = 'read'
        self._taskqueue.put( kwargs )

    def _read_emit(self, frame_id, rxbytes):
        # read operation emit
        self.operation_puthigh_signal.emit(
            'ex_read',
            {
                'frame_id': frame_id,
                'data': rxbytes
            }
        )

    def _timeout_emit(self, name, frame_id):
        # timeout operation emit
        self.operation_puthigh_signal.emit(
            'ex_%s_timeout' % name, { 'frame_id': frame_id }
        )

    def _error_emit(self, task, message):
        self.operation_puthigh_signal.emit(
            'ex_error',
            {
                'task': task,
                'message': message
            }
        )

    # isolated thread methods / worker ---------------------------------------

    @NLogger.wrap('DEBUG')
    def _write(self, frame, frame_id, timeout):
        """  """
        # write and emit succsses signal if all ok
        if self.interface.write(frame, timeout):
            # self._write_emit(frame_id)
            return True
        # else emit timeout
        self._timeout_emit('write', frame_id)
        return False

    @NLogger.wrap('DEBUG')
    def _read(self, frame_id, timeout):
        """   """
        # start read and wait response from slave
        rxbytes = self.interface.read(timeout)
        # emit succsses response signal
        if rxbytes is not None:
            self._read_emit(frame_id, rxbytes)
            return True
        # else timeout
        self._timeout_emit('read', frame_id)
        return False

    @NLogger.wrap('DEBUG')
    def _read_async_slot(self):
        self.ex_recive_op( frame_id=0xAAAAAAAA, timeout_ms=50 )

    @NLogger.wrap('DEBUG')
    def _transaction(self, **kwargs):
        """   """
        # get needed fields
        frame = bytearray( kwargs.get('frame', bytearray()) )
        frame_id = kwargs.get('frame_id', (2**32)-1)
        timeout = kwargs.get('timeout_ms', 0)
        #
        res = self._write(frame, frame_id, timeout)
        if res:
            res = self._read(frame_id, timeout)
        return res

    def _hal_inteface_task(self, **kwargs):
        """ """
        # get task from queue
        task = kwargs.get('task', None)

        # --- manage interface tasks
        if task == 'create':
            # create HAL class instance
            try:
                ihalclass = kwargs.get('hal', None)
                self.interface = ihalclass(**kwargs)
            except Exception as e:
                msgs = ( 'create %s' % str(ihalclass), str(e) )
                self._error_emit(task, msgs)
                return False

            if 'read_async_signal' in dir(self.interface):
                self.interface.read_async_signal.connect(
                    self._read_async_slot
                )

        elif task == 'destroy':
            self.interface = None

        else:
            return False

        return True

    def _hal_command_task(self, **kwargs):
        """ """
        # get task from queue
        task = kwargs.get('task', None)

        if self.interface is None:
            self._error_emit(task, 'interface is None')
        else:
            if not self.interface.open():
                msg = 'interface error: %s' % self.interface.error()
                self._error_emit('open', msg)
            else:
                res = False

                # frame = bytearray( kwargs.get('frame', bytearray()) )
                frame_id = kwargs.get('frame_id', (2**32)-1)
                timeout = kwargs.get('timeout_ms', 0)

                if task == 'transaction':
                    res = self._transaction(**kwargs)

                elif task == 'write':
                    res = self._write(frame_id, timeout)

                elif task == 'read':
                    res = self._read(frame_id, timeout)

                else:
                    self._error_emit(task, 'task not defined')

                if res is False:
                    self._error_emit(
                        task, 'task result state is "False"' )

    def _worker(self):
        """  """
        #
        self.interface = None
        #
        while True:
            # get
            item = self._taskqueue.get()
            #
            with threading.Lock():
                # if hal interface task
                itask = self._hal_inteface_task(**item)
                # else not maby commnd task
                if itask is False:
                    self._hal_command_task(**item)
            #
            self._taskqueue.task_done()
