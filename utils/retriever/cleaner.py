import logging
import re

import yaml


class Cleaner:

    @staticmethod
    def clean_proxies(clash_lines):
        logging.info('Start cleaning proxies')
        ipv4 = r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})'
        ipv6 = r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
        safe_clash = []
        for line in clash_lines:
            try:
                if (re.search(ipv6, str(line)) is None or re.search(ipv4, str(line)) is not None) and re.search(
                        r"path: /(.*?)\?(.*?)=(.*?)}", str(line)) is None:
                    cl_res = yaml.safe_load(line)
                    if cl_res is not None:
                        cl_temp = yaml.safe_load(str(cl_res[0]))
                        if cl_temp is not None:
                            bad_uuid_format = False
                            if 'uuid' in cl_temp:
                                if cl_temp['uuid'].__len__() != 36:
                                    bad_uuid_format = True
                            if not bad_uuid_format:
                                if cl_temp['type'] == "ss":
                                    if cl_temp["cipher"] != "chacha20-poly1305":
                                        safe_clash.append(cl_res)
                                elif cl_temp['type'] == "vmess":
                                    if cl_temp["network"] == "h2" or cl_temp["network"] == "grpc":
                                        if "tls" not in cl_temp or cl_temp['tls'] is not False:
                                            safe_clash.append(cl_res)
                                    else:
                                        safe_clash.append(cl_res)
                                else:
                                    safe_clash.append(cl_res)
            except Exception:
                pass

        corresponding_list = []
        if safe_clash.__len__() > 0:
            for (i, clash_proxy) in enumerate(safe_clash):
                corresponding_list.append({"id": i, "c_clash": clash_proxy[0]})

        corresponding_list = Cleaner.remove_duplication(corresponding_list)

        clash = list(map(lambda x: f"  - {x['c_clash']}", corresponding_list))
        content_yaml = 'proxies:\n' + "\n".join(clash)
        logging.info(f'Proxies cleaned, {clash.__len__()} nodes exist.')
        return content_yaml

    @staticmethod
    def remove_duplication(corresponding_proxies: []):
        begin = 0
        length = len(corresponding_proxies)
        while begin < length:
            proxy_compared = corresponding_proxies[begin]["c_clash"]
            if type(proxy_compared) == list:
                proxy_compared = proxy_compared[0]

            begin_2 = begin + 1
            while begin_2 <= (length - 1):
                correspond_next_proxy = corresponding_proxies[begin_2]["c_clash"]
                if type(correspond_next_proxy) == list:
                    correspond_next_proxy = correspond_next_proxy[0]
                if proxy_compared['server'] == correspond_next_proxy['server'] and proxy_compared['port'] == \
                        correspond_next_proxy['port']:
                    check = True
                    if 'net' in correspond_next_proxy and 'net' in proxy_compared:
                        if proxy_compared['net'] != correspond_next_proxy['net']:
                            check = False

                    if 'tls' in correspond_next_proxy and 'tls' in proxy_compared:
                        if proxy_compared['tls'] != correspond_next_proxy['tls']:
                            check = False

                    if 'ws-opts' in correspond_next_proxy and 'ws-opts' in proxy_compared:
                        if proxy_compared['ws-opts'] != correspond_next_proxy['ws-opts']:
                            check = False

                    if 'cipher' in correspond_next_proxy and 'cipher' in proxy_compared:
                        if proxy_compared['cipher'] != correspond_next_proxy['cipher']:
                            check = False

                    if 'type' in correspond_next_proxy and 'type' in proxy_compared:
                        if proxy_compared['type'] != correspond_next_proxy['type']:
                            check = False

                    if 'network' in correspond_next_proxy and 'network' in proxy_compared:
                        if proxy_compared['network'] != correspond_next_proxy['network']:
                            check = False

                    if 'obfs' in correspond_next_proxy and 'obfs' in proxy_compared:
                        if proxy_compared['obfs'] != correspond_next_proxy['obfs']:
                            check = False

                    if check:
                        corresponding_proxies.pop(begin_2)
                        length -= 1

                begin_2 += 1
            begin += 1

        return corresponding_proxies
