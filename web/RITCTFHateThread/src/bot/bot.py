from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time

def checkEssay(data):
    opts = Options()
    opts.add_argument("--headless")
    driver = Firefox(options=opts)
    driver.set_window_size(320, 240)
    driver.set_page_load_timeout(5)
    driver.get('http://127.0.0.1:8000/')
    driver.add_cookie({"name":"auth","value":"UMASS{N4MB3R_0N3_1N_$TUD3NT_D1N1NG_DVMA216537}"})
    driver.get('http://127.0.0.1:8000/review/essay?email={a}&essay={b}'.format(a=data['email'],b=data['essay']))
    time.sleep(3)
    driver.quit()