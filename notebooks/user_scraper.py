from os.path import exists
# import pandas as pd
# import csv
# from parsel import Selector
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
# from datetime import date
# from datetime import datetime, timedelta
import time
import re
# import networkx as nx
# import matplotlib.pyplot as plt
# from pyvis.network import Network
import math
# from selenium.common.exceptions import NoSuchElementException
import pickle


class UserDict:
    """
    A class used to scrape, process, and retrieve user and follower data from
        Steepster.

    ...

    Attributes
    ----------
    self.user_dict : dict
        Either loads an existing user dictionary or initializes a new dict.
    
    self.all_urls : list
        Big ol' list of all user URLs that is used by other functions to keep
            populating the user_dict.
            -- Note: this should probably be created as a set. Might make things
                just a bit simpler. Later.

    Methods
    -------
    

    # get_teas(tea_pages_to_scrape=1)
        # Scrapes tea names, brands, and URLs from Steepster tea overview page.

    # get_reviews(min_review_pgs=1):
        # Gets reviewer names and ratings for each tea.

    # save_tea_dict(filename='tea_dict',filetype='p'):
        # Pickles the tea_dict data for later use.
    
    
    """

    def __init__(self):
        """
        Initializes the UserDict class with existing data or an empty dictionary
            if no previous data exists.

        ...

        Attributes
        ----------
        self.user_dict : dict
            Either an existing user dictionary or newly initialized empty dict.
        
        """
        user_dict_exists = exists('..\\data\\pickled-data\\user_dict.p')
        if user_dict_exists == True:
            with open("..\\data\\pickled-data\\user_dict.p", 'rb') as p:
                self.user_dict = pickle.load(p)
        else:    
            self.user_dict = {}

        all_urls_exists = exists('..\\data\\pickled-data\\all_urls.p')
        if all_urls_exists == True:
            with open("..\\data\\pickled-data\\all_urls.p", 'rb') as p:
                self.all_urls = pickle.load(p)
        else:
            self.all_urls = []

    
    def get_first_user(self, username='jack'):
        """
        Adds a specific user to start the self.user_dict. You should also use
            this to start your own user_dict from scratch, but you will probably
            use it for adding specific users.
        
        ...

        Parameters
        ----------
        username : str
            The username to start the dictionary. (default is 'jack')
        
        """

        # Creates driver that is updated to work with the latest version of Chrome
        driver = webdriver.Chrome(ChromeDriverManager().install())

        # Navigate to Jack's page (user #1)
        driver.get(f'https://steepster.com/{username}/followers?page=1')

        # self.all_urls = []

        current_user = username

        self.user_dict = {current_user:{}}

        follower_count = int(driver.find_element_by_id('follower_count').text)
        max_follower_pg = int(math.ceil(follower_count / 10.0))

        self.user_dict[current_user]['follower_count'] = follower_count
        self.user_dict[current_user]['follower_pgs'] = max_follower_pg

        following_count = int(driver.find_element_by_id('following_count').text)
        # max_following_pg = int(round(following_count,-1)/10)
        max_following_pg = int(math.ceil(following_count / 10.0))

        # self.user_dict[current_user]['following_count'] = following_count
        # self.user_dict[current_user]['following_pgs'] = max_following_pg

        # user_id = driver.find_elements_by_css_selector("h1>a")

        # for id_info in user_id:
        #     user_id = id_info.get_attribute('data-leader-id')

        follower_urls = []
        # This list will be attached as the followers to the user
        # It will also become the list from which we work to pull names to grow the network

        ff_counts = []

        for j in range(1,min(max_follower_pg+1,2)):
            print('now reading ', current_user, ' page ', j)
            
            # if we're on page 1, keep going. Otherwise, load the next page
            if j == 1:
                pass
            else:
                driver.get(f'https://steepster.com/{current_user}/followers?page={j}')


            # this is where the common xpath goes
            # user_div = driver.find_elements_by_xpath("//div[@class='user']")

            # Get all user urls from the current page
            all_links = driver.find_elements_by_css_selector(".users>.user>.details>a")

            # For users who aren't in the self.user_dict yet, so I need to get their followers
            need_followers = []

            
            for link in all_links:
                user_link = link.get_attribute("href")
                m = re.search(r"(?<=\.com\/).*", user_link)
                follower_urls.append(m.group(0))  # User url: 'jack', 'mike276', etc.

                print('current_follower: ', m.group(0))
                # print('Current self.user_dict list: ', self.user_dict.keys())

                # If the user isn't already in the dictionary, add it to a list to add later
                if m.group(0) not in self.user_dict.keys():
                    print('User is not in self.user_dict')
                    if len(self.all_urls) > 0:
                        self.all_urls.append(m.group(0))
                    # Don't add to dictionary yet. I'll do that with the zipped lists later
                    need_followers.append(m.group(0))
                else:
                    print("This user is already in the self.user_dict")
            print('need_followers for ',current_user,': ',need_followers)
            
            # need to just get both of these at the same time. They share a CSS root
            follower_followers = driver.find_elements_by_css_selector(".users>.user>.details>em")

            for count in follower_followers:
                ff_count = int(count.get_attribute("data-pluralize-count"))
                ff_counts.append(ff_count)

            # zip the lists together
            zipped_ff_list = list(zip(follower_urls, ff_counts))

            print('Followers who are not in the self.user_dict and their follower count:\n', zipped_ff_list)

            # Add new users and their follower counts to the self.user_dict
            for user, user_ff_count in zipped_ff_list:
                print('First user in zipped_ff_list: ', user)
                if user in need_followers:
                    print('adding ',user,' to self.user_dict')
                    self.user_dict[user] = {}
                    self.user_dict[user]['follower_count'] = user_ff_count
                    max_follower_pg = int(math.ceil(self.user_dict[user]['follower_count'] / 10.0))
                    self.user_dict[user]['follower_pgs'] = max_follower_pg
                else:
                    print(user,' is already in self.user_dict')
                # time.sleep(3)

        # follower_urls is added to the current user's dict entry
        self.user_dict[current_user]['followers'] = follower_urls

        self.all_urls = follower_urls
        # Now go to the next follower page

        time.sleep(0.5)

        # Close browser and terminate driver instance
        driver.quit()


    def get_users(self, num_users=2):
        # to advance current user down the list of users,

        i = 0

        # for i in range(0,len(all_urls)+1):

        # this is the number of new users I want to add to the user_dict
        while i < num_users: # len(all_urls)+1:

            current_user = self.all_urls[i]

            # print('---------------------\ncurrent_user: ',current_user)
            # print('---------------------\nall_urls index: ',i)

            # Check if current user already has followers before doing anything else
            if 'followers' in self.user_dict[current_user]:
                # print(f"{current_user} already has followers")
                num_users += 1
                # print(f"new num_users: {num_users}")
                i += 1
            else:
                driver = webdriver.Chrome(ChromeDriverManager().install())

                # Navigate to user's followers page
                driver.get(f'https://steepster.com/{current_user}/followers?page=1')

                # Set max follower and following pages
                max_follower_pg = self.user_dict[current_user]['follower_pgs']

                following_count = int(driver.find_element_by_id('following_count').text)
                # max_following_pg = int(round(following_count,-1)/10)
                max_following_pg = int(math.ceil(following_count / 10.0))
                
                follower_urls = []

                for j in range(1, min(max_follower_pg+1,4)):
                    # print('now reading ', current_user, ' page ', j)

                    # Saves a reload of the first page for every user
                    if j == 1:
                        pass
                    else:
                        driver.get(f'https://steepster.com/{current_user}/followers?page={j}')

                    # Retrieve URLs for followers
                    all_links = driver.find_elements_by_css_selector(".users>.user>.details>a")
                    
                    # For users who aren't in the user_dict yet, so I need to get their followers
                    need_followers = []
                    page_follower_urls = []
                    ff_counts = []

                    # Parse usernames from href (e.g., 'jack' from 'steepster.com/jack')
                    for link in all_links:
                        user_link = link.get_attribute("href")
                        m = re.search(r"(?<=\.com\/).*", user_link)
                        follower_urls.append(m.group(0))
                        page_follower_urls.append(m.group(0))
                        # if url not in user_dict keys, append to all_urls

                        print('current_follower: ', m.group(0))
                        # print('Current user_dict list: ', user_dict.keys())
                        

                        if m.group(0) not in self.user_dict.keys():
                            # print('User is not in user_dict')
                            if len(self.all_urls) > 0:
                                self.all_urls.append(m.group(0))
                            # Don't add to dictionary yet. I'll do that with the zipped lists later
                            need_followers.append(m.group(0))
                        else:
                            pass
                            # print("This user is already in the user_dict")
                    # print('need_followers for ',current_user,': ',need_followers)
                    
                    # if url not in all_urls, add to a list to get number of followers
                    follower_followers = driver.find_elements_by_css_selector(".users>.user>.details>em")

                    for count in follower_followers:
                        ff_count = int(count.get_attribute("data-pluralize-count"))
                        ff_counts.append(ff_count)
                    
                    # zip the lists together
                    zipped_ff_list = list(zip(page_follower_urls, ff_counts))

                    print('Followers who are not in the user_dict and their follower count:\n', zipped_ff_list)

                    for user, user_ff_count in zipped_ff_list:
                        # print('User in zipped_ff_list: ', user)
                        if user in need_followers:
                            # print('adding ',user,' to user_dict')
                            self.user_dict[user] = {}
                            self.user_dict[user]['follower_count'] = user_ff_count
                            max_follower_pg = int(math.ceil(self.user_dict[user]['follower_count'] / 10.0))
                            self.user_dict[user]['follower_pgs'] = max_follower_pg
                        else:
                            pass
                            # print(user,' is already in user_dict')
                        # time.sleep(3)

                self.user_dict[current_user]['followers'] = follower_urls

                # Increment i to move to next user once browser closes
                i+=1

                # print('---------------------\nall_urls: ',self.all_urls)

                # Close browser and terminate driver instance

        driver.quit()

    
    def update_users(self,num_users=1,num_follower_pgs=2):
        """
        Get more follower info for users in the user_dict who already have some
            followers but haven't had all followers scraped yet. For example, 
            if someone has 500 followers, there would be 50 pages of followers.
            If you have only sraped 20 followers, the function will begin
            scraping at page 3 and continue for the specified number of pages.

        ...

        Parameters
        ----------
        num_users : int
            The number of users for which you want more follower info. 
            (default is 1)


                time.sleep(0.25)

    def save_user_dict(self,filename='user_dict',filetype='p'):
        """Pickle the user_dict data for later use.
        
        Parameters
        ----------

        filename : str
            Name assigned to the saved file.
            
        filetype : str       
            Extension you want appended to the file. Default is 'p' for pickle.

        """
        with open(f"..\\data\pickled-data\\{filename}.{filetype}", "wb") as p:
            pickle.dump(self.user_dict, p)
    

    def save_all_urls(self,filename='all_urls',filetype='p'):
        """Pickle the all_urls list for later use.
        
        Parameters
        ----------

        filename : str
            Name assigned to the saved file.
            
        filetype : str       
            Extension you want appended to the file. Default is 'p' for pickle.

        """
        with open(f"..\\data\pickled-data\\{filename}.{filetype}", "wb") as p:
            pickle.dump(self.all_urls, p)

    def save_all_the_things(self):
        self.save_user_dict()
        self.save_all_urls()

# Need add_followers function to go get more followers for an existing user that
# has either fained followers or never had them all scraped in the first place.

# There is a line that says "for j in range(1, min(max_follower_pg+1,4)):" that
# controls how many pages are scraped initially for each user.
# If a user has 35 followers, that means they have 4 follower pages.
# If len('followers') <= 35, let's say it's 30, then cieling divide that number
# by 10 and you'll get the number of pages already scraped (3). To keep scraping
# start from pages already scraped + 1.