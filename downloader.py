# -*- coding: utf-8 -*-

"""
Download music list from specific user profile page.
User profile: http://music.i.ua/user/5497167/playlist/62530/#p0
"""

import os

import requests

from selenium import webdriver
from bs4 import BeautifulSoup as BS


OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), 'music')
SITE_URL     = 'http://music.i.ua'
PAGE_URL     = 'http://music.i.ua/user/5497167/playlist/62530/#p{}'
BROWSER      = webdriver.Firefox()

PAGE_NUM = 0
SUMMARY_FILES_CREATED = 0


def progress_msg(func):
    def wrapper(*args, **kwargs):
        print(f' # Downloading new file "{args[1]} - {args[2]}" from page #{PAGE_NUM}')
        func(*args, **kwargs)
        print(f' + File "{args[1]} - {args[2]}" successfully downloaded.')
        print(f' $ Total downloaded and created {SUMMARY_FILES_CREATED} files.\n')
    return wrapper


if not os.path.exists(OUTPUT_DIR):
    os.mkdir('music')


def get_html_js(url):
    BROWSER.get(url)
    return BROWSER.page_source


def get_html(url):
    try:
        return requests.get(url, timeout=(3, 27)).content
    except Exception as e:
        print(e)


@progress_msg
def create_file(audio_url, singer, composition):
    path = os.path.join(OUTPUT_DIR, f'{singer} - {composition}')

    if not os.path.exists(path):
        bs = BS(get_html_js(audio_url), 'lxml')
        audio_url = 'http:' + bs.find('audio').attrs['src']

    r = requests.get(audio_url, allow_redirects=True)
    open(path, 'wb').write(r.content)

    global SUMMARY_FILES_CREATED
    SUMMARY_FILES_CREATED += 1
    return SUMMARY_FILES_CREATED


def downloader_handler(page_num):
    url = PAGE_URL.format(page_num)
    bs = BS(get_html(url), 'lxml')

    for tr in bs.findAll('tr')[1:]:
        audio_url = composition = singer = None

        for index, val in enumerate(tr.findAll('a')):
            if index == 0:
                audio_url = SITE_URL + val.attrs['href']
            elif index == 1:
                composition = val.get_text()
            elif index == 2:
                singer = val.get_text()

        create_file(audio_url, singer, composition)


def main():
    for i in range(1, 9):
        global PAGE_NUM
        PAGE_NUM = i
        downloader_handler(i)


if __name__ == "__main__":
    main()
