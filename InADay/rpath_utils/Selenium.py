from scrapy.http import Request

def Selenium_Default_Process(url, driver, process_args):
    driver.get(url)

    return {
        'body': driver.page_source,
        'current_url': driver.current_url,
    }


class SeleniumRequest(Request):
    def __init__(self, selenium_process=Selenium_Default_Process, process_args={}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selenium_process = selenium_process
        self.process_args = process_args