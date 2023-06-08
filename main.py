import json
from emu_config.core import default, core
from emu_config.log import log
from emu_config.variables import paths, programs

log.info('core: '+json.dumps(core, indent=4))
log.info('default settings dictionary: '+json.dumps(default, indent=4))
log.info('paths dictionary: '+json.dumps(paths, indent=4))
# log.debug('path_emulation dictionary: '+json.dumps(path_emulation, indent=4))
# log.debug('path_emuconfig dictionary: '+json.dumps(path_emuconfig, indent=4))
log.debug('programs dictionary: '+json.dumps(programs, indent=4))