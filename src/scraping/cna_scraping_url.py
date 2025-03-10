import time
import csv
import requests
import pandas as pd
import os
from fake_useragent import UserAgent
import random 
import datetime

# Selenium Modules
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException,ElementNotInteractableException

base_url = "https://www.channelnewsasia.com/singapore"
current_directory = os.getcwd()

def driver_setup():
    options = Options()
    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('window-size=1920,1080')
    options.add_argument("--disable-gpu")  # Fixes GPU rendering issues
    # options.add_experimental_option("detach", True)
    # Don't show browser when scraping , will be faster
    # options.add_argument("--headless")
    driver =  webdriver.Chrome(options=options)

    return driver

# Get all the articles from top stories url

# Get all the articles from more stories url
def get_more_stories_urls(driver):
    block_articles_section_count = 1
    article_id = 1
    driver.get(base_url)

    while True: # Can Change To While Loop, This for testing currently
        # When you click "View More" Button , it will come out one block by block amount of articles
        # When we click "View More" , the counter will + 1
        view_more_button_avaliable = True
        try:
            view_more_button = driver.find_element(By.XPATH, "//button[contains(@class,'button button--view-more-stories')]")
        except NoSuchElementException:
            view_more_button_avaliable = False
            print("No Such View Button Avaliable")
        
        # If there is view more button then we continue , else just stop the program
        if view_more_button_avaliable:
        # This Help With The Clicking
            driver.execute_script('arguments[0].click()', view_more_button)
        else:
            break

        try: 
            block_articles_section = driver.find_elements(By.XPATH,"//div[contains(@class,'grid-cards-four-column grid-card-carousel-mobile')]")[block_articles_section_count]
        except NoSuchElementException:
            print("No Block Articles Sections Avaliable On The Current Index", block_articles_section_count)

        try:
            card_objects = block_articles_section.find_elements(By.CLASS_NAME,"card-object")
        except NoSuchElementException:
            print("No Card Objects")

        if len(card_objects) > 0:
            for card in card_objects:
                article_headline = card.find_element(By.XPATH,".//div[contains(@class,'card-object__content')]//div[contains(@class,'card-object__body')]//div[contains(@class,'list-object')]//h6[contains(@class,'h6 list-object__heading')]//a[@class='h6__link list-object__heading-link']").get_attribute("innerText")
                article_url = card.find_element(By.XPATH,".//div[contains(@class,'card-object__content')]//div[contains(@class,'card-object__body')]//div[contains(@class,'list-object')]//h6[contains(@class,'h6 list-object__heading')]//a[@class='h6__link list-object__heading-link']").get_attribute("href")
                article_datetime_released = card.find_element(By.XPATH,".//div[contains(@class,'card-object__content')]//div[contains(@class,'card-object__body')]//div[contains(@class,'list-object')]//div[contains(@class,'list-object__datetime-duration')]").get_attribute("innerText")

                # DateTime
                current_datetime = datetime.datetime.now()
                formatted_current_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                # print(f'article_headline: {article_headline}, article_link: {article_url}, article_datetime_released' , {article_datetime_released})
        
                # Save and Update the csv 
                new_article_url = pd.DataFrame({
                    "article_id" : [article_id],
                    "article_headline" : [article_headline],
                    "article_url" : [article_url], 
                    "article_datetime_released" : [article_datetime_released],
                    "datetime_crawled" : [formatted_current_datetime]

                })

                new_article_url.to_csv("articles_url.csv", mode='a', header=False, index=False)
                article_id += 1

            block_articles_section_count += 1
            # Stop The Code From running too fast, later blacklist toh, we don't want the server to overload
           
            sleep_time = generate_random_waiting_time()
            print("I Am Currently Sleeping ...",sleep_time)
            time.sleep(sleep_time)

# Random delay between 20-30 seconds
def generate_random_waiting_time():
    return random.uniform(20, 30)

def file_exists_check():
    articles_url_csv_path = current_directory + "/articles_url.csv"
    if os.path.isfile(articles_url_csv_path):
        print("File Indeed Exists")
    else:
        # Creating an empty DataFrame without specifying data types
        df = pd.DataFrame(columns=['article_id', 'article_headline', 'article_url', 'article_datetime_released', 'datetime_crawled'])
        df.to_csv("articles_url.csv", index=False, encoding="utf-8")
        return "File Does Not Exists , So File Creation Completed"

def main():
    file_exists_check()
    urls_driver = driver_setup()
    print("Starting article urls extraction...")
    get_more_stories_urls(urls_driver)

    urls_driver.quit()
    print("Scraping Completed Successfully!")
 
if __name__ == "__main__":
    main()