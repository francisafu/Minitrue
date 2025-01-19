import json
import logging
import platform
import subprocess
import sys
import time

import psutil
import requests

from utils.fetcher import Fetcher
from utils.generator import Generator


class Initiator:

    @staticmethod
    def find_processes(name):
        pids = []
        for p in psutil.process_iter():
            if p.name().__contains__(name):
                pids.append(p.pid)
        return pids

    @staticmethod
    def start_program(mode, count, nodes_base, generate_link):
        logging.info(f'Program starting with mode: {mode} and count: {count}')
        logging.info('Try updating Country.mmdb')
        try:
            res = requests.get('https://cdn.jsdelivr.net/gh/Loyalsoldier/geoip@release/Country.mmdb')
            with open('./country/Country.mmdb', 'wb') as f:
                f.write(res.content)
        except Exception as e:
            logging.exception(e)
            pass

        with open(generate_link, 'r', encoding='utf-8') as f:
            test_links = json.load(f)
            f.close()
        test_link = test_links['both']
        if mode != 'b':
            test_link = test_links['separate']

        if platform.system() == 'Windows':

            if not Initiator.find_processes('subconverter'):
                subprocess.run("start /b ./subconverter/subconverter.exe  >./output/subconverter.log 2>&1", shell=True)
                time.sleep(5)
                if not Initiator.find_processes('subconverter'):
                    logging.exception('Failed to run subconverter')
                    sys.exit(1)

            if mode != 'd':
                Fetcher.retrieve_subs(nodes_base)
            if mode != 'i':
                logging.info('Start testing')
                subprocess.run(
                    f"start /b ./speedtest/lite-windows.exe --config ./config/speedtest_config.json --test {test_link} >./output/speedtest.log 2>&1",
                    shell=True)
                time.sleep(5)
                process = Initiator.find_processes("lite-windows")
                if len(process) == 1:
                    psutil.Process(process[0]).wait()
                Generator.generate_subs('./out.json', count)

        elif platform.system() == 'Linux':
            subprocess.run("chmod +x ./subconverter/subconverter && chmod +x ./speedtest/lite-linux", shell=True)

            if not Initiator.find_processes('subconverter'):
                subprocess.run("nohup ./subconverter/subconverter >./output/subconverter.log 2>&1 &", shell=True)
                time.sleep(5)
                if not Initiator.find_processes('subconverter'):
                    logging.exception('Failed to run subconverter')
                    sys.exit(1)

            if mode != 'd':
                Fetcher.retrieve_subs(nodes_base)
            if mode != 'i':
                logging.info('Start testing')
                subprocess.run(
                    f"nohup ./speedtest/lite-linux --config ./config/speedtest_config.json --test {test_link} >./output/speedtest.log 2>&1 &",
                    shell=True)
                time.sleep(5)
                process = Initiator.find_processes("lite-linux")
                if len(process) == 1:
                    psutil.Process(process[0]).wait()
                Generator.generate_subs('./out.json', count)
        else:
            logging.exception('Unsupported OS, exit program')
            sys.exit(1)
