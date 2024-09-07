import pytest
import os

@pytest.hookimpl
def pytest_runtest_setup(item):
    """
    Modifies one of the existing pytest_runtest_* hook functions that pytest calls in order to
    dynamically set the log filename using the current date and time.
    """
    logging_plugin = item.config.pluginmanager.get_plugin("logging-plugin")
    timestamp = get_timestamp()
    log_filepath = os.path.abspath(os.path.join(__file__, "../../", "validation", "logs"))
    os.makedirs(log_filepath, exist_ok=True)
    filename = os.path.join(log_filepath, f'{timestamp}.log')
    logging_plugin.set_log_path(filename)
