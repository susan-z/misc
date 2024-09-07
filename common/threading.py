import threading

class Example:
    self._thread = None
    self._is_active = False
    self._stop_event = None

    def start(self):
        if not self._is_active:
            self._stop_event = threading.Event()
            self._thread = threading.Thread(target=lambda: every(TIME, self.SOMEFUNC, self._stop_event))
            self._thread.start()
            self._is_active = True