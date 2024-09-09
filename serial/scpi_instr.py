"""
SCPI commands, constructs commands with a property-like format.
"""

class ScpiInstrument:
    def __init__(self, resource):
        self._res = resource

    def __getattr__(self, attribute):
        """Invoked whenever an attribute that hasn't already been defined is requested"""
        resp = ScpiCommandConstr(self, attribute)
        return resp

    def send(self, command):
        """ Sends a command with Carriage Return and Line Feed"""
        self._res.write(command)

    def send_and_receive(self, command):
        """Sends command and receives the answer"""
        return self._res.query(command)

    def close_comms(self):
        """Close communication with the instrument"""
        if hasattr(self, '_res'):
            self._res.close()

    # Standard SCPI commands
    def get_info(self):
        """Identify instrument"""
        cmd = "*IDN?"
        return self.send_and_receive(cmd)

    def clear_status(self):
        """Clears instrument status and errors"""
        cmd = "*CLS"
        return self.send(cmd)

    def reset(self):
        """Resets the instrument to the Factory configuration"""
        cmd = "*RST"
        return self.send(cmd)

    def get_errors(self):
        """Reads and clears one error from the error queue"""
        cmd = "SYST:ERR?"
        return self.send_and_receive(cmd)

    def set_remote_mode(self):
        """Place the instrument in remote mode"""
        cmd = "SYST:REM"
        self.send(cmd)

    def set_local_mode(self):
        """Place the instrument in local mode"""
        cmd = "SYST:LOC"
        self.send(cmd)


class ScpiCommandConstr:
    """Transforms requested attributes into SCPI commands"""

    def __init__(self, instrument: ScpiInstrument, command):
        self._inst = instrument
        self.args = command.upper()

    def __getattr__(self, command):
        """Called when an attribute that hasn't already been defined is requested"""
        return ScpiCommandConstr(
            self._inst,
            ':'.join((self.args, command.upper()))
        )

    def __call__(self, value=None):
        """Instance of command is called as a function"""
        if value is not None and '?' in str(value):
            # Send as raw
            return self._inst.send_and_receive(f'{self.args}{value}')
        elif value is not None:
            cmd = f'{self.args} {value}'
            self._inst.send(cmd)
        else:
            # No arg, just send a query
            return self._inst.send_and_receive(f'{self.args}?')
