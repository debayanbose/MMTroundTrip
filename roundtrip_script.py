# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 10:30:51 2020

@author: debayan.bose
"""
import csv
import selenium.webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
#from multiprocessing.pool import ThreadPool, Pool
#import threading
from selenium import webdriver
#from multiprocessing import Process
#import multiprocessing
import time
import warnings
import datetime
from dateutil.rrule import rrule, DAILY
#import config
import pandas as pd
import numpy as np
from pymongo import MongoClient 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options



warnings.filterwarnings("ignore", category=UserWarning, module='bs4')


def get_driver():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, executable_path=r'C:/D Backup/geckodriver.exe')
    return driver


def scrape_round(url):
        driver=get_driver()
        driver.get(url)
        time.sleep(10)
        for j in range(1,50):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
          			 # URL requested in browser.
        element_depart =driver.find_elements_by_xpath("//div[@class='splitVw-sctn pull-left']//label[@class='splitVw-radio clearfix cursor_pointer ']")
        
        depart_flight = []
        for i in range(len(element_depart)):
            flight_info = element_depart[i].text.split('\n')[0]
            stop_info = element_depart[i].text.split('\n')[4]
            selection_id = element_depart[i].get_attribute("for")
            depart_flight.append([flight_info,stop_info ,selection_id])
            
        element_return =driver.find_elements_by_xpath("//div[@class='splitVw-sctn pull-right']//label[@class='splitVw-radio clearfix cursor_pointer ']")
        
        return_flight = []
        for i in range(len(element_return)):
            flight_info = element_return[i].text.split('\n')[0]
            stop_info = element_return[i].text.split('\n')[4]
            selection_id = element_return[i].get_attribute("for")
            return_flight.append([flight_info,stop_info ,selection_id])
        
        return_flight_pd = pd.DataFrame(return_flight)
        return_flight_pd.columns = ['FlightName','DSTOP','ID']
        depart_flight_pd = pd.DataFrame(depart_flight)
        depart_flight_pd.columns = ['FlightName','DSTOP','ID']
        return_flight_pd_ns = return_flight_pd[return_flight_pd['DSTOP']=='Non stop']
        depart_flight_pd_ns = depart_flight_pd[depart_flight_pd['DSTOP']=='Non stop']
        
        depart_flight_pd_ns = pd.concat([depart_flight_pd_ns, depart_flight_pd_ns['FlightName'].str.split('|', expand=True)[0]],axis=1)
        depart_flight_pd_ns.columns =  ['Depart_FlightName','Depart_DSTOP','Depart_ID','Carrier']  
        
        return_flight_pd_ns = pd.concat([return_flight_pd_ns, return_flight_pd_ns['FlightName'].str.split('|', expand=True)[0]],axis=1)
        return_flight_pd_ns.columns =  ['Return_FlightName','Return_DSTOP','Return_ID','Carrier']  
        
        final_data = pd.merge(return_flight_pd_ns, depart_flight_pd_ns, on='Carrier') 
        final_fare_val=[]
        
        for i in range(len(final_data)):
            #for j in range(len(return_flight_pd_ns)):
                    xpath_depart = '//label[@for="'+final_data['Depart_ID'].iloc[i]+'"]'
                    xpath_return = '//label[@for="'+final_data['Return_ID'].iloc[i]+'"]'
                    
                    elements = driver.find_element_by_xpath(xpath_depart)
                    driver.execute_script("arguments[0].click();", elements)
                    
                    #time.sleep(1)
                    elements = driver.find_element_by_xpath(xpath_return)
                    driver.execute_script("arguments[0].click();", elements)
                    time.sleep(1)
                    
                    body = driver.page_source
                    soup_page = BeautifulSoup(body, "lxml")  
                    'splitVw-footer-total make_relative make_flex alC'
                    info = soup_page.find_all('div', attrs={'class': 'splitVw-footer-left'})     
                    flight_no = info[0].find_all('span', attrs={'class': 'airlineInfo-sctn'})[0].text
                    dep_time = info[0].find_all('p', attrs={'class': 'dept-time append_bottom3 LatoBold'})[0].text
                    arr_time = info[0].find_all('p', attrs={'class': 'reaching-time append_bottom3 LatoBold'})[0].text
                    duration = info[0].find_all('div', attrs={'class': 'fli-stops pull-left'})[0].text
                    depart_fare = info[0].find_all('p', attrs={'class': 'actual-price'})[0].text
                    
                    info_right = soup_page.find_all('div', attrs={'class': 'splitVw-footer-right'})     
                    flight_no_right = info_right[0].find_all('span', attrs={'class': 'airlineInfo-sctn'})[0].text
                    dep_time_right = info_right[0].find_all('p', attrs={'class': 'dept-time append_bottom3 LatoBold'})[0].text
                    arr_time_right = info_right[0].find_all('p', attrs={'class': 'reaching-time append_bottom3 LatoBold'})[0].text
                    duration_right = info_right[0].find_all('div', attrs={'class': 'fli-stops pull-left'})[0].text
                    depart_fare_right = info_right[0].find_all('p', attrs={'class': 'actual-price'})[0].text
                    
                    final_fare = soup_page.find_all('span', attrs={'class': 'splitVw-total-fare'})[0].text
                    final_fare_val.append(final_fare)
                    print('=========='+str(i)+'============')
        return final_fare_val

if __name__ == '__main__':
    print(datetime.datetime.now())
    url='https://www.makemytrip.com/flight/search?itinerary=BOM-DEL-21/02/2020_DEL-BOM-24/02/2020&tripType=R&paxType=A-1_C-0_I-0&intl=false&cabinClass=E'
    mydata = scrape_round(url)
    print(datetime.datetime.now())