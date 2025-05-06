import ctypes
from threading import Lock

class ParallelPort:
    def __init__(self, address: str, thread_lock: Lock = None) -> None:
        """
        Class to initialize and set up parallel port communication
        """
        # Load parallel comunication DLLs
        try:
            self.pport = ctypes.WinDLL("inpoutx64.dll")  # 64-bit version
        except:
            self.pport = ctypes.WinDLL("inpout32.dll")  # 32-bit version

        # Set up a lock for thread safe communication
        if thread_lock is not None:
            self.thread_lock = thread_lock
        else:
            self.thread_lock = Lock()

        # Address (hex to dec)
        self.lpt = int(address, 16)

        # Initialize the state of pins
        try:
            data_register = self.pport.Inp32(self.lpt)
            self.pstate = list(f'{data_register:08b}')
        except:
            self.pstate = ['0'] * 8

    def set_data_high(self, pin: int):
        with self.thread_lock:
            self.pstate[7-pin] = '1'
            self.pport.Out32(self.lpt, int(''.join(self.pstate), 2))

    def set_data_low(self, pin: int):
        with self.thread_lock:
            self.pstate[7-pin] = '0'
            self.pport.Out32(self.lpt, int(''.join(self.pstate), 2))

    def get_data(self, pin: int) -> int:
        with self.thread_lock:
            return int(self.pstate[pin])

    def get_status(self):
        with self.thread_lock:
            return self.pport.Inp32(self.lpt + 1)
