import time
from datetime import datetime
import json
import progressbar
import os
import sys
from selenium.webdriver.common.keys import Keys

sys.path.append(os.path.abspath('../Amazon_Tracker_Python'))

from config import(
  getWebDriverOptions,
  getChromeDriver,
  setIgnoreCertificateError,
  setBrowserAsIncognito,
  setHeadless
)

from amazon_config import(
  SEARCH_TERM,
  CURRENCY,
  FILTERS,
  BASE_URL,
  MAX_NB_RESULTS,
  DIRECTORY,
  HEADLESS
)

class GenerateReport:
  def __init__(self, file_name, filters, base_link, currency, max_results, data):
    report = {
      'title': file_name,
      'date': self.getNow(),
      'currency' : currency,
      'filters': filters,
      'base_link': base_link,
      'max_results': max_results,
      'products': data
    }
    file_location = f'{DIRECTORY}/{file_name}.json'
    with open(file_location, 'w') as f:
      json.dump(report, f)
    print(f"Data written to {file_location}")

  def getNow(self):
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")

class AmazonAPI:
  def __init__(self, search_term, filters, base_url, currency, max_results, headless):
    self.search_term = search_term
    self.filter = filters
    self.base_url = base_url
    self.currency = currency
    self.max_results = max_results
    self.price_filter = f"&rh=p_36%3A{round(filters['min']*100)}-{round(filters['max']*100)}"

    # Initialize the Driver
    options = getWebDriverOptions()
    setIgnoreCertificateError(options)
    setBrowserAsIncognito(options)
    if headless: setHeadless(options)
    self.driver = getChromeDriver(options)

  # Run Scrapping Script
  def run(self):
    print(f"Scrapping {self.base_url} for {self.max_results} first matches of \"{self.search_term}\" with price in range {self.filter['min']}{self.currency}-{self.filter['max']}{self.currency}", end='')

    # Get Links of Products
    links = self.getProductLinks()

    if not links:
      print(" - Found 0 Products")
      return
    print(f" - Found {len(links)} Products")

    # Get more Info about Products
    products = self.getProductsInfo(links)

    # Quit the Driver
    self.driver.quit()

    print(f"Scrapped {len(products)} complete products!")
    return products

  # Get all Links
  def getProductLinks(self):
    links = []
    page = 1
    while True:
      self.driver.get(f"{self.base_url}s?k={self.search_term}{self.price_filter}?page={page}")
      link = self.getProductPageLinks()
      if link:
        for l in link:
          links.append(l)
      else: 
        return links
      if len(links) > self.max_results:
        return links[0:self.max_results]
      page += 1

  # Get Links to all Products on a Page
  def getProductPageLinks(self):
    result_list = self.driver.find_element_by_class_name('s-result-list')
    try:
      results = result_list.find_elements_by_xpath("//div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a")
      return [link.get_attribute('href') for link in results]
    except Exception as e:
      print(f"Exception : {e}")
      return []

  # Get Products Info for all Products
  def getProductsInfo(self, links):
    asins = self.getAsins(links)
    products = []
    for i in progressbar.progressbar(range(len(asins))):
      product = self.getProductInfo(asins[i])
      if product: products.append(product)
    return products

  # Get Complete Product Info of Single Product
  def getProductInfo(self, asin):
    short_url = self.shortURL(asin)
    self.driver.get(f"{short_url}")

    title = self.getProductTitle()
    seller = self.getProductSeller()
    price = self.getProductPrice()

    if title and seller and price:
      return {
        'asin' : asin,
        'url': short_url,
        'title': title,
        'seller': seller,
        'price': price
      }
    return None

  # Get Product Title
  def getProductTitle(self):
    try:
      return self.driver.find_element_by_id("productTitle").text
    except:
      return None

  # Get Product Seller
  def getProductSeller(self):
    try:
      return self.driver.find_element_by_id("bylineInfo").text
    except:
      return None

  # Get Product Price
  def getProductPrice(self):
    try:
      price = self.driver.find_element_by_id("priceblock_ourprice").text
      return float(price[2:].replace(",", "."))
    except:
        return None

  # Extract Asin from URL
  def getAsins(self, links):
    return [link[link.find('/dp/')+4: link.find('/ref')] for link in links]

  # Remove unnecessary stuff from URL
  def shortURL(self, asin):
    return self.base_url + 'dp/' + asin


if __name__ == '__main__':
  os.system('clear')
  print("Starting Scrapping Script...")
  amazon = AmazonAPI(SEARCH_TERM, FILTERS, BASE_URL, CURRENCY, MAX_NB_RESULTS, HEADLESS)
  data = amazon.run()
  GenerateReport(SEARCH_TERM, FILTERS, BASE_URL, CURRENCY, MAX_NB_RESULTS, data)

