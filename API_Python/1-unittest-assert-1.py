# below is for python3
import unittest
import requests
import logging
logging.basicConfig(filename="test.log",
                    filemode="w",
                    format="%(asctime)s %(filename)s: [line:%(lineno)d] %(levelname)s: %(message)s",  # 这个filename是脚本名字
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.DEBUG)
class UrlGet(unittest.TestCase):
    def setUp(self):
        self.r = requests.get('https://www.baidu.com/?tn=sitehao123_15')

    def test_status_code(self):
        result = self.r
        print(result)
        logging.info('start')
        self.assertEqual(result.status_code, 500, 'status code is not 200')
        logging.info('end')
        # test log is:Ran 1 test in 0.251s
        #
        # FAILED (failures=1)
        # <Response [200]>
        #
        # status code is not 200
        # 500 != 200
        #
        # Expected :200
        # Actual   :500

    def test_response_text(self):
        result = self.r
        # print(result.text)
        logging.info('response start')
        self.assertTrue('baidu' in result.text)
        logging.info('response end')


if __name__ == '__main__':
    unittest.main()