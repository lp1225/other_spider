import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


# dcap = DesiredCapabilities.PHANTOMJS
# print(dcap)
# dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36")

driver = webdriver.PhantomJS(executable_path='D:/phantomjs/phantomjs-2.1.1-windows/bin/phantomjs.exe')

# driver = webdriver.PhantomJS(desired_capabilities=dcap)
driver.set_page_load_timeout(10)
driver.set_script_timeout(10)  # 设置页面退出时间

try:
    driver.get("http://www.baidu.com")
    content = driver.page_source
    print(content)
    time.sleep(1)
except:
    driver.execute_script('window.stop()')
driver.close()

