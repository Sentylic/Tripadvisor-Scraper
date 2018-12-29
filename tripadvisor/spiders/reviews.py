# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from pprint import pprint
from scrapy.selector import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class wait_for_load(object):
    def __init__(self,old):
        self.old = old
    def __call__(self, driver):
        element = driver.find_element_by_xpath("//div[@class='review-container']")   # Finding the referenced element
        if self.old != element.text:
            return element
        else:
            return False

class ReviewsSpider(scrapy.Spider):
    name = "reviews"
    allowed_domains = ["tripadvisor.com"]
    start_urls = (
        # 'https://www.tripadvisor.com/Attraction_Review-g304141-d317483-Reviews-Citadel_of_Sigiriya_Lion_Rock-Sigiriya_Central_Province.html',
        # 'https://www.tripadvisor.com/Attraction_Review-g616035-d2478367-Reviews-Little_Adam_s_Peak-Ella_Uva_Province.html',
        'https://www.tripadvisor.com/Attraction_Review-g304141-d4782530-Reviews-Sigiriya_World_Heritage_Site-Sigiriya_Central_Province.html',
    )

    def __init__(self):
        self.driver = webdriver.Firefox()

    def parse(self, response):
        self.driver.get(response.url)
        next_page = self.driver.find_element_by_xpath('//div[@class="pageNumbers"]/a[contains(@class,"current")]/following-sibling::a[1]')
        while next_page is not None:
            more = self.driver.find_elements_by_xpath("//p[@class='partial_entry']/span")
            for x in range(0,len(more)):
                try:
                    more[x].click()
                except:
                    pass
            try:
                wait = WebDriverWait(self.driver, 20)
                element = wait.until(EC.text_to_be_present_in_element((By.XPATH,"//div[@class='entry']/span"),"Show less"))
            finally:
                res = Selector(text=self.driver.page_source)

            for idx,review in enumerate(res.css('div.review-container')):
                yield {
                    'place_name': response.css('h1.heading_title::text').extract_first(),
                    'tagline': review.css('span.noQuotes::text').extract_first(),
                    'review_title': review.css('span.noQuotes::text').extract_first(),
                    'review_body': review.css('p.partial_entry::text').extract_first(),
                    'review_date': review.xpath('//*[@class="ratingDate"]/@title')[idx].extract(),
                    'num_reviews_reviewer': review.css('span.badgetext::text').extract_first(),
                    'reviewer_name': review.css('span.scrname::text').extract_first(),
                    'bubble_rating': review.xpath("//div[contains(@class, 'review-container')]//span[contains(@class, 'ui_bubble_rating')]/@class")[idx].re(r'(?<=ui_bubble_rating bubble_).+?(?=0)')
                }

            next_page.click()
            try:
                wait2= WebDriverWait(self.driver, 20)
                element2 = wait2.until(wait_for_load(self.driver.find_element_by_xpath("//div[@class='review-container']").text))
            except:
                pass
            try:
                next_page = self.driver.find_element_by_xpath('//div[@class="pageNumbers"]/a[contains(@class,"current")]/following-sibling::a[1]')
            except:
                pass
        self.driver.close()
