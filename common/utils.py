import git
import logging
import paramiko
import os
import socket
import subprocess
import time
from datetime import datetime

logger = logging.getLogger()

class ConstDefaults:
    # Read-only constants
    __slots__ = ()
    EXAMPLE_VAR = 5

class AttrDict(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def update(self, entries):
        for key, value in entries.items():
            setattr(self, key, value)


class Validate():
    """Validate class contains methods that test and return bool True or False"""
    def within_percent_tolerance(expected, actual, percent_tolerance):
        """ Determine if change is within percent tolerance threshold. Returns true if within acceptable range """
        percent_change = abs(((actual - expected) / expected) * 100)
        return True if percent_change <= percent_tolerance else False


class Check():
    """Check class contains methods that test and raise an exception if not met"""
    def in_list(value, values: list):
        """Check if a given value is contained in list. If not, raise a ValueError exception"""
        if value not in values:
            raise ValueError(
                f'Invalid value: {value}. Valid values: {values}')

    def in_range(value, start: int, stop: int, step: int = 1):
        """Check if a given value is in range. If not, raise a ValueError exception"""
        if value not in range(start, stop, step):
            raise ValueError(
                f'Invalid value: {value}. Not in range: ({start}, {stop}) with steps of {step}')


def get_repo_path():
    """Returns absolute path"""
    return os.path.abspath(os.path.join(__file__, "../../../../../"))


def get_timestamp() -> str:
    """Get formatted time and date"""
    now = datetime.now()
    timestamp = str(now.strftime("%Y%m%d%H%M%S"))
    return timestamp


def execute_command(command, cwd_path):
    """Subprocess to run command-line calls and capture output. Raises error if exit status indicates a failure."""
    try:
        # Run the command in the specified path and capture the output
        result = subprocess.run(command, shell=True,
                                text=True, capture_output=True, cwd=cwd_path)

        # Check the return code to determine success
        if result.returncode != 0:
            raise ValueError(
                f"Command failed with return code {result.returncode}:\n{result.stdout.strip()}")
    except Exception as e:
        raise ValueError(f"An error occurred: {e}")
    return result


def wait_ping(host, timeout=45):
    """Subprocess to continuously ping an ip address. Fails if ping does not succeed before timeout."""
    start_time = time.time()
    ping_succeeded = False
    while time.time() - start_time < timeout:
        # Run the ping command
        try:
            subprocess.check_output(['ping', '-c', '1', host])
            ping_succeeded = True
            break
        except subprocess.CalledProcessError:
            # If ping failed, wait for a while before retrying
            time.sleep(1)
    return ping_succeeded


def ssh_with_command(host, password, cmd):
    """Use paramiko to ssh to host and run a command, returns stdin/stdout/stderr"""
    output = None
    try:
        # Create SSH client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the SSH server
        ssh_client.connect(hostname=host, password=password)

        # Open a session
        ssh_session = ssh_client.get_transport().open_session()

        # Execute command
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        output = stdout.read().decode()

        # Close the SSH session and connection
        ssh_session.close()
        ssh_client.close()
        return output

    except Exception as e:
        logging.error(f"An error occurred during ssh with command {cmd}: {e}")
        return None


def get_current_git_commit_hash():
    """Uses gitpython to get the short-hash of the current commit."""
    try:
        # Open the repository
        repo = git.Repo(get_repo_path())

        # Get the hash of the current commit
        short_commit_hash = repo.head.object.hexsha[:7]

        return short_commit_hash

    except Exception as e:
        logging.error(f"An error occurred during git hash retrieval: {e}")
        return None


def get_host_ip():
    ip = None
    try:
        # Connect to an external address to get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        logging.error(f"Unable to get local host ip: {e}")
    return ip


def _repo_path(self):
    """Returns absolute path of embedded-software"""
    return path.abspath(path.join(__file__, "../../../"))

def print_summary(self):
    """Prints details of object attributes and methods"""

    attributes = [attr for attr in dir(self) if not callable(
        getattr(self, attr)) and not attr.startswith("_")]
    methods = [method for method in dir(self) if callable(
        getattr(self, method)) and not method.startswith("_")]

    summary = f"{type(self)}\n\nSummary:\n"
    for attribute in attributes:
        summary += f"{attribute}: {getattr(self, attribute)}\n"

    summary += "\nMethods:\n"
    for method_name in methods:
        method = getattr(self, method_name)
        method_signature = inspect.signature(method)
        summary += f"{method_name}{method_signature}\n"

    print(summary)
