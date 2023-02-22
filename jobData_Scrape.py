# -*- coding: utf-8 -*-
"""

@author: Ammad
"""

location = r'change location accordingly'
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
import time

from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.action_chains import ActionChains

original = []
with open(location + "\\Filter.txt") as f:
	for line in f:
		original.append(line.strip())

#chrome_options = Options()
#chrome_options.add_argument('--headless')

# =============================================================================
# # Here it asks from the user the keyword which he wants the jobs to search for
# =============================================================================
keyword = input('Please enter the jobs you want to search for: ')

# =============================================================================
# # THis part of the code opens the chrome and the website from which we want to extract data
# =============================================================================
link = 'https://www.google.com/search?q=jobs+in+pune&ibp=htl;jobs&sa=X&ved=2ahUKEwi9i7SMxP36AhWT_7sIHerSDDIQudcGKAJ6BAgIEEA&sxsrf=ALiCzsZ1HEAwa1pYyBV4x6AiiKElCDO9Xg:1666774828130#fpstate=tldetail&htivrt=jobs&htidocid=9iNypAiHyS8AAAAAAAAAAA%3D%3D/'

driver = webdriver.Chrome(location + '//chromedriver.exe')
driver.get(link)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#driver.find_element(By.CLASS_NAME, 'lssxud').click()


# It is going to search for the search box
searchBox = driver.find_element(By.ID, 'hs-qsb')
# THis line of code removes any text within the search box
driver.execute_script("arguments[0].value = ''", searchBox)

# The below 2 line of codes enters the keywords and press ENTER key
searchBox.send_keys(keyword)
searchBox.send_keys(Keys.RETURN)


# The following three line of code make sure that all the results are loaded (Pagination)
for i in range(0,35):
	time.sleep(2)
	footer = driver.find_element(By.XPATH, "//div[@class = 'HwPaOd']")
	scroll_origin = ScrollOrigin.from_element(footer, 0, -50)
	ActionChains(driver).scroll_from_origin(scroll_origin, 0, 2000).perform()


# =============================================================================
# # The below lines of code extract the companies and addresses of the job posts
# # And stores them in the List datatype "companies" and "addresses"
# =============================================================================
jobsElement = driver.find_element(By.XPATH, "//div[@jsname = 'CaV2mb']")
jobsHTML = jobsElement.get_attribute('innerHTML')

splitted = jobsHTML.split('<li class=')

companies = []
addresses = []

# The following loop is to make sure every job post data is extracted
for uniqueJob in splitted[1:]:
	companyName = uniqueJob.split('<div class="vNEEBe">')[1].split('<')[0]
	address = uniqueJob.split('<div class="Qk80Jf">')[1].split('</')[0]
	companies.append(companyName)
	addresses.append(address)
	
# =============================================================================
# # Next we search for compaines in https://www.zaubacorp.com/
# =============================================================================
link = 'https://www.zaubacorp.com/'
driver = webdriver.Chrome(location + '//chromedriver.exe')
driver.get(link)


zaubacorpLinks = {}
companiesUpdated = []

# Looping through each company
for company in companies:
	# Check the notepad file to see if the company name is in the txt file
	if any(ext in company for ext in original):
		additionalText = [text for text in original if(text in company)]
		company = company.replace(additionalText[0], '').strip()
		
	# Searching for each company in the search box
	searchBox = driver.find_element(By.ID, 'searchid')
	
	# THis line of code removes any text within the search box
	driver.execute_script("arguments[0].value = ''", searchBox)

	searchBox.send_keys(company)
	time.sleep(3)
	try:
		searchResults = driver.find_element(By.XPATH, "//div[@id = 'result']")
		searchResultsHTML = searchResults.get_attribute('innerHTML').split('id="c')[1:]
		
	except:
		pass
	
	links = []
		
	for searchResultHTML in searchResultsHTML:
		patentLink = link + 'c' + searchResultHTML.split('">')[0]
		
		links.append(patentLink)
	
	# Store the list of links in the dictionary with company names
	zaubacorpLinks[company] = links
	companiesUpdated.append(company)
	time.sleep(3)
	

# Storing all the extracted data into the dataframe which will then be extracted as a CSV file
dataframe = pd.DataFrame()
dataframe['Sr.No'] = np.arange(1, len(companies) + 1).tolist()
dataframe['CompanyName'] = companiesUpdated
dataframe['URL'] = dataframe['CompanyName'].map(zaubacorpLinks)
dataframe['Address'] = addresses
dataframe = dataframe.explode('URL')

# Export the dataframe into the same folder
dataframe.to_csv(location + '\\jobsData.csv', index = False)

print('The Scraping is Complete!')