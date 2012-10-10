
from datetime import datetime
from django.test import LiveServerTestCase
from django.conf import settings
from selenium import webdriver
import os
import time

class JSTests(LiveServerTestCase):

    fixtures = ['100trash.json']

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Firefox()
                        #~ webdriver.Remote('http://127.0.0.1:4444/wd/hub/',
                        #~ desired_capabilities={'javascriptEnabled': True})
        super(JSTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super(JSTests, cls).tearDownClass()

    def check(self):
        status = self.driver.find_element_by_id('test_status')
        while int(status.get_attribute("value")) not in (1, 3): # ready and done
            time.sleep(0.5)
        return int(status.get_attribute("value"))

    def screenshot(self, name):
        timestamp = datetime.now().isoformat().replace(':', '')
        filename = os.path.join(settings.MEDIA_ROOT, 'tests',
                    "test_{0}_{1}_.png".format(name, timestamp))
        self.driver.save_screenshot(filename)

    def run_tests(self, name):
        self.driver.get('{0}#test/{1}/all'.format(self.live_server_url, name))
        self.screenshot(name)
        button = self.driver.find_element_by_id('test_c_bt')
        while self.check() != 3: # done
            self.screenshot(name)
            button.click()
        self.screenshot(name)

    def test_cnt(self):
        self.run_tests('cnt')




