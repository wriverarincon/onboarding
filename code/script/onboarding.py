# %% [markdown]
# # Imports

# %%
# Web interaction
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Data manipulation
import pandas as pd

# Enviorenment variables
from dotenv import load_dotenv, dotenv_values
import json
load_dotenv()

# Interact with OS/Computer
import os

# Time
import time
import asyncio

# Types
from typing import Callable, Iterable
from selenium.webdriver.remote.webelement import WebElement

# %% [markdown]
# # Data Preparation

# %%
# Data
df = pd.read_excel('./data.xlsx')
df['Display Name'] = df['Display Name'].astype(str)

# %% [markdown]
# # Browser Configuration

# %%
opt = Options()
opt.add_argument('--start-maximized')
opt.add_experimental_option('detach', True)
opt.add_argument('--lang=en')
opt.add_argument('--remote-debugging-port=9222')
opt.add_argument("--window-size=2560,1440")
# opt.add_argument('--headless=new')

# %% [markdown]
# # Helper Functions/Variables

# %%
# Start browser
DRIVER = Chrome(options=opt)

# Wait time
WAIT = WebDriverWait(DRIVER, 30)

# Turn "find_element" method into a function for reuse
def findElement(selector: str, loc: str = 'css_selector') -> WebElement:
    '''
    Puts the DRIVER and WAIT references for easily reuse. With the "tries" parameter we can limit the search
    to prevent an infinite loop.
    '''
    element = None # Web element reference
    
    # Get attribute of the type of selector we choose so we can use it as a variable,
    # therefore change it at will with the function's parameter, i.e "ID, XPATH.."
    locator = getattr(By, loc.upper())

    while True:
        try:
            element = WAIT.until(EC.presence_of_element_located(
                (locator, selector)
                )
            )
            if element != None:
                break
        except TimeoutException:
            pass
    return element
# %%
TEAMS = json.loads(dotenv_values().get('TEAMS'))

# %% [markdown]
# # Webex

