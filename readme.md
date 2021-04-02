# MapleStory Ping Ranker
## GMS-Reboot Server 

## about
multiprocessed approach to identify the ping on MapleStory channels, and ranking them (ascending) to show which is the
lowest latency channel.



## running
run `pip install -r requirements.txt` in shell (ideally from a virtual environment)

after,
`python lowest_ch_ping.py`

requirements:
- python 3
- selenium
- pandas

## sources
used the [maple.watch](https://xymu.github.io/maple.watch/#GMS-Reboot) site to identify the pings.
