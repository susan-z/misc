"""
Wrapper for modbus_tk python package.
"""

# Third-party modules
from modbus_tk.defines import (
    READ_HOLDING_REGISTERS,
    READ_COILS,
    WRITE_SINGLE_REGISTER,
    WRITE_SINGLE_COIL,
    WRITE_MULTIPLE_REGISTERS
)
from modbus_tk.exceptions import ModbusInvalidResponseError
from modbus_tk.modbus_rtu import RtuMaster
from modbus_tk import hooks
from serial import Serial


class ModbusWrapper:
    def __init__(self, port: str, baudrate: int):
        self._serial = Serial(port, baudrate)
        self._address = 1
        self._master = RtuMaster(self._serial)
        self._timeout = 0.5
        self._master.set_timeout(self._timeout)

    def read_register(self, register: int, length: int = 1, data_format="", data_type="", returns_raw=False) -> int or str or tuple:
        """Read register"""
        try:
            # Modify the data format to the appropriate type
            if data_type == "c":
                data_format = ">" + (length * 2 * "c")
            if data_type == "f":
                data_format = ">" + (length // 2 * "f")
            response = self._master.execute(
                self._address, READ_HOLDING_REGISTERS, register, length, data_format=data_format, returns_raw=returns_raw
            )
            if data_type == "c":
                # Concatenate bytes and remove null bytes
                filtered_response_string = b''.join(
                    response).replace(b'\x00', b'')
                # Convert to string
                response = filtered_response_string.decode('utf-8')
            return response if (length > 1 and data_type != "f") else response[0]
        except ModbusInvalidResponseError:
            self.close()
            raise ValueError(
                f"Unable to read register : {register} with length: {length}")

    def read_coil(self, register: int, length: int = 1, returns_raw=False) -> int or tuple:
        """Read coil"""
        try:
            response = self._master.execute(
                self._address, READ_COILS, register, length, returns_raw=returns_raw
            )
            return response if length > 1 else response[0]
        except ModbusInvalidResponseError:
            self.close()
            raise ValueError(
                f"Unable to read register : {register} with length: {length}")

    def write_single_register(self, register: int, value: int, returns_raw=False) -> int:
        """Write register"""
        try:
            return self._master.execute(
                self._address, WRITE_SINGLE_REGISTER, register, 1, value, returns_raw=returns_raw
            )[0]
        except ModbusInvalidResponseError:
            self.close()
            raise ValueError(
                f"Unable to write register : {register} with value: {value}")

    def write_coil(self, register: int, value: int, returns_raw=False) -> int:
        """Write coil"""
        try:
            return self._master.execute(
                self._address, WRITE_SINGLE_COIL, register, 1, value, returns_raw=returns_raw
            )[0]
        except ModbusInvalidResponseError:
            self.close()
            raise ValueError(
                f"Unable to write single coil : {register} with value: {value}")

    def write_multiple_registers(self, register: int, values: tuple or list, length=1, returns_raw=False) -> tuple:
        """Write multiple registers"""
        try:
            return self._master.execute(
                self._address, WRITE_MULTIPLE_REGISTERS, register, length, output_value=values, returns_raw=returns_raw
            )[0]
        except ModbusInvalidResponseError:
            self.close()
            raise ValueError(
                f"Unable to write register : {register} with value: {values}")

    def install_hooks(self):
        hooks.install_hook(
            "modbus_rtu.RtuMaster.before_send", lambda self: self._do_open()
        )
        hooks.install_hook(
            "modbus_rtu.RtuMaster.after_recv", lambda self: self._do_close()
        )

    def close(self):
        """Close communication with the power supply instrument"""
        if self._serial != None:
            self._serial.close()
