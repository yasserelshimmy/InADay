from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException
import usaddress
from selenium import webdriver


class Interact:
    """This Class contains multiple helper methods to interact with webpages using selenium

    Attributes
    ----------
    driver : str
        The webdriver that will be used to navigate the web
    matching_keys : list
        The list of keys used by the "compare_addresses" method to dissect the addresses and compare its parts
        see following to see what keys you can use:
            https://usaddress.readthedocs.io/en/latest/
    slave_tabs
        The list where new tab IDs are stored at time of creation to be referenced in order
    master_tabs
        The list where "current/previous" tab IDs are stored at the of creating a new to be referenced in order

    Methods
    -------
    def set_address_keys(self, val: list)
        This method can be used to change the "matching_keys" class variable
    def stringsintersect(string1, string2, intersection_level=0.5)
        This function can be used to determine if two strings achieve a certain level of exact matchness
    def compare_addresses(self, desired_adr, suggested_adr, intersection_level=0.5)
        This method is used to to see if two addresses match where it counts as determined by "matching_keys"
    def get_webelement(self, xpath)
        This method return a selenium.webelement using provided xpath
    def get_webelements(self, xpath, visible=False)
        This method returns a list of selenium.webelement elements using provided xpath
    def click(self, xpath)
        This method click on an element on a website using provided xpath or selenium.webelement
    def wait(self, xpath, timeout=10, clickable=False, invisibility=False, present=False)
        This method will wait for an element to be visible on a webpage unless other condition is desired
    def sendkeys(self, xpath, keys, dont_clear=False)
        This method will send keys to an element on a webpage using provided xpath or selenium.webelement
    def new_tab(self)
        This method will open a new tab and change focus to it
    def close_tab(self)
        This method will close the current tab and will change focus to the one before it.
    def full_page_screenshot(self)
        This method will take a full page screenshot of the webpage and return a png image of it
    def getElemsFromShadowRoot(self, css_selector)
        This method will recursively look for elements with the provided css_selector and return a list of selenium.webelement elements
    def clear_cache(self)
        This method will clear the cache of the chromedriver instance used by the class
   """
    def __init__(self, driver: webdriver):
        """
        Parameters
        ----------
        driver : selenium.webdriver
            The webdriver the will be used to navigate to the webpage
        """
        self.driver = driver
        self.master_tabs = []
        self.slave_tabs = []
        self.matching_keys = ["AddressNumber",
                              "StreetName", "ZipCode"]

    def set_address_keys(self, vals: list):
        """This method will update the list of keys used by the "compare_addresses" method to dissect the addresses and compare its parts
           see following to see what keys you can use:
            https://usaddress.readthedocs.io/en/latest/

        Parameters
        ----------
        vals : list
            list of keys used for comparing addresses for the "compare_addresses" method
        """
        self.matching_keys = vals

    @staticmethod
    def stringsintersect(string1, string2, separator=' ', intersection_level=0.5):
        """This function will return a boolean value indicating if two strings intersect to an acceptable degree

        Paramaters
        ----------
        string1 : str
            The first string in the string comparison
        string2 : str
            The second string in the string comparison
        separator : str
            The separator used to split up the strings to lists
        intersection_level : float
            The degree to which the strings intersection/similarity is acceptable

        Return
        ------
        Bool
            A boolean value indicating if the strings match acceptably
        """
        s1 = string1.split(separator)
        s2 = string2.split(separator)
        max_length = max([len(s1), len(s2)])
        intersections = len(set(s1).intersection(s2))
        magnitude_of_intersection = intersections / max_length
        if magnitude_of_intersection >= intersection_level:
            return True
        else:
            return False

    def addresses_match(self, desired_adr, suggested_adr, intersection_level=0.5):
        """This function will return a boolean value indicating if two addresses intersect to an acceptable degree

        Paramaters
        ----------
        desired_adr : str
            The first string in the string comparison
        suggested_adr : str
            The second string in the string comparison
        intersection_level : float
            The degree to which the addresses intersection/similarity is acceptable

        Return
        ------
        Bool
            A boolean value indicating if the addresses match acceptably
        """
        looped = 0
        input_adr = dict(usaddress.tag(desired_adr.lower())[0])
        suggested_adr = dict(usaddress.tag(suggested_adr.lower())[0])
        for tag, value in suggested_adr.items():
            if tag in self.matching_keys:
                looped += 1
                input_adr_tag_value = input_adr.get(tag, False)
                if input_adr_tag_value:
                    if not Interact.stringsintersect(input_adr_tag_value, value, intersection_level=intersection_level):
                        return False
        if looped > 0:
            return True
        else:
            return False

    def get_webelement(self, xpath, visible=False):
        """This method returns a selenium.webelement using a given xpath

        Parameters
        ----------
        xpath : str
            xpath for desired webelement
        visible : bool, optional
            set to True if you want the element if its visible only

        Return
        ------
        selenium.webelement
            the webelement on the page with the given xpath
        """
        if visible:
            try:
                element = self.get_webelements(xpath, visible=True)[0]
            except IndexError:
                element = self.driver.find_element_by_xpath(xpath)
        else:
            element = self.driver.find_element_by_xpath(xpath)
        return element

    def get_webelements(self, xpath, visible=False):
        """This method returns a list of selenium.webelement elements using a given xpath

        Parameters
        ----------
        xpath : str
            xpath for desired webelements
        visible : bool, optional
            set to True if you want the element if its visible only

        Return
        ------
        list
            the list of selenium.webelement elements on the page with the given xpath
        """
        if visible:
            elements = [elem for elem in self.driver.find_elements_by_xpath(xpath) if elem.is_displayed()]
        else:
            elements = self.driver.find_elements_by_xpath(xpath)
        return elements

    def click(self, xpath, normal_click=False):
        """This subroutine clicks on an element on a page using a given xpath or selenium.webelement

        Parameters
        ----------
        xpath : str or selenium.webelement
            xpath or selenium.webelement that will be clicked
        normal_click : bool, optional
            set to true if you want to do a normal selenium click as opposed to a JS click.
        """
        if isinstance(xpath, str):
            element = self.get_webelement(xpath)
        else:
            element = xpath
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        if normal_click:
            element.click()
        else:
            self.driver.execute_script('arguments[0].click()', element)

    def wait(self, xpath, timeout=10, clickable=False, invisibility=False, present=False, staleness=False, nofail=False):
        """This subroutine is used to wait for a condition to happen on the page

        Parameters
        ----------
        xpath : str
            the xpath for the element desired to have the condition to be tested against
        timeout : int, optional
            the duration to wait for the condition to be fulfilled
        clickable : bool, optional
            set to true if you want the condition is that the element to be clickable
        invisibility : bool, optional
            set to true if you want the condition is that the element to be invisible
        present : bool, optional
            set to true if you want the condition is that the element to be present
        nofail : bool, optional
            set to true if you want to avoid timeout exceptions
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            if clickable:
                wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            elif invisibility:
                wait.until(EC.invisibility_of_element_located((By.XPATH, xpath)))
            elif present:
                wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            elif staleness:
                wait.until(EC.staleness_of((By.XPATH, xpath)))
            else:
                wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        except TimeoutException as timeout_exception:
            if not nofail:
                raise timeout_exception

    def sendkeys(self, xpath, keys, dont_clear=False):
        """This subroutine is used to send keys to a field on a webpage

        Parameters
        ----------
        xpath : str or selenium.webelement
            the field that needs to be sent the desired keys
        keys : str
            the text you want in the field
        dont_clear : bool, optional
            set to true if you want the field to not be cleared before filling it with desired text
        """
        if isinstance(xpath, str):
            element = self.get_webelement(xpath)
        else:
            element = xpath
        if not dont_clear:
            element.clear()
        element.send_keys(keys)

    def new_tab(self):
        """This subroutine is used to open a new tab and switch focus to it"""
        master_window_handle = self.driver.current_window_handle
        before_new_window = self.driver.window_handles
        self.driver.execute_script("window.open('', '_blank');")
        slave_window_handle = ''.join(
            [handle for handle in self.driver.window_handles if handle not in before_new_window])
        self.driver.switch_to.window(slave_window_handle)
        self.master_tabs.append(master_window_handle)
        self.slave_tabs.append(slave_window_handle)

    def close_tab(self):
        """This subroutine is used to close the current tab and switch focus to the one before it"""
        self.driver.close()
        self.driver.switch_to.window(self.master_tabs[-1])
        self.master_tabs.remove(self.master_tabs[-1])
        self.slave_tabs.remove(self.slave_tabs[-1])

    def refresh(self):
        self.driver.refresh()

    def full_page_screenshot(self):
        """This method is used to take a screenshot of the webpage and return a png

        Return
        ------
        bytes
            the png image of the page
        """
        width = self.driver.execute_script(
            "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
        height = self.driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
        if height > 4000:
            height = 4000
        if width > 4000:
            width = 4000
        self.driver.set_window_size(width + 100, height + 100)
        return self.driver.get_screenshot_as_png()

    def getElemsFromShadowRoot(self, css_selector):
        """This function is used to recursively search for a webelement in all shadow roots of a webpage

        Parameter
        ---------
        css_selector : str
            The css selector for the webelement that is desired

        Return
        ------
        list
            a list of selenium.webelement elements with webelements the fit the provided selector
        """
        script = """
        var allElems = []
        function recursiveShadows(document, slctr) {
            var allNodes = document.querySelectorAll('*');
            for (var i = 0; i < allNodes.length; i++) {
              if(allNodes[i].shadowRoot) {
                allElems.push.apply(allElems, allNodes[i].shadowRoot.querySelectorAll(slctr))
                recursiveShadows(allNodes[i].shadowRoot, slctr)
              }
            }
        };
        recursiveShadows(document, arguments[0]);
        return allElems;
        """

        elems = self.driver.execute_script(script, css_selector)

        return elems

    def clear_cache(self):
        """This subroutine is used to clear the cache and cookies of the selenium.webdrive instance passed to
            this instance of the class
        """
        self.driver.get('chrome://settings/clearBrowserData')
        retries = 0
        while retries < 5:
            retries += 1
            clear_data_buttons = self.getElemsFromShadowRoot('#clearBrowsingDataConfirm')
            if len(clear_data_buttons) > 0:
                self.click(clear_data_buttons[0])
                break
            else:
                time.sleep(2)

        time.sleep(2)

        waits = 0
        while waits < 5:
            time.sleep(1)
            waits += 1
            elems = [x for x in self.getElemsFromShadowRoot('div.circle') if x.is_displayed()]
            if len(elems) == 0:
                break

        time.sleep(2)

    def scroll_to_load(self, sleeptime=2):
        """This subroutine is used to scroll down to load dynamically loaded elements"""

        # Get scroll height.
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:

            # Scroll down to the bottom.
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(sleeptime)

            # Calculate new scroll height and compare with last scroll height.
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:

                break

            last_height = new_height