from logtestmain import *

logger.info('Start')
logger.warning('Something maybe fail.')
try:
    result = 10 / 0
except Exception:
    logger.error('Failed to get result', exc_info=True)
    # logging.exception("Exception occurred")
logger.info('Finished')