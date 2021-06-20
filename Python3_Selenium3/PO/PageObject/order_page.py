from Base.base import Base
import time


class OrderPage(Base):   # this is a trial, I did not add any passenger infor
    # 预定车票
    def input_box(self):   # this is an input box
        return self.by_css("#pasglistdiv > div > ul > li:nth-child(2) > input")

    def user_info(self, name):  # input username
        time.sleep(5)
        self.input_box().send_keys(name)
        time.sleep(2)
