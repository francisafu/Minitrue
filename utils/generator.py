import base64
import json
import logging
import os
import shutil
import socket
import sys

import geoip2.database
import yaml

from utils.retriever.converter import Converter


class Generator:

    @staticmethod
    def write_new_file(file, content):
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
            f.close()

    @staticmethod
    def generate_subs(file, num):
        if not os.path.isfile(file):
            logging.exception('out.json not found, exit program')
            sys.exit(1)
        with open(file, 'r', encoding='utf-8') as f:
            proxies_all = json.load(f)["nodes"]
            f.close()

        filtered_list = sorted(list(filter(lambda x: x['avg_speed'] != 0 and x['isok'], proxies_all)),
                               key=lambda x: x['avg_speed'], reverse=True)
        nodes_list = []
        for item in filtered_list:
            nodes_list.append(item['link'])

        base_temp = base64.b64encode('\n'.join(nodes_list).encode('utf-8')).decode('ascii')
        Generator.write_new_file('./output/base_temp.txt', base_temp)
        clash_nodes = []
        clash_id = 0
        for line in Converter.convert_sub('../output/base_temp.txt', 'clash').split('\n'):
            if not line.strip("\n").__contains__("proxies:"):
                clash_nodes.append({"id": clash_id, "clash": yaml.safe_load(line)})
                clash_id += 1
        clash_nodes = Generator.fix_name(clash_nodes)
        clash = list(map(lambda x: f"  - {x['clash']}", clash_nodes))
        Generator.default_clients(clash, nodes_list.__len__(), num)
        Generator.custom_clients(nodes_list.__len__(), num)
        logging.info(f'Subs generated, total: {clash.__len__()}')

    @staticmethod
    def default_clients(clash, total_length, num):
        content_yaml = 'proxies:\n' + "\n".join(clash)
        Generator.write_new_file('./output/clash_all_temp.txt', content_yaml)
        Generator.write_new_file('./output/clash_all.yml',
                                 Converter.convert_sub('../output/clash_all_temp.txt', 'clash', '&list=false'))

        if total_length > num:
            content_yaml = 'proxies:\n' + "\n".join(clash[:num])
            Generator.write_new_file('./output/clash_part_temp.txt', content_yaml)
            Generator.write_new_file('./output/clash_part.yml',
                                     Converter.convert_sub('../output/clash_part_temp.txt', 'clash', '&list=false'))

        else:
            shutil.copy('./output/clash_all.yml', './output/clash_part.yml')

    @staticmethod
    def custom_clients(total_length, num):
        # Notice: Your custom clients generator here
        pass

    @staticmethod
    def fix_name(corresponding_proxies: []):
        corresponding_proxies = list(filter(lambda x: str(x).__contains__("�") is False, corresponding_proxies))

        for (index, c_proxy) in enumerate(corresponding_proxies):
            proxy = c_proxy['clash']
            if type(proxy) == list:
                proxy = proxy[0]

            server = str(proxy['server'])
            if server.replace('.', '').isdigit():
                ip = server
            else:
                try:
                    ip = socket.gethostbyname(server)
                except Exception:
                    ip = server

            with geoip2.database.Reader('./country/Country.mmdb') as ip_reader:
                try:
                    response = ip_reader.country(ip)
                    country_code = response.country.iso_code
                except Exception:
                    ip = '0.0.0.0'
                    country_code = 'NOWHERE'

            if country_code == 'CLOUDFLARE':
                country_code = 'RELAY'
            elif country_code == 'PRIVATE':
                country_code = 'RELAY'

            proxies_len = len(str(len(corresponding_proxies)))
            proxy['name'] = f'{country_code}-{ip}-{index:0>{proxies_len}d}'

            corresponding_proxies[index]["clash"] = proxy

        return corresponding_proxies
