from pride.utilities import Latency
import time

def test():
    latency = Latency("Sleep test")
    mark = latency.mark
    sleep = time.sleep
    for x in xrange(1000):
        mark()
        sleep(.01)
    return latency
    