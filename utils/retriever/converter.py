import logging
import urllib.parse

import requests


class Converter:
    @staticmethod
    def convert_sub(url: str, target: str, extra_options="&list=true", convertor_host="http://127.0.0.1:25500"):
        parsed_url = urllib.parse.quote(url, safe='')
        try:
            convert_url = f'{convertor_host}/sub?target={target}&url={parsed_url}{extra_options}'
            result = requests.get(convert_url, timeout=240).text
            if result == "No nodes were found!":
                return "An error occurred"
            return result
        except Exception as e:
            logging.exception(e)
            return "An error occurred"
