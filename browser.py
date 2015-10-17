import selenium.webdriver

import pride.base

class Browser(pride.base.Wrapper):
    defaults = pride.base.Wrapper.defaults.copy()
    defaults.update({"browser_type" : "Firefox",
                     "scroll_amount" : 200})
               
    def __init__(self, **kwargs):
        super(Browser, self).__init__(**kwargs)
        self.driver = getattr(selenium.webdriver, self.browser_type)
        
    def scroll(self, x_amount=0, y_amount=200):
        self.driver.execute_script("window.scrollBy({}, {})".format(x_amount, y_amount), "")