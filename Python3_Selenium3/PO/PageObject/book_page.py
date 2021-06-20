from Base.base import Base
import time


class BookPage(Base):
    # 预定车票
    def book(self):  # find book button
        return self.by_xpath("//*[@id='tbody-01-K5260']/div[1]/div[6]/div[4]/a")

    # 动车
    def book_typeD(self):
        return self.by_css("#resultFilters01 > dl:nth-child(1) > dd.current > label > i")

    # # 关闭浮层
    # def book_close(self):
    #     return self.by_css("#appd_wrap_close")

    def book_btn(self):    # click book button
        try:
            self.book().click()
            time.sleep(10)
        except Exception as e:
            self.log.error("车次查询失败")
        return self.dr_url()
