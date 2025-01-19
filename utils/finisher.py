import os

import psutil


class Finisher:
    @staticmethod
    def remove_redundancies():
        # if os.path.exists('./out.json'):
        #     os.unlink('./out.json')
        if os.path.exists('./output/base_temp.txt'):
            os.unlink('./output/base_temp.txt')
        if os.path.exists('./output/clash_all_temp.txt'):
            os.unlink('./output/clash_all_temp.txt')
        if os.path.exists('./output/clash_part_temp.txt'):
            os.unlink('./output/clash_part_temp.txt')
        Finisher.kill_processes('subconverter')

    @staticmethod
    def kill_processes(name):
        for p in psutil.process_iter():
            if p.name().__contains__(name):
                p.kill()
