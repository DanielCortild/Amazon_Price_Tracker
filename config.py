from selenium import webdriver

def getChromeDriver(options):
  return webdriver.Chrome('./chromedriver', chrome_options=options)

def getWebDriverOptions():
  return webdriver.ChromeOptions()

def setIgnoreCertificateError(options):
  options.add_argument('--ignore-certificate-errors')

def setBrowserAsIncognito(options):
  options.add_argument('incognito')

def setHeadless(options):
  options.add_argument("headless")