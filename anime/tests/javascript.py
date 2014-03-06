
from anime.tests._classes import FIXTURES_MAP
from anime.tests._functions import create_user
from anime.utils import cache
from datetime import datetime
from django.test import LiveServerTestCase
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from urllib2 import URLError
import os
import signal
import subprocess
import socket
import time


def wait_for_selenium(port, timeout=15):
    """Blocks until the specified port is connectable."""

    def is_connectable(port):
        """Tries to connect to the specified port."""
        try:
            socket_ = socket.create_connection(("127.0.0.1", port), 1)
            socket_.close()
            return True
        except socket.error:
            return False

    count = 0
    step = 5
    while not is_connectable(port):
        if count >= timeout:
            return False
        count += step
        time.sleep(step)
    return True


class JSTests(LiveServerTestCase):

    test_delay = 2
    enabled = True

    @classmethod
    def setUpClass(cls):
        if settings.SELENIUM_LOCAL:
            cls.selenium_server = subprocess.Popen(('java', '-jar', settings.SELENIUM_SERVER_PATH))
            if not wait_for_selenium(4444):
                cls.selenium_server.kill()
                cls.enabled = False
                raise AssertionError("Selenium server does not respond.")

        driver = getattr(webdriver, settings.SELENIUM_DRIVER, None)
        assert driver, "settings.SELENIUM_DRIVER: dirver not found"
        if driver is webdriver.Remote:
            if isinstance(settings.SELENIUM_CAPABILITY, dict):
                capability = settings.SELENIUM_CAPABILITY
            else:
                capability = getattr(webdriver.DesiredCapabilities, settings.SELENIUM_CAPABILITY, None)
                assert capability, 'settings.SELENIUM_CAPABILITY: capability does not exist'
            try:
                cls.driver = driver('http://%s:%d/wd/hub' % (settings.SELENIUM_HOST, settings.SELENIUM_PORT), capability)
            except URLError:
                cls.driver = None
                cls.enabled = False
        else:
            cls.driver = driver(settings.SELENIUM_CHROME_DRIVER)
        super(JSTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()
        if settings.SELENIUM_LOCAL:
            cls.selenium_server.send_signal(signal.SIGINT)
            if cls.selenium_server.poll() is None:
                cls.selenium_server.kill()
                cls.selenium_server.wait()
        super(JSTests, cls).tearDownClass()

    @create_user()
    def setUp(self):
        if not self.enabled:
            self.skipTest("No selenium")

    def tearDown(self, fixture_names=[]):
        for key in ['38e442f57cd588f5e52f1484b1bc67c480df31ae',
                    '47585a4c37e8f7c9845f97099debf576fe46fb92',
                    '66811e1a68035d2514733b54be7e9fc7e98d5a2e',
                    '4c2730ba7c3198ec39fadb22988623e2be0dd908',
                    '8ccbb6ff42daa120dd76e2beec460b282d8ed746',
                    'd3d7104e052e8ffcb12d50a0a67cf73e63bfce2a',
                    'f64fb8af9af73f3cf54dad6c86cc8f6334e9b74a',
                    '6e64e4439655dc3c7be724a8a4799b878373b024',
                    '463afcfedb462d918bc2d37f3e6f18f23acdd9de',
                    '2177e4ddf8cae674f5dc145b3bf45ed0f90eec7f',
                    '0004520750a07fce88a77c57ca7b352d055f40db',
                    'f816664b4adfbf2b459b538060ea231ba93d04e1',
                    'f04ae8e0c0af62999dd60b17418d70cf57e40f32']:
            cache.invalidate_key('mainTable', key)
            cache.delete('ajaxlist:%s' % key)
            cache.invalidate_key('search', key)
            cache.delete('ajaxsearch:%s' % key)
        cache.delete('Stat:1')
        cache.delete('lastuserbundle:1')
        cache.delete('lastuserbundle:2')
        cache.delete('lastuserbundle:3')

        fixtures = fixture_names or getattr(self, 'fixtures', [])
        for fixture in fixtures:
            for k, v in FIXTURES_MAP[fixture].items():
                for i in range(1, v+1):
                    cache.delete('{0}:{1}'.format(k, i))
                cache.delete(k)

    def login(self):
        from anime.tests._functions import user, passwd
        self.driver.get('{0}/login/'.format(self.live_server_url))
        time.sleep(self.test_delay * 1)
        self.driver.find_element_by_xpath("//td/input[@id='id_username']").send_keys(user)
        self.driver.find_element_by_xpath("//td/input[@id='id_password']").send_keys(passwd)
        self.driver.find_element_by_id('login_button').click()

    def logout(self):
        self.driver.get('{0}/logout/'.format(self.live_server_url))
        time.sleep(self.test_delay * 2)

    def check(self):
        status = self.driver.find_element_by_id('test_status')
        while int(status.get_attribute("value")) > 0: # running
            time.sleep(self.test_delay * 0.5)
        return int(status.get_attribute("value"))

    def screenshot(self, name):
        timestamp = datetime.now().isoformat().replace(':', '')
        filename = os.path.join(settings.MEDIA_ROOT, 'tests',
                    "test_{0}_{1}.png".format(name, timestamp))
        if settings.SELENIUM_DRIVER == 'Remote':
            self.driver.get_screenshot_as_file(filename)
        else:
            self.driver.save_screenshot(filename)


    def run_tests(self, name, subname='all', screenshot=True):
        self.driver.get('{0}#test/{1}/{2}'.format(self.live_server_url, name, subname))
        time.sleep(self.test_delay * 1)
        self.driver.find_element_by_xpath("//a[@href='/search/']").click()
        self.driver.find_element_by_id('sin').send_keys(Keys.CONTROL, 'r')
        time.sleep(self.test_delay * 2)
        if screenshot:
            self.screenshot(name)
        button = self.driver.find_element_by_id('test_c_bt')
        while subname == 'all' and self.check() >= 0: # not done
            if screenshot:
                self.screenshot(name)
            button.click()
        time.sleep(self.test_delay * 2)
        self.screenshot(name)


class JSLightTests(JSTests):

    fixtures = ['2trash.json']

    def test_cnt(self):
        self.run_tests('cnt')

    def test_card(self):
        self.login()
        self.run_tests('card')
        self.logout()
        self.run_tests('card')

    def test_statistics(self):
        self.login()
        self.run_tests('statistics')
        self.logout()
        self.run_tests('statistics')

    def test_user(self):
        self.run_tests('user')
        self.run_tests('user', 'logout', False)

    def test_add(self):
        self.login()
        self.run_tests('add')
        self.logout()

    def test_filter(self):
        self.run_tests('filter')


class JSHardTests(JSTests):

    fixtures = ['100trash.json']

    def test_main(self):
        self.run_tests('main')

    def test_search(self):
        self.run_tests('search')
