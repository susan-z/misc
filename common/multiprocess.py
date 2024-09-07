import logging
import time
from multiprocessing import Process, Manager, Event
import multiprocessing as mp

logger = logging.getLogger()

class MqttClientProcess(Process):

    def __init__(self):
        # Maintain shared variables
        super().__init__()
        self.exit = Event()
        self.client = None
        self.mqtt_payloads = Manager().dict({"initial": "test"})

    @staticmethod
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0 and client.is_connected():
            logger.info("Connected!")
            client.subscribe(mqtt_consts.TOPIC)
        else:
            logger.info(f'Failed to connect, return code {rc}')

    @staticmethod
    def on_disconnect(client, userdata, rc):
        logging.info("Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 0, mqtt_consts.FIRST_RECONNECT_DELAY
        while reconnect_count < mqtt_consts.MAX_RECONNECT_COUNT:
            logging.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                logging.info("Reconnected successfully!")
                return
            except Exception as err:
                logging.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= mqtt_consts.RECONNECT_RATE
            reconnect_delay = min(
                reconnect_delay, mqtt_consts.MAX_RECONNECT_DELAY)
            reconnect_count += 1
        logging.info(
            "Reconnect failed after %s attempts. Exiting...", reconnect_count)

    def on_message(self, client, userdata, msg):
        # Place message payload information into shared data structure
        data = msg.payload.decode()
        # Strip everything before the start of the dict
        data = data[data.index('{'):]
        data_dict = json.loads(data)
        for key, val in data_dict.items():
            self.mqtt_payloads[key] = val

    def run(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(mqtt_consts.BROKER, mqtt_consts.PORT)
        self.client.on_disconnect = self.on_disconnect
        self.client.loop_start()
        while not self.exit.is_set():
            time.sleep(1)
        self.client.loop_stop()

    def shutdown(self):
        self.exit.set()


def mqtt_process():
    mp.set_start_method("spawn", force=True)
    process = MqttClientProcess()
    process.start()
    yield process
    process.shutdown()
    process.join()