#!/usr/local/bin/python3
from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.Connection import Connection
from subprocess import Popen, PIPE
from datetime import datetime

import json
import time
import logging
import sys

# editable config
connection_url = AuthorizedConnection('http://admin:admin1234@192.168.1.3/')
speedtest_cmd = "/Users/omar/Utility/speedtest -s 4302 -f json".split()
bands = ["7+3", "7+3+20", "7+3+20+1"]

# better not edit config
sleep_between_bends = 10
sleep_between_tests = 3600

# not edit config
bandsList = [
    ('b1', 'FDD', '2100', '1'),
    ('b2', 'FDD', '1900', '2'),
    ('b3', 'FDD', '1800', '4'),
    ('b4', 'FDD', '1700', '8'),
    ('b5', 'FDD', '850', '10'),
    ('b6', 'FDD', '800', '20'),
    ('b7', 'FDD', '2600', '40'),
    ('b8', 'FDD', '900', '80'),
    ('b19', 'FDD', '850', '40000'),
    ('b20', 'FDD', '800', '80000'),
    ('b26', 'FDD', '850', '2000000'),
    ('b28', 'FDD', '700', '8000000'),
    ('b32', 'FDD', '1500', '80000000'),
    ('b38', 'TDD', '2600', '2000000000'),
    ('b40', 'TDD', '2300', '8000000000'),
    ('b41', 'TDD', '2500', '10000000000'),
]

sleep_apply_band = 5

# init logger
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
fh = logging.StreamHandler()
fh_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

# functions
def login_router():
    # connect to router
    client = Client(connection_url)
    return client


def get_bands():
    bandRead = str(client.net.net_mode()["LTEBand"])
    bandPrint = ""
    for bandl in bandsList:
        if bool(int(bandRead, 16) & int(bandl[3], 16)):
            bandPrint = bandPrint + bandl[0] + " "
    return (bandPrint)


def apply_band(band):
    logger.debug("applying band: %i" % band)
    lteband = str(hex(band)).replace("0x", "")
    networkband = "3FFFFFFF"
    networkmode = "03"
    client.net.set_net_mode(lteband, networkband, networkmode)
    time.sleep(sleep_apply_band)



def set_bands(bandIn):
    bandTab = (bandIn.replace("+", " ")).split()
    band = 0
    for bandt in bandTab:
        if bandt == "28":
            exp = int(bandsList[11][0].replace('b', ''))
        elif bandt == "20":
            exp = int(bandsList[9][0].replace('b', ''))
        elif bandt == "8":
            exp = int(bandsList[7][0].replace('b', ''))
        elif bandt == "3":
            exp = int(bandsList[2][0].replace('b', ''))
        elif bandt == "1":
            exp = int(bandsList[0][0].replace('b', ''))
        elif bandt == "7":
            exp = int(bandsList[6][0].replace('b', ''))
        elif bandt == "32":
            exp = int(bandsList[12][0].replace('b', ''))
        elif bandt == "38":
            exp = int(bandsList[13][0].replace('b', ''))
        else:
            raise Exception("Unknown frequency: %s" % bandt)
        band = band + 2 ** (exp - 1)

        # apply first band as primary
        if bandt == bandTab[0]:
            apply_band(band)

    # more than one band, apply secondary
    if len(bandTab) > 1:
        apply_band(band)


def launch_speedtest():
    # launch speedtest
    logger.debug("launching speed test")

    output = Popen(speedtest_cmd, stdout=PIPE)
    output_rows = output.communicate()
    #output_rows = (b'{"type":"result","timestamp":"2020-06-10T12:21:25Z","ping":{"jitter":0.14399999999999999,"latency":29.881},"download":{"bandwidth":11547518,"bytes":130498445,"elapsed":13000},"upload":{"bandwidth":4056234,"bytes":42741437,"elapsed":11910},"packetLoss":0,"isp":"Aruba S.p.A.","interface":{"internalIp":"192.168.1.19","name":"en0","macAddr":"AC:BC:32:C1:BB:3B","isVpn":false,"externalIp":"195.231.84.119"},"server":{"id":4302,"name":"Vodafone IT","location":"Milan","country":"Italy","host":"speedtest.vodafone.it","port":8080,"ip":"217.171.46.93"},"result":{"id":"08863488-7af9-4eb1-b604-e29a46ce0616","url":"https://www.speedtest.net/result/c/08863488-7af9-4eb1-b604-e29a46ce0616"}}\n',None)
    speedtest_info = json.loads(output_rows[0])

    # logger.info pretty speed_test
    #logger.debug(json.dumps(speedtest_info, indent=4, sort_keys=True))
    return speedtest_info


def print_stats(client, speed_test, band):
    signal_info = client.device.signal()
    device_info = client.device.information()

    # logger.info pretty info
    logger.debug(json.dumps(signal_info, sort_keys=True, indent=4))
    #logger.info(json.dumps(device_info, sort_keys=True, indent=4))

    download_mbps = 8 * speedtest_info["download"]["bandwidth"] / 1000 / 1000
    upload_mbps = 8 * speedtest_info["upload"]["bandwidth"] / 1000 / 1000
    ping_ms = speedtest_info["ping"]["latency"]
    jitter = speedtest_info["ping"]["jitter"]

    datetimestr = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    logger.info("%s,%s,%s,%s,%s,%s,%.2f,%.2f,%.2f,%.2f"
          % (datetimestr, band, signal_info["rsrp"], signal_info["rsrq"], signal_info["rssi"], signal_info["sinr"],
             download_mbps, upload_mbps, ping_ms, jitter))


# main
try:
    logger.debug("started")
    client = login_router()
    logger.info("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %
          ("time", "band", "rsrp", "rsrq", "rssi", "sinr", "download", "upload", "ping", "jitter"))
    while (1):
        for band in bands:
            logger.debug("trying band: %s" % band)
            set_bands(band)
            speedtest_info = launch_speedtest()
            print_stats(client, speedtest_info, band)
            logger.debug("sleeping for next band: %i sec" % sleep_between_bends)
            time.sleep(sleep_between_bends)
        logger.debug("sleeping for next test: %i sec" % sleep_between_tests)
        time.sleep(sleep_between_tests)

except Exception as e:
    logger.info("Exception occurred: %s" % e)
