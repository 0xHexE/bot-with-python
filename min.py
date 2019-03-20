import signal
import time
from contextlib import contextmanager

from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver


def open_browser_window(url: str):
    options = webdriver.FirefoxOptions()
    options.binary_location = "/usr/bin/firefox"
    # options.set_preference("permissions.default.stylesheet", 2)
    # options.set_preference("permissions.default.image", 2)
    web_driver = webdriver.Firefox(options=options)

    try:
        web_driver.get(url)
    except:
        web_driver.close()
        return open_browser_window(url=url)

    return web_driver


def fetch_question(web_driver: WebDriver):
    question = web_driver.find_element_by_css_selector('div.phoenix-question__body > p')
    options_list = web_driver.find_elements_by_css_selector('div.phoenix-question__body > ul > li > span:nth-child(2)')

    options = ""

    for option in options_list:
        options += '\n' + option.get_attribute('textContent').strip()

    return f"Question: \n{question.get_attribute('textContent')}\nOptions:\n {options.strip()}"


def fetch_answer(web_driver: WebDriver):
    first_option = web_driver.find_element_by_css_selector('div.phoenix-question__body > ul > li:nth-child(1)')
    web_driver.execute_script("arguments[0].click()", first_option)
    time.sleep(1)
    submit_button = web_driver.find_element_by_class_name('submit-practice-btn')
    web_driver.execute_script("arguments[0].click()", submit_button)
    return web_driver.find_element_by_css_selector(
        '.phoenix-question__choice--right > span:nth-child(2)').get_attribute('textContent')


def next_question(web_driver: WebDriver):
    next_button = web_driver.find_element_by_css_selector('.next-question-practice-btn')
    web_driver.execute_script("arguments[0].click()", next_button)


my_list = [
    'https://www.embibe.com/medical/practice/solve/cet-aipmt/biology/biology-in-human-welfare/human-health-and'
    '-disease/session',
    'https://www.embibe.com/medical/practice/solve/cet-aipmt/biology/biotechnology/biotechnology-and-its-applications'
    '/session',
    'https://www.embibe.com/medical/practice/solve/cet-aipmt/biology/diversity-in-the-living-world/biological'
    '-classification/session',
    'https://www.embibe.com/medical/practice/solve/cet-aipmt/biology/ecology/environmental-issues/session',
    'https://www.embibe.com/medical/practice/solve/cet-aipmt/biology/plant-physiology/transport-in-plants/session',
    'https://www.embibe.com/medical/practice/solve/cet-aipmt/biology/reproduction/sexual-reproduction-in-flowering'
    '-plants/session',
    'https://www.embibe.com/medical/practice/solve/cet-aipmt/biology/genetics-and-evolution/principles-of-inheritance'
    '-and-variation/session',
    'https://www.embibe.com/medical/practice/solve/cet-aipmt/biology/human-physiology/digestion-and-absorption/session',
    'https://www.embibe.com/medical/practice/solve/cet-aipmt/biology/structural-organisation-in-animals-and-plants'
    '/anatomy-of-flowering-plants/session',
    'https://www.embibe.com/medical/practice/solve/cet-aipmt/biology/cell-structure-and-function/cell-cycle-and-cell'
    '-division/session',
]


class TimeoutException(Exception): pass


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def load_question():
    my_list.reverse()
    for my_item in my_list:
        driver = open_browser_window(url=my_item)

        driver.implicitly_wait(10)
        try:
            element = driver.find_element_by_id('all')
            driver.execute_script("arguments[0].click()", element)
        except:
            driver.close()
            continue

        name_of_question_bank_stage = my_item.split('/')
        name_of_question_bank = name_of_question_bank_stage[len(name_of_question_bank_stage) - 2]

        print(name_of_question_bank)

        file = open(f'{name_of_question_bank}.txt', 'a', encoding='utf-8')

        retry = 0

        for _ in range(20):
            try:
                with time_limit(10):
                    question = fetch_question(driver)
                    time.sleep(1)
                    answer = fetch_answer(driver)
                    time.sleep(1)
                    next_question(driver)
                    time.sleep(2)
                    file.write(f'{question}\nAnswer: ${answer}\n')
            except TimeoutException as e:
                retry += 1
                if retry > 5:
                    break
            except:
                retry += 1
                if retry > 5:
                    break
        file.close()
        driver.quit()

for _ in range(100):
    load_question()
