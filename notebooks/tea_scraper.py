# Purpose of this class:
## Gather tea names, links, overall ratings - DONE
## Get initial reviewer and rating data for teas - DONE
## Continue updating adding reviewers to teas with no reviewers - DONE
## Update existing teas if/when they have new reviews - DONE
## Update a specific tea

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
        Pickles the tea_dict data for later use.
    
    """



    def __init__(self):
        """
        Initializes the TeaDict class with existing data or an empty dictionary
            if no previous data exists.

        ...

        Attributes
        ----------
        tea_dict : dict
            Either an existing tea dictionary or newly initialized empty dict.


        """
        tea_dict_exists = exists('..\\data\\pickled-data\\tea_dict.p')
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
        driver = webdriver.Chrome(ChromeDriverManager().install())

        # Find out how many tea pages there are

        pages_xpath = "//nav[@class='pagination']//ul//li[last()-1]//a"
        max_pages = driver.find_elements_by_xpath(pages_xpath)
        for page in max_pages:
            max_tea_pages = int(page.text)
        
        total_teas_scraped = len(self.tea_dict.keys())

        start_page = int(ceil(total_teas_scraped/28))
        end_page = min(tea_pages_to_scrape+1, max_tea_pages)

        for i in range(start_page,end_page):

            driver.get(f'https://steepster.com/teas?page={i}&sort=popular')

            tea_xpath = "//div[@class='product tea']//div[@class='tea']"

            tea_root =  driver.find_elements_by_xpath(tea_xpath)

            for tea in tea_root:

                nb = tea.text.split('\n')
                name = nb[0]

                # Check if tea is already in tea_dict
                if name in self.tea_dict.keys():
                    print(f'{name} skipped. Already in tea_dict.')
                    pass
                else:
                    # Add tea name to tea_dict
                    self.tea_dict[name] = {}
                    print('name:', name)

                    # Add brand to tea entry
                    brand = nb[1]
                    self.tea_dict[name]['brand'] = brand
                    print('brand:', brand)

                    # Add url to tea entry
                    tea_link = tea.get_attribute("href")
                    self.tea_dict[name]['url'] = tea_link

                    # Add overall rating to tea entry
                    tea_rating_xpath = ".//div[contains(@class, 'tea-rating')]"
                    tea_rating = tea.find_element_by_xpath(tea_rating_xpath)
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
        reviews from the page where it left off last time.

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
    

    
    def add_individual_tea(self,url):
        already_in_dict_check = self.search_url(data=self.tea_dict,url=url)
        
        if already_in_dict_check == True:
            print("This tea is already in the tea dictionary.")
        else:
            print('Adding new tea to the tea dictionary...')
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(url)

            time.sleep(3)

            driver.quit()




        # Check if provided URL is in the list of urls in the tea dict - DONE
        # Create driver - DONE
        # Go to provided URL - DONE
        # Get name (h1)
        # Check if name exists
        # brand, url, and aggregate rating

    def search_url(self, data, url):
        """Look for provided URL among existing tea URLs in the tea_dict

        Parameters
        ----------

        data : dict
            The tea_dict should be provided.
        
        url : str
            URL you would like to check for in the tea_dict
        
        Note: This is a recursive function, so the data parameter will change
            with each recursion of the function. That's why I added the data
            parameter instead of just using self.tea_dict.
        
        Source: https://stackoverflow.com/questions/50698390
            /find-a-key-if-a-value-exists-in-a-nested-dictionary
        """
        for a, b in data.items():
            if url in str(b):
                return True
            if isinstance(b, dict):
                return self.search_url(b, url)
    

    #         # else:
    #             print(f'{url} is not in the tea dictionary yet. Add it!')
            

    # def get_keys(d, to_find):
    #     for a, b in d.items():
    #         if to_find in b:
    #         yield a
    #         if isinstance(b, dict):
    #         yield from get_keys(b, to_find)
