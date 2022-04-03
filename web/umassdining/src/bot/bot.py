from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
admin_cookie = "VEgxUzFTRDRTVVAzUlMzQ1IzVDRETTFOQzAwS0kzTDBMIQ"
def checkEssay(data):
    opts = Options()
    opts.add_argument("--headless")

    driver = Firefox(executable_path='/usr/bin/geckodriver',options=opts)
    driver.set_window_size(320, 240)
    driver.set_page_load_timeout(5)
    driver.get('http://127.0.0.1:6942/')
    driver.add_cookie({"name":"auth","value":admin_cookie})
    driver.get('http://127.0.0.1:6942/review/essay?email={a}&essay={b}'.format(a=data['email'],b=data['essay']))    
    time.sleep(3)
    driver.quit()