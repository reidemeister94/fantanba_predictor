import time
from selenium import webdriver
import sys
import os
from pathlib import Path
import platform

path_util = Path(os.getcwd())
path_util = str(path_util) + '/utils/'
sys.path.append(path_util)
import minor_things_helper


class scraper:
    def __init__(self):
        # this function substitutes start_chrome
        # Adding adblock to chromedriver and starting it #
        options = webdriver.ChromeOptions()
        #print(str(Path(os.getcwd())) + "/browser/adblock.crx")
        options.add_extension(
            str(Path(os.getcwd())) + "/browser/adblock.crx"
        )
        options.add_extension(
            str(Path(os.getcwd())) + "/browser/adblock_plus.crx"
        )
        if platform.system() == 'Windows':
            self.driver = webdriver.Chrome(
                str(Path(os.getcwd())) + "/browser/chromedriver.exe",
                options=options)
        else:
            self.driver = webdriver.Chrome(
                str(Path(os.getcwd())) + "/browser/chromedriver",
                chrome_options=options)
        time.sleep(2.5)
        before = self.driver.window_handles[0]
        after = self.driver.window_handles[1]
        self.driver.switch_to_window(after)
        time.sleep(0.5)
        self.driver.close()
        time.sleep(0.5)
        self.driver.switch_to_window(self.driver.window_handles[1])
        time.sleep(0.5)
        self.driver.close()
        time.sleep(0.5)
        self.driver.switch_to_window(before)

    def check_last_page(self):
        try:
            next_page_button = self.driver.find_element_by_css_selector(
                ".dun-pagination__item.dun-pagination__item--next.ng-star-inserted"
            )
        except Exception:
            # selenium.common.exceptions.NoSuchElementException
            return True
        return next_page_button is None

    def scraping_bets(self, dunkest_bot):
        ##SCRAPING BETS FOR THE GAMES TO BE PLAYED##
        self.driver.execute_script("window.open('');")
        time.sleep(1)
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get('https://www.sisal.it/scommesse/basket/usa/nba')
        time.sleep(4.5)
        xpath_games = "//div[@class='events']/div[contains(@class, 'partitasingola') and contains(@class, 'multiscommessa')]\
        [@style='display: block;']/div"

        xpath_teams = ".//div[@class='multiscommessa__dettagli']/div[@class='multiscommessa__dettagli__nome']"
        xpath_bets = ".//div[@class = 'multiscommessa__container__allquote']/div[@class='multiscommessa__container__quote']\
        /div[@class='multiscommessa__box__esito__singolo']/div[contains(@class, 'quota')]/div[@class='quota-label gradient']"

        events_deep = self.driver.find_elements_by_xpath(xpath_games)
        for game in events_deep:
            string_teams = game.find_elements_by_xpath(xpath_teams)[0].text
            string_teams = minor_things_helper.fix_sisal_name_teams(
                dunkest_bot, string_teams)
            string_bets = game.find_elements_by_xpath(xpath_bets)
            dunkest_bot.teams_and_bets_from_sisal[str(
                string_teams[0])] = float(string_bets[0].text)
            dunkest_bot.teams_and_bets_from_sisal[str(
                string_teams[1])] = float(string_bets[1].text)
        self.driver.close()
        time.sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(2)
