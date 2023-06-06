import json
from emu_config.log import log
from emu_config.variablesBase import base, default

log.debug('base dictionary: '+json.dumps(base, indent=4))
log.debug('default settings dictionary: '+json.dumps(default, indent=4))

from emu_config.variables import path,program

log.debug('path dictionary: '+json.dumps(path, indent=4))
log.debug('program dictionary: '+json.dumps(program, indent=4))


