# log既显示在console口，又保存在文件li
# 封装到一个模块中，然后其他case来调用
import logging

logger = logging.getLogger(__name__)    # __name__可以根据需要设置
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)
# 具体使用以上方法来记录log,参考logtest.py
# logger.info('Start')
# logger.warning('Something maybe fail.')
# try:
#     result = 10 / 0
# except Exception:
#     logger.error('Failed to get result', exc_info=True)
#     # logging.exception("Exception occurred")
# logger.info('Finished')
