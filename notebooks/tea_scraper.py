from math import ceil
from os.path import exists
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


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

        A new dictionary is added to each tea's entry in the tea dict. The key
        is 'reviewers', and the value is a dictionary of reviewers and their 
        respective ratings of that tea.

        If a tea is already in the tea dict, the function will start adding 
        reviews from the page where it left off last time.
    
    get_max_pages(self, tea_id, driver):
        Gets the total number of review pages for a tea if the tea doesn't
        already have a 'review_pages' dictionary entry.

    check_existing_reviews(self, tea_id):
        Check to see if a tea has a 'reviewers' dictionary entry. If not,
        creates one.

    count_teas_with_flavors(self):
        Counts the number of teas that have the 'flavors' subdict key
    
    get_flavors(self, num_teas=2):
        Gets flavor list for each tea
    
    search_url(self, data, url):
        Look for provided URL among existing tea URLs in the tea_dict

    add_individual_tea(self,url):
        Add specific tea to tea_dict if it isn't already there.

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

        self.driver_options = Options()
        self.driver_options.headless = True


    def get_teas(self, tea_pages_to_scrape=1):
        """Scrapes tea names, brands, and URLs from Steepster tea overview page.

        The function picks up on the page it left off on last time. For example,
        if you had scraped 42 teas and there are 28 on a page, then that means
        you stopped on page 2. The function will round up to the nearest integer
        (42/28 = 1.5), so you'll start on page 2. There is some redundancy, but 
        it's better than starting from page 1 every time.

        Note: This function will work well as long as the teas don't move around
        often. If they are often shuffled, then you'll need to write a function
        like the user_dict that pulls from an ever-growing list of URLs. Even 
        that would be challenging if the teas are moving around a lot. Just get
        going and hope things don't change too much by the time you finish :) 

        Parameters
        ----------
        tea_pages_to_scrape : int, optional
            The number of pages to scrape (default is 1)
            There are 28 teas per page

        """
        driver = webdriver.Chrome(ChromeDriverManager().install(),
                                  options=self.driver_options)

        # Find out how many tea pages there are
        driver.get(f'https://steepster.com/teas?sort=popular')
        pages_xpath = "//nav[@class='pagination']//ul//li[last()-1]//a"
        max_pages = driver.find_elements(By.XPATH,pages_xpath)
        for page in max_pages:
            max_tea_pages = int(page.text)
        
        total_teas_scraped = len(self.tea_dict.keys())

        start_page = int(ceil(total_teas_scraped/28))+1
        end_page = start_page + min(tea_pages_to_scrape+1, max_tea_pages)

        # print(start_page)
        # print(end_page)

        for i in range(start_page,end_page):

            driver.get(f'https://steepster.com/teas?page={i}&sort=popular')

            tea_xpath = "//div[@class='product tea']" #//div[@class='tea']"

            tea_root =  driver.find_elements(By.XPATH,tea_xpath)

            for tea in tea_root:

                tea_id = tea.get_attribute("id")

                tea_details = tea.find_element(By.CLASS_NAME, 'tea')
    
                nb = tea_details.text.split('\n')
                name = nb[0]
                # print(nb)

                # Check if tea is already in tea_dict
                if name in self.tea_dict.keys():
                    # print(f'{name} skipped. Already in tea_dict.')
                    pass
                else:
                    # Add new tea to tea_dict
                    self.tea_dict[tea_id] = {}

                    # Add tea name to tea entry
                    self.tea_dict[tea_id]['name'] = name
                    # print('name:', name)

                    # Add brand to tea entry
                    brand = nb[1]
                    self.tea_dict[tea_id]['brand'] = brand
                #     # print('brand:', brand)

                    # Add tea URL to tea entry
                    # tea_link = tea.find_element(By.TAG_NAME,'a').get_attribute("href")
                    tea_link = tea.find_element(By.CLASS_NAME,'tea-name').get_attribute("href")
                    # tea_link = tea.find_element(By.CLASS_NAME,'entry-count').get_attribute("href")
                    # tea_link = tea.get_attribute("href")
                    # print(f"This is the tea link: {tea_link}")
                    self.tea_dict[tea_id]['url'] = tea_link

                    # Add overall rating to tea entry
                    tea_rating_xpath = ".//div[contains(@class, 'tea-rating')]"
                    tea_rating = tea.find_element(By.XPATH,tea_rating_xpath)
                    rating = int(tea_rating.text)
                    self.tea_dict[tea_id]['rating'] = rating

        driver.quit()

    def get_max_pages(self, tea_id, driver):
        """Gets the total number of review pages for a tea if the tea doesn't
        already have a 'review_pages' dictionary entry.

        Parameters
        ----------
        tea_id : str
            Tea ID for a tea in the dictionary. ID is used to call correct URL.
        """
        try:
            if self.tea_dict[tea_id]['review_pages']:
                print(self.tea_dict[tea_id]['name'], ' already has review_pages')
        except:
            tea_url = self.tea_dict[tea_id]['url']
            
            driver.get(f'{tea_url}?page=1#tasting-notes')

            pages_xpath = "//nav[@class='pagination']//ul//li[last()-1]//a"
            max_pages = driver.find_elements(By.XPATH,pages_xpath)
            for page in max_pages:
                max_review_pgs = int(page.text)
                self.tea_dict[tea_id]['review_pages'] = max_review_pgs
            print(f"{self.tea_dict[tea_id]['name']} has {max_review_pgs} review_pages")


    def check_existing_reviews(self, tea_id):
        """Check to see if a tea has a 'reviewers' dictionary entry. If not,
        creates one.

        Parameters
        ----------
        tea_id : str
            Tea ID for a tea in the dictionary. ID is used to call correct URL.
        
        Returns
        -------
        review_count : int
            Total reviews already logged
        
        start_page : int
            Page where review scraper should start collecting more reviews
        """

        # if the tea has reviews, calculate appropriate start page
        try:
            if self.tea_dict[tea_id]['reviewers']:
                review_count = len(self.tea_dict[tea_id]['reviewers'].keys())
                start_page = int(ceil(review_count/10))+1
                print('start page:', start_page)
                print(f'{tea_id} has {review_count} existing reviews.')
        # if the tea has no reviews, create 'reviewers' dictionary
        except:
            self.tea_dict[tea_id]['reviewers'] = {}
            review_count = 0
            start_page = 1
            print(f'{tea_id} has no existing reviews.')
        
        return review_count, start_page


    def get_reviews(self, num_teas=1, review_pgs=1):
        """Gets reviewer names and ratings for each tea.

        A new dictionary is added to each tea's entry in the tea dict. The key
        is 'reviewers', and the value is a dictionary of reviewers and their 
        respective ratings of that tea.

        If a tea is already in the tea dict, the function will start adding 
        reviews from the page where it left off last time.

        Note: Reviews submitted without ratings are given a score of 1000. This
        will need to be adjusted or excluded later.

        Parameters
        ----------
        num_teas : int
            The number of teas to scrape (default is 1)

        review_pgs : int
            The number of review pages to scrape (default is 1)
        
        """

        driver = webdriver.Chrome(ChromeDriverManager().install(),
                                  options=self.driver_options)

        i = 0
        while i < num_teas:
            all_teas = list(self.tea_dict.keys())
            tea_id = all_teas[i]
            print(tea_id)
            # current_tea is a tea ID number

            # make sure tea has review_pages attribute
            self.get_max_pages(tea_id=tea_id, driver=driver)

            review_count, start_page = self.check_existing_reviews(tea_id)

            max_review_pgs = self.tea_dict[tea_id]['review_pages']
            min_review_pgs = start_page + review_pgs
            end_page = min(min_review_pgs, max_review_pgs)

            # what happens when a tea has all the ratings scraped?
            if start_page >= max_review_pgs:
                num_teas += 1
            else:
            # Scrape reviewers and ratings
                for j in range(start_page, end_page):

                    if j == start_page:
                        print(f'Adding new reviews starting on page {start_page}.')

                    # Only need this for >1 because we are already on the page
                    if j > 1:
                        tea_url = self.tea_dict[tea_id]['url']
                        driver.get(f'{tea_url}?page={j}#tasting-notes')

                    all_user_elements = []

                    user_div = driver.find_elements(By.XPATH,"//div[@class='user']")

                    for user in user_div:

                        user_info = []

                        # Reviewer
                        re_xpath = ".//span[@itemprop='author']//a[@itemprop='url']"
                        r = user.find_element(By.XPATH,re_xpath)
                        r_url = r.get_attribute('href')
                        reviewer = re.search(r"(?<=\.com\/).*", r_url)
                        user_info.append(reviewer.group(0))

                        # Rating
                        try:
                            ra_xpath = """.//div[@itemprop='reviewRating']
                                        //span[@itemprop='ratingValue']"""
                            r = user.find_element(By.XPATH,ra_xpath)
                            rating = int(r.text)
                            user_info.append(rating)
                        except NoSuchElementException:
                            rating = 1000
                            user_info.append(rating)

                        if len(user_info) == 2:
                            all_user_elements.append(user_info)
                            self.tea_dict[tea_id]['reviewers'][user_info[0]] = {}
                            (self.tea_dict[tea_id]['reviewers'][user_info[0]]
                                ['weight']) = user_info[1]

                new_review_count = len(self.tea_dict[tea_id]['reviewers'].keys())
                reviews_added = new_review_count - review_count

                print(f'Previous review count: {review_count}')
                print(f'New review count: {new_review_count}')
                print(f'{reviews_added} reviews added to {tea_id}')

                print(tea_id,'complete')
            print('-----------------------\n')
            i += 1

        driver.quit()

    
    def count_teas_with_flavors(self):
        """Counts the number of teas that have the 'flavors' subdict key
        """
        count = 0
        for key in self.tea_dict:
            try:
                if self.tea_dict[key]['flavors']:
                    count += 1
            except:
                pass
        return count


    def get_flavors(self, num_teas=2):
        """Gets flavor list for each tea    

        ...

        Parameters
        ----------
        num_teas : int
            Number of teas you'd like to scrape flavors for. Default is 2
        """

        tea_ids = list(self.tea_dict.keys())
        teas_with_flavors = self.count_teas_with_flavors()
        max_teas_to_scrape = len(tea_ids) - teas_with_flavors

        # print(len(self))
        # print(teas_with_flavors)
        # print(max_teas_to_scrape)

        num_to_scrape = min(num_teas,max_teas_to_scrape)

        if num_to_scrape == 0:
            return "All teas previously scraped. Run get_teas to add more"

        driver = webdriver.Chrome(ChromeDriverManager().install(),
                                  options=self.driver_options)

        i = 0

        while i < num_to_scrape:

            current_tea = tea_ids[i]

            if 'flavors' in self.tea_dict[current_tea].keys():
                i += 1
                num_to_scrape += 1
            
            else:
                print('Current tea:',current_tea)
                tea_url = self.tea_dict[current_tea]['url']
                driver.get(f'{tea_url}?page=1')

                flavor_str = driver.find_element(By.XPATH,"//dl[@class='tea-description']/dt[text() = 'Flavors']/following-sibling::dd").text
                flavor_list = flavor_str.split(', ')
                self.tea_dict[current_tea]['flavors'] = flavor_list

                i += 1

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
        """Add specific tea to tea_dict if it isn't already there.

        Parameters
        ----------

        url : str
            URL you would like to check for in the tea_dict
        """
        already_in_dict_check = self.search_url(data=self.tea_dict,url=url)
        
        if already_in_dict_check == True:
            print("This tea is already in the tea dictionary.")
        else:
            print('Adding new tea to the tea dictionary...')
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(url)

            time.sleep(1)

            driver.quit()


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