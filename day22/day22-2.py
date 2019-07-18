# log既显示在console口，又保存在文件li
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)
# log
logger.info('Start')
logger.warning('Something maybe fail.')
try:
    result = 10 / 0
except Exception:
    # logger.error('Failed to get result', exc_info=True)
    logging.exception("Exception occurred")
logger.info('Finished')
# log
# logger.info("Start print log")
# logger.debug("Do something")
# logger.warning("Something maybe fail.")
# logger.info("Finish")