import logging

import pytest

from haloslackchat.botlogging import log_setup


@pytest.fixture(scope="module")
def log():
    """Set up logging as a pytest fixture."""
    log_setup()
    return logging.getLogger('haloslackchat')
