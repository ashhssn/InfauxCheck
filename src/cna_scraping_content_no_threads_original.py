import time
import csv
import requests
import pandas as pd
import os
from fake_useragent import UserAgent
import random 
import datetime
from ftfy import fix_text

# Selenium Modules
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException,ElementNotInteractableException

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
    options.add_argument("--headless")
    driver =  webdriver.Chrome(options=options)

    return driver

def reset_driver():
    new_driver = driver_setup()
    return new_driver

# Normally start_article_id = 0 , since we start from 0
def get_article_contents(driver, start_article_id):
    df_articles_url = pd.read_csv("articles_url.csv")
    articles_url = df_articles_url["article_url"]
    articles_ids = df_articles_url["article_id"]

    for i in range(start_article_id,5474):
        # For Testing Purpose
        article_url = articles_url[i]
        article_id = articles_ids[i]

        retry_count = 0
        max_retries = 3 # Change From 5 to 3, To Speed Up
        # Solving The Timeout Error 
        while retry_count < max_retries:
            try:
                driver.get(article_url)
                driver.implicitly_wait(10)
                break
            except TimeoutException as e:
                print(f"TimeoutError! for {article_url}: Restarting WebDriver and retrying, The error is : {e}")
                retry_count += 1
                driver.quit()
                driver = reset_driver()
                time.sleep(5)
            
        if retry_count == max_retries:
            print(f"Article Id: {article_id} after {max_retries} failed attempts, skipping to the next link")
            with open("failed_articles_extraction.log", "a") as f:  # Log failed articles for review
                f.write(f"{article_id},{article_url}\n")
            continue  # Move to next article if it keeps failing, will not run the below code anymore

        try:
            content_wrapper_elements = driver.find_elements(By.XPATH,"//div[contains(@class,'content-wrapper')]")
        except NoSuchElementException:
            print("No Content Wrapper Elements")

        article_headline = df_articles_url["article_headline"][start_article_id]
        article_whole_text = []
        print("I am currenting scraping article:", article_headline)
        if len(content_wrapper_elements) > 0 :
            # print("Content Wrapper Total:", len(content_wrapper_elements))
            for content_wrapper in content_wrapper_elements:
                try:
                    text_contents = content_wrapper.find_elements(By.XPATH, ".//div[contains(@class,'text')]//div[contains(@class,'text-long')]")
                except NoSuchElementException:
                    print("No Such Text Contents")
                # print("Text Contents Total:", len(text_contents))
                if len(text_contents) > 0 :
                    for text_content in text_contents:
                        article_whole_text.append(text_content.text)
                        # print(text_content.text, "\n")

        article_short_description_element = driver.find_elements(By.XPATH,"//div[contains(@class,'content-detail__description')]")
        if len(article_short_description_element) > 0:
            article_short_description = fix_text(article_short_description_element[0].text)
        else:
            print("No Article Short Description")
            article_short_description = ""

        article_author_element = driver.find_elements(By.XPATH,"//a[contains(@class,'h6__link')]")
        if len(article_author_element) > 0:
            article_author_link = article_author_element[0].get_attribute("href")
        else:
            article_author_link = ""
            print("No Article Author Link")
        
        article_author_element = driver.find_elements(By.XPATH,"//a[contains(@class,'h6__link')]")
        if len(article_author_element) > 0:
            article_author_name = article_author_element[0].get_attribute("innerText")
        else:
            article_author_name = ""
            print("No Article Author Name")

        article_datetime_element = driver.find_elements(By.XPATH,"//div[contains(@class,'article-publish article-publish--')]")
        if len(article_datetime_element) > 0:
            article_datetime_published = article_datetime_element[0].text
        else:
            article_datetime_published = ""
            print("No Article Date Time Published")

        
        # DateTime
        current_datetime = datetime.datetime.now()
        formatted_current_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        # print(f'article_headline: {article_headline}, article_link: {article_url}, article_datetime_released' , {article_datetime_released})

        article_text = fix_text("\n\n".join(article_whole_text))

        # Save and Update the csv 
        new_article_content_df = pd.DataFrame({
            "article_id" : [article_id],
            "article_headline" : [article_headline],
            "article_short_description" : [article_short_description],
            "article_text" : [article_text], 
            "article_url" : [article_url], 
            "article_author_name" : [article_author_name], 
            "article_author_link" : [article_author_link], 
            "article_datetime_published" : [article_datetime_published],
            "datetime_crawled" : [formatted_current_datetime]
        })

        new_article_content_df.to_csv("articles_content.csv", mode='a', header=False, index=False)
        # counter += 1
        start_article_id += 1

        sleep_time = generate_random_waiting_time()
        print("I Am Currently Sleeping ...",sleep_time)
        time.sleep(sleep_time)

def file_exists_check():
    articles_url_csv_path = current_directory + "/articles_content.csv"
    if os.path.isfile(articles_url_csv_path):
        print("File Indeed Exists")
    else:
        # Creating an empty DataFrame without specifying data types
        df = pd.DataFrame(columns=['article_id', 'article_headline', 'article_short_description',
                                   'article_text', 'article_url', 'article_author_name', 
                                   'article_author_link','article_datetime_released', 
                                   'datetime_crawled'])
        df.to_csv("articles_content.csv", index=False, encoding="utf-8")
        return "File Does Not Exists , So File Creation Completed"

# Random delay between 18-25 seconds , To 10-15 seconds 
def generate_random_waiting_time():
    return random.uniform(1, 3)

def main():
    file_exists_check()
    content_driver = driver_setup()
    print("Starting article content extraction...")
    # Pass the value 0 if you are start from the top, id = 0, because my program stops after scraping 264 rows, i want 265th row , index 264 -> 265th row
    get_article_contents(content_driver,5473)

    content_driver.quit()
    print("Scraping Completed Successfully!")
 
if __name__ == "__main__":
    main()