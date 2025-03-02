import time
import csv
import requests
import pandas as pd
import os
from fake_useragent import UserAgent
import random 
import datetime
from ftfy import fix_text

# For Multi-Threading
from concurrent.futures import ThreadPoolExecutor

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
def get_article_contents(thread_id ,start_article_id, end_article_id):
    df_articles_url = pd.read_csv("articles_url.csv")
    articles_url = df_articles_url["article_url"]
    articles_ids = df_articles_url["article_id"]
    driver = driver_setup()

    number_of_tasks = end_article_id - start_article_id
    tasks_completed = 0
    for i in range(start_article_id,end_article_id):
        # For Testing Purpose
        article_url = articles_url[i]
        article_id = articles_ids[i]

        retry_count = 0
        max_retries = 2 # Change From 5 to 2, To Speed Up
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
                time.sleep(4)
            
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
    
        start_article_id += 1
        tasks_completed += 1

        print(f"[Thread: {thread_id}] Done Appending {article_headline}) To CSV , Article ID {start_article_id}")
        if tasks_completed >= number_of_tasks:
            break  # Stop thread when it finishes assigned tasks

        sleep_time = generate_random_waiting_time()
        print("I Am Currently Sleeping ...",sleep_time)
        time.sleep(sleep_time)
    
    driver.quit()
    print(f"[Thread: {thread_id}] Completed all tasks ({tasks_completed}/{number_of_tasks}) and is stopping.")

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
        # encoding="utf-8-sig" , this forces excel to read as utf-8 , solve the problem for the encoding because now the windows system read as cp-1252
        return "File Does Not Exists , So File Creation Completed"

# Random delay timer generator function , starting was between 20-30 seconds , To 1-3 seconds (Actually the program run quite slow and which result the request of the web page slows down too, thus low sleeping/waiting time)
def generate_random_waiting_time():
    return random.uniform(1, 3)

def main():
    file_exists_check()

    num_of_threads = 5  
    # Should start From 0...Some Number, then split the rows/tasks into few parts
    thread_ranges = [
        (1, 994, 2504),
        (2, 2504, 4014),
        (3, 4014, 5524),
        (4, 5524, 7034),
        (5, 7034, 8544)
    ]

    with ThreadPoolExecutor(max_workers=num_of_threads) as executor:
        for thread_id, start_id, end_id in thread_ranges:
            executor.submit(get_article_contents, thread_id, start_id, end_id)
    
    print("Scraping Job Is Done!")
 
if __name__ == "__main__":
    main()

"""
    Learning Points:
    https://docs.python.org/3/library/concurrent.futures.html
    Do Take Note: That ThreadPoolExecutor is not recommended for long running tasks, sometimes the Thread just
    die out without you knowing. Luckily, there is an indication of each thread workload (the indexs), then we can change the number accordingly.
    But this is not a good approach. To enchance this code:
    1. Do not let your ThreadPoolExecutor work for too long , If not they play MIA. 
        Maybe can put 50 indexes, after finishing the task, destroy the thread and make new one
        This way we can ensure that everything will run more smoothly
    2. Check whether the thread is stuck/dead, by using try/except : https://stackoverflow.com/questions/61777917/python-threadpoolexecutor-threads-not-finishing
        Since the scraping is going to end already, I did not implement, but the idea is above the link


    Selenium Scraping is generally slower than other scraping libraries framework I believe. Beautiful Soup Or Scrapy might be a better choice for static information like the cna website.
    But for scraping the urls, selenium is needed, to simulate the user click button        
"""