# %%
async def onboardOnWebex(data: Iterable):
    '''
    Set the agents' profiles in Webex.
    '''
    print('*--- WEBEX ---*')
    
    # ---- Log in  ---- #
    email_bar = findElement('IDToken1', 'id')
    email_bar.send_keys(os.getenv('WEBEX_EMAIL'), Keys.RETURN)

    pwd_bar = findElement('IDToken2', 'id')
    pwd_bar.send_keys(os.getenv('WEBEX_PWD'), Keys.RETURN)

    # --- START ONBOARDING --- #

    for index, row in data.iterrows():
        # Agent's info
        email = row['Email']
        team = row['Team']

        print('\n', 'Working with:', email)

        # Search agent
        search_bar = findElement("div#user-container_filter > label > input[type='search']")
        search_bar.clear()
        search_bar.send_keys(email)

        # If there are no results, go next
        try:
            DRIVER.find_element(By.CLASS_NAME, 'dataTables_empty')
        except NoSuchElementException:
            pass
        else:
            print(email, 'showed no results, going next')
            continue

        # Get display name
        first_name = findElement("tr[role='row'] > td:nth-child(2)").text
        last_name = findElement("tr[role='row'] > td:nth-child(3)").text

        # Add it to the table
        df.loc[index, 'Display Name'] = first_name + ' ' + last_name

        # Status
        status = findElement("tr[role='row'] > td:nth-child(8)").text

        # Click on edit
        DRIVER.execute_script("arguments[0].setAttribute('class', 'dropdown actions open')",
                            findElement("tr[role='row'] > td > div.dropdown.actions"))
        findElement("a.action-edit[data-title='Edit']").click()

        try:
            # If agent not enabled, complete the initial settings
            if status.lower() == 'no':
                # Enable Call Center Capabilities
                findElement('span.toggle-handle.btn.btn-default.btn-sm').click()
            else:
                raise NoSuchElementException
        except NoSuchElementException:
            pass
        else:
            print('Adding info..')

            # User Profile
            user_profile = findElement('span#select2-userProfileId-container')
            user_profile.click()
            write = findElement("span > span > input.select2-search__field[type='search']")
            write.send_keys(TEAMS[team][0], Keys.ENTER, Keys.ESCAPE)

            time.sleep(1)

            # Site
            site = findElement('span#select2-siteId-container')
            site.click()
            write = findElement('span > span > span > input.select2-search__field')
            write.send_keys('RadNet', Keys.RETURN, Keys.ESCAPE)
            
            time.sleep(0.5)

            # Skill Profile
            skill = findElement('select2-skillProfileId-container', 'id')
            skill.click()
            write = findElement('span > span > span.select2-search.select2-search--dropdown > input.select2-search__field')
            write.send_keys('Scheduler Level 01 Bilingual', Keys.RETURN, Keys.ESCAPE)

        time.sleep(0.2)

        # Check team assignment
            # Search field
        team_bar = findElement("ul > li > input")
        try:
            # Confirm there is not a team assigned already
            DRIVER.find_element(By.CSS_SELECTOR, 'ul > li.select2-selection__choice > span')

        except NoSuchElementException:
            # Wait for the next fields to update
            while True:
                placeholder = team_bar.get_attribute('placeholder')
                if placeholder == 'Select an option':
                    break
                else:
                    time.sleep(3)
        else:
            findElement('cancelBtn', 'id').click()
            df.loc[index, 'Checked'] = 1 
            df.to_excel('data.xlsx', index=False)

            print('Everything was alright.')
            continue

        # When available, continue
        team_bar.send_keys(TEAMS[team][1], Keys.ARROW_DOWN, Keys.RETURN, Keys.ESCAPE)

        time.sleep(0.5)

        # Agent Profile
        agent_profile = findElement('select2-agentProfileId-container', 'id')
        agent_profile.click()
        write = findElement('span > span > span.select2-search.select2-search--dropdown > input')
        write.send_keys(TEAMS[team][2], Keys.RETURN, Keys.ESCAPE)

        time.sleep(0.5)

        # Save changes
        save = findElement('button#submitBtn')
        save.click()

        df.loc[index, 'Checked'] = True 
        print('Completed.')
    
        df.to_excel('data.xlsx', index=False)

    print('Webex done.')

# %% [markdown]
# # Calabrio

