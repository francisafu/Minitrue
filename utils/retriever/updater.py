import json
import logging
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter


class Updater:
    @staticmethod
    def custom_update(remarks, current_url):
        new_url = ''

        if remarks == "pojiezhiyuanjun/2023":
            today = datetime.today().strftime('%m%d')
            url_front = 'https://raw.githubusercontent.com/pojiezhiyuanjun/2023/main/'
            url_end = '.txt'
            new_url = url_front + today + url_end

        if remarks == "Nodefree.org":
            today = datetime.today().strftime('%Y%m%d')
            this_month = datetime.today().strftime('%Y/%m')
            url_front = 'https://nodefree.org/dy/'
            url_end = '.txt'
            new_url = url_front + this_month + '/' + today + url_end

        if remarks == "FiFier/v2rayShare":
            today = datetime.today().strftime('%Y%m%d')
            this_month = datetime.today().strftime('%Y/%m')
            url_front = 'https://v2rayshare.com/wp-content/uploads/'
            url_end = '.txt'
            new_url = url_front + this_month + '/' + today + url_end

        if remarks == "huanongkejizhijia/clashnode":
            today = datetime.today().strftime('%Y%m%d')
            this_month = datetime.today().strftime('%Y/%m')
            url_front = 'https://clashnode.com/wp-content/uploads/'
            url_end = '.txt'
            new_url = url_front + this_month + '/' + today + url_end

        if remarks == "halfaaa/Free":
            today = datetime.today().strftime('%m.%d.%Y')
            url_front = 'https://raw.githubusercontent.com/halfaaa/Free/main/'
            url_end = '.txt'
            new_url = url_front + today + url_end

        if remarks == "mianfeifq/share":
            try:
                res_json = requests.get('https://api.github.com/repos/mianfeifq/share/contents/').json()
                for file in res_json:
                    if file['name'].startswith('data'):
                        new_url += file['download_url'] + '|'
            except Exception:
                new_url = current_url + '|'
            new_url = current_url if new_url == '' else new_url.strip('|')

        if remarks == "abbasdvd3/node":
            try:
                commit_json = requests.get('https://api.github.com/repos/abbasdvd3/node/commits').json()
                latest_sha = commit_json[0]['sha']
                res_json = requests.get('https://api.github.com/repos/abbasdvd3/node/commits/' + latest_sha).json()
                new_url = ''
                for file in res_json['files']:
                    if file['filename'].__contains__('yaml'):
                        new_url += file['raw_url'] + '|'
            except Exception:
                new_url = current_url + '|'
            new_url = current_url if new_url == '' else new_url.strip('|')

        # Notice: Your custom updater here
        if remarks == "":
            new_url = current_url

        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=2))
        s.mount('https://', HTTPAdapter(max_retries=2))
        try:
            status = s.get(new_url, timeout=4).status_code
        except Exception:
            status = 404
        if status == 200:
            return new_url
        return current_url

    @staticmethod
    def update_list(sub_list):
        logging.info('Start updating sub list')
        with open(sub_list, 'r', encoding='utf-8') as f:
            raw_list = json.load(f)
            f.close()

        for sub in raw_list:
            if sub['method'] != 'auto' and sub['enabled'] is True:
                logging.info('Updating ' + sub['remarks'])
                sub['url'] = Updater.custom_update(sub['remarks'], sub['url'])

        updated_list = json.dumps(raw_list, sort_keys=False, indent=2, ensure_ascii=False)
        file = open(sub_list, 'w', encoding='utf-8')
        file.write(updated_list)
        file.close()
        logging.info('Sub list updated')
