# Purpose of this class:
## Gather tea names, links, overall ratings - DONE
## Get initial reviewer and rating data for teas - DONE
## Continue updating adding reviewers to teas with no reviewers (haven't written yet)
## Update existing teas if/when they have new reviews (haven't written yet)

from math import ceil
from os.path import exists
import pickle
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from selenium.common.exceptions import NoSuchElementException


class TeaDict:
    """
    A class used to scrape, process, and retrieve tea review data from Steepster

    ...

    Attributes
    ----------
    tea_dict : dict
        Either loads an existing tea dictionary or initializes a new dict.

    Methods
    -------
    get_teas(tea_pages_to_scrape=1)
        Scrapes tea names, brands, and URLs from Steepster tea overview page.

    get_reviews(min_review_pgs=1):
        Gets reviewer names and ratings for each tea.

    save_tea_dict(filename='tea_dict',filetype='p'):
        Pickle the tea_dict data for later use.
    
    """



    def __init__(self):
        """
        A class used to scrape and process tea review data from Steepster

        ...

        Attributes
        ----------
        tea_dict : dict
            Either loads an existing tea dictionary or initializes a new dict.

        Methods
        -------
        get_teas(tea_pages_to_scrape=1)
            Scrapes tea names, brands, and URLs from tea overview page.

        Parameters
        ----------

        tea_dict : dict
            Either loads an existing tea dictionary or initializes a new dict.

        """
        tea_dict_exists = exists('..\\data\pickled-data\\tea_dict.p')
        if tea_dict_exists == True:
            with open("..\\data\\pickled-data\\tea_dict.p", 'rb') as p:
                self.tea_dict = pickle.load(p)
        else:    
            self.tea_dict = {}



    def get_teas(self, tea_pages_to_scrape=1):
        """Scrapes tea names, brands, and URLs from Steepster tea overview page.

        Parameters
        ----------
        tea_pages_to_scrape : int, optional
            The number of pages to scrape (default is 1)
            There are 28 teas per page

        """
        for i in range(1,tea_pages_to_scrape+1):

            # Creates driver that works with the latest version of Chrome
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(f'https://steepster.com/teas?page={i}&sort=popular')

            tea_xpath = "//div[@class='product tea']//div[@class='tea']"

            tea_root =  driver.find_elements_by_xpath(tea_xpath)

            for tea in tea_root:

                # tea_info = []

                # Tea Name
                # Not sure why I don't need this xpath, leaving it here for now
                # tea_name_xpath = ".//a[@class='tea-name']"
                # tea_name = tea.find_element_by_xpath(tea_name_xpath)

                # for tea in tea_name:
                nb = tea.text.split('\n')
                name = nb[0]

                # Check if tea is already in tea_dict
                if name in self.tea_dict.keys():
                    print(f'{name} skipped. Already in tea_dict.')
                    pass
                else:
                    self.tea_dict[name] = {}
                    print('name:', name)

                    brand = nb[1]
                    self.tea_dict[name]['brand'] = brand
                    print('brand:', brand)

                    tea_link = tea.get_attribute("href")
                    self.tea_dict[name]['url'] = tea_link

                    # Tea Rating
                    tea_rating_xpath = ".//div[contains(@class, 'tea-rating')]"
                    tea_rating = tea.find_element_by_xpath(tea_rating_xpath)

                    # for tea in tea_rating:
                    rating = int(tea_rating.text)
                    self.tea_dict[name]['rating'] = rating

            driver.quit()

        return self.tea_dict



    def get_reviews(self, min_review_pgs=1):
        """Gets reviewer names and ratings for each tea.

        A new is added to each tea's entry in the tea dict. The key is
        'reviewers', and the value is a dictionary of reviewers and their 
        respective ratings of that tea.

        If a tea is already in the tea dict, the function will start adding 
        reviews from the page where it left of last time.

        Parameters
        ----------
        min_rating_pages : int, optional
            The number of pages to scrape. (default is 1)
        
        """

        driver = webdriver.Chrome(ChromeDriverManager().install())

        for tea in self.tea_dict.keys():

            print('Current tea:',tea)

            # Find out how many review pages a tea has
            tea_url = self.tea_dict[tea]['url']

            # driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(f'{tea_url}?page=1#tasting-notes')
            time.sleep(1)

            pages_xpath = "//nav[@class='pagination']//ul//li[last()-1]//a"
            max_pages = driver.find_elements_by_xpath(pages_xpath)
            for page in max_pages:
                max_review_pgs = int(page.text)
                self.tea_dict[tea]['review_pages'] = max_review_pgs
            
            # Check to see if the tea already has reviewers
            if 'reviewers' in self.tea_dict[tea].keys():
                review_count = len(self.tea_dict[tea]['reviewers'].keys())
                start_page = int(ceil(review_count/10))
                print('start page:', start_page)
                print(f'{tea} has {review_count} existing reviews.')
            else:
                self.tea_dict[tea]['reviewers'] = {}
                review_count = 0
                start_page = 1
                print(f'{tea} has no existing reviews.')

            end_page = min(min_review_pgs+1,max_review_pgs)

            # Scrape reviewers and ratings
            for i in range(start_page, end_page):

                if i == start_page:
                    print(f'Adding new reviews starting on page {start_page}.')

                # Only need this for >1 because we are already on the page
                if i > 1:
                    driver.get(f'{tea_url}?page={i}#tasting-notes')

                all_user_elements = []

                user_div = driver.find_elements_by_xpath("//div[@class='user']")

                for user in user_div:

                    user_info = []

                    # Reviewer
                    re_xpath = ".//span[@itemprop='author']//a[@itemprop='url']"
                    r = user.find_element_by_xpath(re_xpath)
                    r_url = r.get_attribute('href')
                    reviewer = re.search(r"(?<=\.com\/).*", r_url)
                    user_info.append(reviewer.group(0))

                    # Rating
                    try:
                        ra_xpath = """.//div[@itemprop='reviewRating']
                                       //span[@itemprop='ratingValue']"""
                        r = user.find_element_by_xpath(ra_xpath)
                        rating = int(r.text)
                        user_info.append(rating)
                    except NoSuchElementException:
                        pass

                    if len(user_info) == 2:
                        all_user_elements.append(user_info)
                        self.tea_dict[tea]['reviewers'][user_info[0]] = {}
                        (self.tea_dict[tea]['reviewers'][user_info[0]]
                            ['weight']) = user_info[1]

            new_review_count = len(self.tea_dict[tea]['reviewers'].keys())
            reviews_added = new_review_count - review_count

            print(f'Previous review count: {review_count}')
            print(f'New review count: {new_review_count}')
            print(f'{reviews_added} reviews added to {tea}')

            # driver.quit()
                
            time.sleep(0.5)

            print(tea,'complete')
            print('-----------------------\n')
        driver.quit()

    def save_tea_dict(self,filename='tea_dict',filetype='p'):
        """Pickle the tea_dict data for later use. Pickled tea - yum...
        
        Parameters
        ----------

        filename : str
            Name assigned to the saved file.
            
        filetype : str       
            Extension you want appended to the file. Default is 'p' for pickle.

        """
        with open(f"..\\data\pickled-data\\{filename}.{filetype}", "wb") as p:
            pickle.dump(self.tea_dict, p)