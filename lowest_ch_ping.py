import re
import time
from multiprocessing import Process, Queue
from functools import reduce
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
DRIVER_PATH = 'geckodriver.exe'

def getPing(out_q):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path=DRIVER_PATH,options=options)
    driver.get('https://xymu.github.io/maple.watch/#GMS-Reboot')

    time.sleep(5)

    all_servers = driver.find_element_by_class_name("servers").text.split('ms')
    driver.quit()

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
    out_q.put(channels)

def mp_ping(numProcs):
    out_q = Queue()
    procs = []
    for i in range(numProcs):
        p = Process(target=getPing, args=(out_q,))
        procs.append(p)
        p.start()
    results = []
    for i in range(numProcs):
        results.append(out_q.get())
    for p in procs:
        p.join()
    return results

if __name__ == "__main__":
    import multiprocessing
    num_cores = multiprocessing.cpu_count()

    results = mp_ping(numProcs=num_cores)
    avg = reduce(lambda x,y: x.add(y, fill_value=0), results)
    avg = (avg['ping'] / len(results)).sort_values()

    for i, ping in enumerate(avg):
        channel = avg.index[i]
        print(channel, '|', f"{ping:.2f}ms")
