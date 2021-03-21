from Selenium_scripts.Interact import Interact
from scrapy.selector import Selector

class InADay_Interact(Interact):

    def __init__(self, driver):
        super().__init__(driver)

def selenium_process(url, driver, process_args):
    pass