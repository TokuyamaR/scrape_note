# seleniumを用いてnoteのデザインカテゴリの人気記事を取得
import logging
import json
import requests
import datetime
from typing import List
from selenium.webdriver import Chrome, ChromeOptions,Remote
from selenium.common.exceptions import NoSuchElementException

def main():
    options = ChromeOptions()
    options.headless = True
    driver = Chrome(options=options)

    navigate(driver)

    contents = scrape_contents(driver)

    if len(contents) > 0:
        message = transfer_contents(contents)
    else:
        message = '人気の記事はありません。'

    post_contents(message)

    driver.quit()

# 指定したページに遷移する
def navigate(driver: Remote):
    logging.info('Navigating...')
    driver.get('https://note.com/topic/design/p/home/s/3')

    assert 'note' in driver.title

def scrape_contents(driver: Remote) -> List[dict]:
    contents = []

    for div in driver.find_elements_by_css_selector(".m-largeNoteWrapper__card"):
        a = div.find_element_by_css_selector('a')
        try:
            like = int(div.find_element_by_css_selector('.m-noteBody__statusLabel').text)
        except NoSuchElementException:
            like = 0
        contents.append({
            'url': a.get_attribute('href'),
            'title': a.get_attribute('aria-label'),
            'like': like
        })

    logging.info(f'Found {len(contents)} contents')
    print_finish_log('取得', True)

    return contents

# チャットワーク用に取得コンテンツを変換
def transfer_contents(contents):
    message_list = []
    dt_now = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')
    message_list.append(f'{dt_now} 時点の人気記事です')
    for content in contents:
        message = f'[info][title]{content["title"]}[/title]{content["url"]}[/info]'
        message_list.append(message)
    all_messages = '\n'.join(message_list)

    print(all_messages)

    return all_messages

def post_contents(message):

    BASE_URL = 'https://api.chatwork.com/v2'

    #Setting
    roomid   = '89512053'
    apikey   = '88f75087e274ee2a2d790fdbd8936122'

    post_message_url = '{}/rooms/{}/messages'.format(BASE_URL, roomid)

    headers = { 'X-ChatWorkToken': apikey}
    params = { 'body': message }
    r = requests.post(
            post_message_url,
            headers=headers,
            params=params
        )
    if(r.status_code == 200):
        print_finish_log('投稿', True)
    else:
        print_finish_log('投稿', False)

def print_finish_log(action, isSuccess):
    if isSuccess:
        print('\n')
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(f'+++++++++++++++++++++++{action}((｀･∀･´))ｵﾜﾀ+++++++++++++++++++++++++++++++++')
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('\n')
    else:
        print('\n')
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(f'+++++++++++++++++++++++{action}((´･ω･｀))ﾀﾞﾒﾎﾟ+++++++++++++++++++++++++++++++++')
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('\n')

if __name__ == '__main__':
    # INFOレベル以上のログを出力する
    logging.basicConfig(level=logging.INFO)
    main()
