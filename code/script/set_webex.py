from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import pandas as pd

import os
import time

from helper_functions import FindElements

class setWebex:
    def __init__(self, data, driver):
        '''
        Set the agents' profiles in Webex.
        '''
        self._df = pd.DataFrame(data)

        print('*--- WEBEX ---*')
        
        # ---- Log in  ---- #
        email_bar = FindElements.waitUntilFound(driver, 'IDToken1', 'id')
        email_bar.send_keys(os.getenv('WEBEX_EMAIL'), Keys.RETURN)

        pwd_bar = FindElements.waitUntilFound(driver, 'IDToken2', 'id')
        pwd_bar.send_keys(os.getenv('WEBEX_PWD'), Keys.RETURN)

        # --- START ONBOARDING --- #

        for index, row in data.iterrows():
            # Agent's info
            email = row['Email']
            team = row['Team']

            print('\n', 'Working with:', email)

            # Search agent
            search_bar = FindElements.waitUntilFound(driver, "div#user-container_filter > label > input[type='search']")
            search_bar.clear()
            search_bar.send_keys(email)

            # If there are no results, go next
            try:
                FindElements.tryToFind(driver, 'dataTables_empty', 'class_name')
            except NoSuchElementException:
                pass
            else:
                print(email, 'showed no results, going next')
                continue

            # Get display name
            first_name = FindElements.waitUntilFound(driver, "tr[role='row'] > td:nth-child(2)").text
            last_name = FindElements.waitUntilFound(driver, "tr[role='row'] > td:nth-child(3)").text

            # Add it to the table
            self._df.loc[index, 'Display Name'] = first_name + ' ' + last_name

            # Status
            status = FindElements.waitUntilFound(driver, "tr[role='row'] > td:nth-child(8)").text

            # Click on edit
            driver.execute_script("arguments[0].setAttribute('class', 'dropdown actions open')",
                                FindElements.waitUntilFound(driver, "tr[role='row'] > td > div.dropdown.actions"))
            FindElements.waitUntilFound(driver, "a.action-edit[data-title='Edit']").click()

            try:
                # If agent not enabled, complete the initial settings
                if status.lower() == 'no':
                    # Enable Call Center Capabilities
                    FindElements.waitUntilFound(driver, 'span.toggle-handle.btn.btn-default.btn-sm').click()
                else:
                    raise NoSuchElementException
            except NoSuchElementException:
                pass
            else:
                print('Adding info..')

                # User Profile
                user_profile = FindElements.waitUntilFound(driver, 'span#select2-userProfileId-container')
                user_profile.click()
                write = FindElements.waitUntilFound(driver, "span > span > input.select2-search__field[type='search']")
                write.send_keys(TEAMS[team][0], Keys.ENTER, Keys.ESCAPE)

                time.sleep(1)

                # Site
                site = FindElements.waitUntilFound(driver, 'span#select2-siteId-container')
                site.click()
                write = FindElements.waitUntilFound(driver, 'span > span > span > input.select2-search__field')
                write.send_keys('RadNet', Keys.RETURN, Keys.ESCAPE)
                
                time.sleep(0.5)

                # Skill Profile
                skill = FindElements.waitUntilFound(driver, 'select2-skillProfileId-container', 'id')
                skill.click()
                write = FindElements.waitUntilFound(driver, 'span > span > span.select2-search.select2-search--dropdown > input.select2-search__field')
                write.send_keys('Scheduler Level 01 Bilingual', Keys.RETURN, Keys.ESCAPE)

            time.sleep(0.2)

            # Check team assignment
                # Search field
            team_bar = FindElements.waitUntilFound(driver, "ul > li > input")
            try:
                # Confirm there is not a team assigned already
                FindElements.tryToFind(driver, 'ul > li.select2-selection__choice > span')

            except NoSuchElementException:
                # Wait for the next fields to update
                while True:
                    placeholder = team_bar.get_attribute('placeholder')
                    if placeholder == 'Select an option':
                        break
                    else:
                        time.sleep(3)
            else:
                FindElements.waitUntilFound(driver, 'cancelBtn', 'id').click()
                self._df.loc[index, 'Checked'] = 1 
                self._df.to_excel('data.xlsx', index=False)

                print('Everything was alright.')
                continue

            # When available, continue
            team_bar.send_keys(TEAMS[team][1], Keys.ARROW_DOWN, Keys.RETURN, Keys.ESCAPE)

            time.sleep(0.5)

            # Agent Profile
            agent_profile = FindElements.waitUntilFound(driver, 'select2-agentProfileId-container', 'id')
            agent_profile.click()
            write = FindElements.waitUntilFound('span > span > span.select2-search.select2-search--dropdown > input')
            write.send_keys(TEAMS[team][2], Keys.RETURN, Keys.ESCAPE)

            time.sleep(0.5)

            # Save changes
            save = FindElements.waitUntilFound('button#submitBtn')
            save.click()

            self._df.loc[index, 'Checked'] = True 
            print('Completed.')
        
            self._df.to_excel('data.xlsx', index=False)

        print('Webex done.')