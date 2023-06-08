import os
import logging
from .core import core, default

# Create the log directory if it doesn't exist
log_dir = core['core']['log']
log_file = os.path.join(log_dir,'emu-config-debug.log')
default_log_level = default['log_level']
print(log_file)
os.makedirs(log_dir, exist_ok=True)

if default_log_level == 'DEBUG':
    log_level = logging.DEBUG
elif default_log_level == 'WARNING':
    log_level = logging.WARNING
elif default_log_level == 'ERROR':
    log_level = logging.ERROR
elif default_log_level == 'CRITICAL':
    log_level = logging.CRITICAL
else:
    log_level = logging.INFO

log = logging.getLogger(__name__)

# Set Log level
log.setLevel(log_level)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(log_file)
console_handler.setLevel(log_level)
file_handler.setLevel(log_level)

# Create formatters and add it to handlers
console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_format)
file_handler.setFormatter(file_format)

# Add handlers to the log
log.addHandler(console_handler)
log.addHandler(file_handler)

# Log examples
# log.debug('This is a debug message')
# log.info('This is an info message')
# log.warning('This is a warning message')
# log.error('This is an error message')
# log.critical('This is a critical message')

log.info(f"LOG - Log file: {log_file} Debug level: {default_log_level}")