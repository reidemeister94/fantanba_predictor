def start_chrome_dunkest(self):
        # Adding adblock to chromedriver and starting it #
        options = webdriver.ChromeOptions()
        options.add_extension("browser/adblock.crx")
        options.add_extension("browser/adblock_plus.crx")
        self.driver = webdriver.Chrome("/Users/silvio/OneDrive - Politecnico di Milano/dunkest/browser/chromedriver",chrome_options = options)
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
        # Login to dunkest #
        self.driver.get('https://nba.dunkest.com/it/dashboard')
        time.sleep(5)
        self.driver.find_elements_by_id("qcCmpButtons")[0].click()
        time.sleep(2)
        button_container = self.driver.find_element_by_css_selector(".dun-cart-item.dun-btn.dun-btn--brand-03.ng-star-inserted")
        login_button = button_container.find_element_by_class_name("dun-btn__text").click()
        time.sleep(2)
        username = self.driver.find_element_by_name("email")
        password = self.driver.find_element_by_name("password")
        username.send_keys("silvio.pavanetto@gmail.com")
        password.send_keys("Salmousb1!")
        # username.send_keys("kuhetave@web2mailco.com")
        # password.send_keys("alpine")
        self.driver.find_element_by_css_selector(".dun-login__form.ng-valid.ng-dirty.ng-touched")\
        .find_elements_by_class_name("dun-btn__text")[0].click()
        #self.driver.find_element_by_name("submit").click()
        time.sleep(3)
        self.driver.find_element_by_css_selector(".dun-land-team.ng-star-inserted")\
        .find_elements_by_class_name("dun-btn__text")[0].click()
        time.sleep(4)


   def scraping_dunkest(self):
        # Scraping info from dunkest :)
        '''
        #this works only in the day before new journey starts
        info_team = self.driver.find_element_by_css_selector(".dun-st-tab__data.dun-st-tab__data--info.ng-star-inserted")
        li = info_team.find_elements_by_tag_name("li")[0]
        credits_total_temp = li.text.strip().split("/")[1]
        #print(elem.get_attribute('innerHTML'))
        self.credits_total = float(credits_total_temp)
        '''
        #hardcoded to test the bot in the others days
        self.credits_total = 97.2
        self.credits_computed = self.credits_total
        xpath = "//div[contains(@class, 'dun-my-team__table-players') and contains(@class, 'ng-star-inserted')]"
        finished = False
        while (finished == False):
            table_id = self.driver.find_elements_by_xpath(xpath)
            path_data_player = "//div[contains(@class, 'dun-player-tab') and contains(@class, 'ng-star-inserted')]"
            rows = table_id[0].find_elements_by_xpath(path_data_player)
            # get all of the rows in the table
            for row in rows:
                # Get the columns (all the column 2)
                name_team = str(row.find_elements_by_class_name("dun-tr__team")[0].text)
                position = str(row.find_elements_by_class_name("dun-tr__role")[0].text)
                name_player_ = str(row.find_elements_by_class_name("dun-player-tab__name")[0].text)
                name_player = self.fix_name(name_player_)
                credits_player = float(row.find_element_by_css_selector(".dun-btn.dun-btn--brand-03.dun-btn--icn.dun-btn--credits.ng-star-inserted")\
                    .text.replace("cr","").strip())
                if position == "HC":
                    self.coaches[name_player] = [self.code_teams[name_team.lower()],credits_player,0.0]
                else:
                    #player = [name team, position, cost, score, fantasy pts predicted]
                    self.players[name_player] = [self.code_teams[name_team.lower()],position,credits_player,0.0,0.0]
            if self.check_last_page() == False:
                self.driver.find_element_by_css_selector(".dun-pagination__item.dun-pagination__item--next.ng-star-inserted").click()
                time.sleep(0.3)
            else:
                finished = True


    def add_game_to_list(self,game):
        name_teams = game.find_elements_by_tag_name("h4")
        code_teams = game.find_elements_by_class_name("dun-team-lab")
        away_team = name_teams[0].text.lower().strip()
        home_team = name_teams[1].text.lower().strip()
        #here are all the matches
        self.games.append([away_team,home_team])
        #here are all the teams together
        if home_team not in self.games_list:
            self.games_list.append(home_team)
            self.code_teams[code_teams[1].text.lower().strip()] = home_team
        if away_team not in self.games_list:
            self.games_list.append(away_team)
            self.code_teams[code_teams[0].text.lower().strip()] = away_team

    def scraping_games_dunkest(self):
        ##scraping games to be played##
        containers_turns = self.driver.find_elements_by_css_selector(".dun-my-team__calendar-table.ng-star-inserted")
        for turn in containers_turns:
            container_games = turn.find_elements_by_class_name("dun-cal-cell__team-wrap")
            for game in container_games:
                self.add_game_to_list(game)
