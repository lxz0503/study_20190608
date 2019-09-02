from lettuce import before, world
from selenium import webdriver
import lettuce_webdriver.webdriver


@before.all
def setup_browser():
    world.browser = webdriver.Firefox()