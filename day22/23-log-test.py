from logtestmain import *

logger.info('Start')
logger.warning('Something maybe fail.')
try:
    result = 10 / 0
except Exception as e:
    logger.error('======exception as below=======')
    logger.error(str(e), exc_info=True)
    # logging.exception("Exception occurred")
logger.info('Finished')