# %%
async def onboardOnCalabrio(data: Iterable):
    '''
    Set the agents' profiles in Calabrio.
    '''
    print('*-- Calabrio --*')

    # ---- Log in ---- #
    email_bar = findElement("input[type='text']")
    email_bar.send_keys(os.environ.get('CALABRIO_EMAIL'))

    pwd_bar = findElement("input[type='password']")
    pwd_bar.send_keys(os.environ.get('CALABRIO_PWD'), Keys.RETURN)

    time.sleep(5)

    # Go to 'Users' page
    DRIVER.get(os.environ.get('CALABRIO_URL'))

    time.sleep(1)

    # --- START ONBOARDING --- #
    
    for index, row in data.iterrows():
        # Search field
        search_bar = findElement('dijit_form_FilteringSelect_0', 'id')

        # Agent's info
        name = row['Display Name']
        email = row['Email']
        team = row['Team']
        schedule = row['Schedule']

        print('\n', 'Working with:', name)

        # Search agent
        while True:
            try:
                search_bar.click()
                search_bar.clear()
            except ElementClickInterceptedException:
                time.sleep(5)
            else:
                break

        time.sleep(0.5)
        search_bar.send_keys(name)
        time.sleep(0.5)
        search_bar.send_keys(Keys.RETURN)

        time.sleep(1)

        # If nothing comes up, go next
        try:
            email_bar = WebDriverWait(DRIVER, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'input[type="email"]')
                )
            )
            email_bar.send_keys(email) # Set email
        except TimeoutException:
            DRIVER.refresh()
            df.loc[index, 'Calabrio'] = 1
            df.to_excel('data.xlsx', index=False)
            continue

        # Set team
        team_bar = findElement('dijit_form_FilteringSelect_2', 'id')
        team_bar.clear()
        print(team)
        team_bar.send_keys(team)
        time.sleep(0.2)
        team_bar.send_keys(Keys.RETURN)

        # Set view
        views_bar = findElement('radio-source-target > source-target > div > div:nth-child(1) > text-box > span > div > div > input')
        time.sleep(0.5)
        views_bar.send_keys(os.environ.get('CALABRIO_VIEW'))
        findElement("radio-source-target > source-target > div > div.st-pane.ng-scope > div.list-container > ul > li").click()
        findElement('radio-source-target > source-target > div > div.list-controls.ng-scope > button:nth-child(1) > span').click()
                
        # Set time zones
        time_zones = ['dijit_form_FilteringSelect_3', 'dijit_form_FilteringSelect_4']

        for tz in time_zones:
            while True:
                try:
                    time_zone = DRIVER.find_element(By.ID, tz)
                    time_zone.clear()
                    time_zone.send_keys('[-0800/-0700] America/Los_Angeles (PST/PDT)')
                except NoSuchElementException:
                    # Enable scheduling
                    try:
                        scheduling = DRIVER.find_element(By.CSS_SELECTOR, 'cal-checkbox[auto-qa-id="Users-Scheduling-calCheckbox"]')
                        scheduling.find_element(By.CSS_SELECTOR, 'div > div > material-icon').click()
                    except NoSuchElementException:
                        pass
                else:
                    break

        # Set start date
        date = os.getenv('START_DATE')
        fields = ['cone_wijit_DateTextBox_0', 'cone_wijit_DateTextBox_2']

        for field in fields:
            element = findElement(field, 'id')
            if element.text != '':
                element.send_keys(date, Keys.RETURN)
            else:
                pass
 
        # Set queue
        queue = findElement('dijit_form_FilteringSelect_5', 'id')
        queue.send_keys(TEAMS[team][3])
        time.sleep(0.2)
        queue.send_keys(Keys.RETURN)

        # Set schedule
        SCHEDULES = json.loads(dotenv_values().get('SCHEDULES'))
        
        work_shift = findElement('dijit_form_TextBox_1', 'id')
        work_shift.send_keys(SCHEDULES[schedule])

        DRIVER.execute_script("arguments[0].setAttribute('class', 'lastSelected selected')",
                            findElement('div#dijit__Templated_0 > div.sourceTarget > div.contentBox > div.contentList > li'))
        findElement('div#dijit__Templated_0 > div.sourceTarget > div.arrowContainer > span').click()

        try:
            while DRIVER.find_element(By.CSS_SELECTOR, 'div.title-row__buttons > button[disabled="disabled"]:nth-child(2)'):
                print('\n Theres an issue that is not allowing me to save the changes, I will check again in 30 seconds.')
                for i in range(1, 31):
                    print(f'\rTimer: {i}', end='', flush=True)
                    time.sleep(1)
                
                if input('\n Found the issue? ') == 'y':
                    break
        except NoSuchElementException:
            pass

        # Save changes
        findElement('div.title-row__buttons > button:nth-child(2)').click()

        # Wait until it saves
        findElement('div.title-row__buttons > button[disabled="disabled"]:nth-child(2)')

        # Refresh the page
        DRIVER.refresh()

        df.loc[index, 'Calabrio'] = 1
        df.to_excel('data.xlsx', index=False)

    DRIVER.quit()

# %%
async def main():
    webex = input('Onboard on Webex? Y/N: ').lower()
    calabrio = input('Onboard on Calabrio? Y/N: ').lower()

    if webex == 'y':
        DRIVER.get(os.environ.get('WEBEX_URL'))
        df_filtered = df[(df['Checked'] == 0) | (df['Display Name'] == 'nan')]
        await onboardOnWebex(df_filtered)

    if calabrio == 'y':
        DRIVER.get(os.environ.get('CALABRIO_URL'))
        df_filtered = df[(df['Calabrio'] != 1) & (df['Checked'] == 1)]
        await onboardOnCalabrio(df_filtered)

asyncio.run(main())

# %% [markdown]
# 


