import re
import time
from multiprocessing import Process, Queue
from functools import reduce
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
#specify where the geckodriver responsible for selenium-firefox is
DRIVER_PATH = 'geckodriver.exe'

def getPing(out_q):
    options = Options()

    #don't want selenium to spawn a new window, will keep headless, so low-profile
    options.headless = True

    #creating the webdriver used to make the request
    driver = webdriver.Firefox(executable_path=DRIVER_PATH,options=options)

    #sending the request to the maple.watch page
    driver.get('https://xymu.github.io/maple.watch/#GMS-Reboot')

    # on avg. it takes ~5s to fully load the page with JS, so add some waiting for that to complete.
    time.sleep(5)

    #find all the results for the channel pings, separate into a list using 'ms' delimiter
    all_servers = driver.find_element_by_class_name("servers").text.split('ms')

    #no longer need the firefox process, can kill to save memory.
    driver.quit()

    temp_channels = []
    #going to extract the channel and ping
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

    #packaging up the channels and their ping into a dataframe
    channels = pd.DataFrame(temp_channels[:30], columns=['channel', 'ping'])
    channels.set_index(['channel'], inplace=True)

    #adding the values generated into the queue given at the beginning (for MP)
    out_q.put(channels)

def mp_ping(numProcs):
    out_q = Queue()
    procs = []
    for i in range(numProcs):
        #adding each process to the Queue for multiprocessing
        p = Process(target=getPing, args=(out_q,))
        procs.append(p)
        #starting the process
        p.start()
    results = []
    for i in range(numProcs):
        #add the results of the getPing() for each process into a results list
        results.append(out_q.get())
    for p in procs:
        #ensure each process finishes
        p.join()
    return results

if __name__ == "__main__":
    import multiprocessing
    #to make it as reliable as possible while maintaining speed, finds the number of cores on system
    num_cores = multiprocessing.cpu_count()

    #sets number of processes to spawn according to num of cores
    results = mp_ping(numProcs=num_cores)

    #sums the values in all the results for mean calculation later
    avg = reduce(lambda x,y: x.add(y, fill_value=0), results)

    #divides by number of processes, and ranks from lowest -> highest ping
    avg = (avg['ping'] / len(results)).sort_values()

    #outputs to user the values
    for i, ping in enumerate(avg):
        channel = avg.index[i]
        print(channel, '|', f"{ping:.2f}ms")
