"""
Parse CAN database files, get message and signal values, encode and decode CAN messages.
"""
import cantools
import os
import logging

logger = logging.getLogger()

class DbcMessage(Generic):
    """
    Contains all information of a single message and its signals. Supports CAN message encoding and decoding.
    """
    def __init__(self, db_message):
        self._db_message = db_message
        self.signals = self._db_message.signal_tree

        self._initial_message_value = [0]*self.length
        self._initial_signals_values = {}

        self._get_initial_values()

    @property
    def name(self):
        return self._db_message.name

    @property
    def id(self):
        return self._db_message.frame_id

    @property
    def id_hex(self):
        return hex(self._db_message.frame_id)

    @property
    def length(self):
        return self._db_message.length

    @property
    def cycle_time(self):
        return self._db_message.cycle_time

    @property
    def initial_signals_values(self):
        return self._initial_signals_values

    @property
    def initial_message_value(self):
        return self._initial_message_value

    def encode(self, signal_values):
        return [byte for byte in self._db_message.encode(signal_values)]


    def decode(self, message_value):
        return self._db_message.decode(bytearray(message_value))

    def _get_initial_values(self):
        multiplexer = None
        for db_item in self._db_message.signals:
            if db_item.is_multiplexer:
                self._add_initial_signal_value(db_item)
                multiplexer = self._initial_signals_values[db_item.name]
            elif multiplexer == None:
                self._add_initial_signal_value(db_item)

            elif multiplexer != None and db_item.multiplexer_ids != None:
                if db_item.multiplexer_ids[0] == multiplexer:
                    self._add_initial_signal_value(db_item)

        try:
            self._initial_message_value = self.encode(self._initial_signals_values)
        except Exception as e:
            logger.warning(f"Exception caught when encoding {self._initial_signals_values}: {e}")
            self._initial_message_value = None           

    def _add_initial_signal_value(self, db_item):
        if db_item.initial == None:
            self._initial_signals_values[db_item.name] = 0
        else:
            self._initial_signals_values[db_item.name] = db_item.initial


class Dbc(Generic):
    """
    Load .dbc files and store message information within DbcMessage object.
    """
    def __init__(self, dbc_file_name):
        self._dbc_file_path = os.path.join(self._repo_path, dbc_file_name)
        self._db = cantools.database.load_file(self._dbc_file_path)
        self._messages_by_id = {}
        self._messages_by_name = {}

        for db_item in self._db.messages:
            message_obj = DbcMessage(db_item)
            self._messages_by_id[db_item.frame_id] = message_obj
            self._messages_by_name[db_item.name] = message_obj

    def __getitem__(self, key):
        if key in self._messages_by_id:
            return self._messages_by_id[key]
        elif key in self._messages_by_name:
            return self._messages_by_name[key]
        else:
            raise ValueError(f"Unable to find message: {key}")

    @property
    def dbc_file_path(self):
        return self._dbc_file_path

    @property
    def message_count(self):
        return len(self.all_messages)

    @property
    def all_messages(self):
        return self._messages_by_name
