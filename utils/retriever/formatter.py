import base64
import logging
import os
import re

import requests

from utils.retriever.converter import Converter


class Formatter:

    @staticmethod
    def default_formatter(sub):
        urls = re.split('\|', sub['url'])
        converted = ''
        for url in urls:
            result = Converter.convert_sub(url, 'clash')
            if result == 'An error occurred':
                logging.warning('Could not fetch node from url: ' + url)
            else:
                converted += result + '\n'
        return converted

    @staticmethod
    def plain_formatter(sub):
        urls = re.split('\|', sub['url'])
        converted = ''
        for url in urls:
            res = requests.get(url, timeout=240).text
            subs = base64.b64encode(res.encode('utf-8')).decode('ascii')
            with open('./output/temp', 'w', encoding='utf-8') as f:
                f.write(subs)
                f.close()
            result = Converter.convert_sub('./output/temp', 'clash')
            if result == 'An error occurred':
                logging.warning('Could not fetch node from url: ' + url)
            else:
                converted += result + '\n'
        os.unlink('./output/temp')
        return converted

    @staticmethod
    def links_formatter(sub):
        urls = re.split('\|', sub['url'])
        converted = ''
        for url in urls:
            res = requests.get(url, timeout=240).text.split("\n")
            for sub_link in res:
                if sub_link.startswith("http"):
                    result = Converter.convert_sub(sub_link, 'clash')
                    if result == 'An error occurred':
                        logging.warning('Could not fetch node from url: ' + url + ': ' + sub_link)
                    else:
                        converted += result + '\n'
        return converted

    @staticmethod
    def custom_formatter(sub):
        # Notice: Your custom formatter here
        urls = re.split('\|', sub['url'])
        converted = ''
        for url in urls:
            pass
        return converted

    @staticmethod
    def format_nodes(raw_list):
        logging.info('Start fetching nodes')
        converted = ''
        with open('./output/all_proxies.yml', 'w', encoding='utf-8') as file_object:
            for sub in raw_list:
                if sub['enabled']:
                    if sub['format'] == 'plain':
                        converted += Formatter.plain_formatter(sub)
                    elif sub['format'] == 'links':
                        converted += Formatter.links_formatter(sub)
                    elif sub['format'] == "":
                        # Notice: Change to your format identifier
                        converted += Formatter.custom_formatter(sub)
                    else:
                        converted += Formatter.default_formatter(sub)
            file_object.write(converted)
            file_object.close()

        lines = open("./output/all_proxies.yml", "r", encoding='utf-8').readlines()
        clash_lines = []
        for line in set(lines):
            if not line.strip("\n").__contains__("proxies:"):
                clash_lines.append(line)
        logging.info(f'Fetching nodes complete, {clash_lines.__len__()} nodes fetched.')

        return clash_lines
