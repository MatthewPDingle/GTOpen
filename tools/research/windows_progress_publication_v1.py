"""Bounded recovery from Windows sharing conflicts for mutable progress only.

Never use this to rewrite registered results or scientific checkpoints. An
unpublished temporary file is retained if publication ultimately fails.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import time
import uuid


def publish_progress(path, value, *, timeout=5.0):
    if os.name != 'nt' or not 0 < timeout <= 5:
        raise ValueError('Windows and a bounded positive timeout are required')
    path = Path(path)
    if not path.name.endswith('-status.json'):
        raise ValueError('Mutable status path required')
    pending = path.with_name('.status-retry-' + uuid.uuid4().hex + '.pending')
    with pending.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, separators=(',', ':'), allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    deadline = time.monotonic() + timeout
    retries = 0
    while True:
        try:
            os.replace(pending, path)
            return retries
        except OSError as error:
            if getattr(error, 'winerror', None) not in (5, 32, 33):
                raise
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise
            retries += 1
            time.sleep(min(0.05, remaining))


@contextmanager
def status_only(driver):
    original = driver.write_status
    path = driver.OUT / f'{driver.PREFIX}-status.json'
    def write(value):
        publish_progress(path, value)
    driver.write_status = write
    try:
        yield
    finally:
        driver.write_status = original
