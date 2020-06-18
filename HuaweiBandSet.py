#!/usr/local/bin/python3
from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
import time
import logging
import sys


connection_url = AuthorizedConnection('http://admin:admin1234@192.168.1.3/')

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


# main
try:
    logger.debug("start")
    client = login_router()
    set_bands(sys.argv[1])
    logger.info("band set primary: b%s" % client.device.signal()["band"])
    logger.info("band set global: %s" % get_bands())
    logger.debug("end")

except Exception as e:
    logger.info("Exception occurred: %s" % e)
