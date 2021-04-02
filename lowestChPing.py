from selenium import webdriver
import re
import time
import pandas as pd
from multiprocessing import Process, Queue
from selenium.webdriver.firefox.options import Options


def getPing():
    options = Options()
    options.headless = True
    # options.add_argument("--ignore-certificate-errors")
    # options.add_argument("acceptInsecureCerts")
    # options.add_argument('--disable-web-security')
    # options.add_argument('--allow-running-insecure-content')
    # options.set_capability("acceptInsecureCerts", True)

    driver = webdriver.Firefox(options=options)
    driver.get('https://xymu.github.io/maple.watch/#GMS-Reboot')

    time.sleep(5)

    all_servers = driver.find_element_by_class_name("servers").text.split('ms')

    temp_channels = []
    for server in all_servers[:30]:

        split_server = server.splitlines()
        if '' in split_server:
            split_server.remove('')
        try:
            channel, ping = split_server[0], split_server[2]
        except ValueError:
            continue

        re_ping = int(re.search('\d+', ping)[0])
        temp_channels.append([channel, re_ping])

    channels = pd.DataFrame(temp_channels[:30], columns=['channel', 'ping'])
    channels.set_index(['channel'], inplace=True)
    return channels

def mp_ping(numProcs):
    


if __name__ == '__main__':
    out_q = Queue()
    procs = []
    for i in range(3):
        p = Process(target=)


    avg = ((first['ping'] + second['ping'] + third['ping']) / 3).sort_values()

    for i, ping in enumerate(avg):
        channel = avg.sort_values().index[i]
        print(channel, f"{ping:.2f}")
