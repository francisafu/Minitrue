import argparse
import logging

from utils.finisher import Finisher
from utils.initiator import Initiator

parser = argparse.ArgumentParser(prog='minitrue.py', description='Welcome to the brand new world!',
                                 epilog='H²=(ȧ/a)²=8πGρ/3-κc²/a²+Δc²/3')
parser.add_argument('-m', type=str, default='b', choices=['b', 'd', 'i'],
                    help='current place, d: domestic, i: international, default(%(default)s): both')
parser.add_argument('-c', type=int, default=200, metavar='int', help='extract nodes count, default: 200')

if __name__ == '__main__':
    args = parser.parse_args()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M"))
    file_handler = logging.FileHandler('./output/minitrue.log')
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s", "%Y-%m-%d %H:%M"))
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    # Notice: Edit here to switch between debug and production situation
    nodes_base = './config/sub_list.json'
    generate_link = './config/generate_link.json'
    # nodes_base = './config/sub_list_test.json'
    # generate_link = './config/generate_link_test.json'

    Initiator.start_program(args.m, args.c, nodes_base, generate_link)
    Finisher.remove_redundancies()
