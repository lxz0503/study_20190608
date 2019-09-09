import logging

logging.basicConfig(filename="test.log",
                    filemode="w",
                    format="%(asctime)s %(filename)s: [line:%(lineno)d] %(levelname)s: %(message)s",  # 这个filename是脚本名字
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.DEBUG)