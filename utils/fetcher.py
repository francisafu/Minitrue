import json

from utils.retriever.cleaner import Cleaner
from utils.retriever.formatter import Formatter
from utils.retriever.updater import Updater


class Fetcher:
    @staticmethod
    def retrieve_subs(sub_list):
        Updater.update_list(sub_list)

        with open(sub_list, 'r', encoding='utf-8') as f:
            raw_list = json.load(f)
            f.close()
        clash_yml = Cleaner.clean_proxies(Formatter.format_nodes(raw_list))
        with open("./output/all_proxies.yml", "w", encoding='utf-8') as f:
            f.write(clash_yml)
            f.close()
