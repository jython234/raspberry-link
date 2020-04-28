from time import sleep
import socket
import threading
import logging


class AudioServiceCommunicator:
    sock = None
    recv_thread = None

    logger = logging.getLogger("AudioServiceCommunicator")

    active_calls = {}

    def __init__(self, socket_file="/run/raspberrylink_audio.socket"):
        self.logger.setLevel(logging.DEBUG)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        retries = 0
        while retries < 5:
            if self._try_connect(socket_file):
                return  # Connection successful
            sleep(3)

        # Connection wasn't successful if we made it here
        raise RuntimeError("Failed to connect to RaspberryLink Audio Socket (perhaps the service isn't running?)")

    def _try_connect(self, socket_file):
        try:
            self.sock.connect(socket_file)
            self.logger.debug("Connected to RaspberryLink Audio socket")

            self.recv_thread = threading.Thread(target=self._process_recv, daemon=True)
            self.recv_thread.start()
            return True
        except FileNotFoundError:
            return False

    def answer_call(self, path):
        self.sock.send(("CALL-ANSWER~" + path).encode("UTF-8"))

    def hangup_call(self, path):
        self.sock.send(("CALL-HANGUP~" + path).encode("UTF-8"))

    def _process_recv(self):
        self.logger.debug("Listening for data from RaspberryLink Audio process")
        while True:
            data = self.sock.recv(512).decode("UTF-8").split("~")

            if data[0] == "CALL-STATE":
                calls = data[1].split("|")
                active_calls = {}
                for call in calls:
                    if call == "":
                        break

                    call_data = call.split("`")
                    active_calls[call_data[3]] = {
                        "modem": call_data[0],
                        "state": call_data[1],
                        "name": call_data[2]
                    }

                self.active_calls = active_calls
            else:
                self.logger.debug("Unknown message from RaspberryLink Audio process " + str(data))
