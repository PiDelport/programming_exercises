#!/usr/bin/python3
# Note: This was a code challenge for an interview. The better answer is to use a proper monitoring system.
# Purpose: Check for flapping and down ports
# Arbitrary hosts and execution interval.
# Note: developing this on a Linux desktop with multiple Python versions installed,
# hence the shebang.

import sys
import time
import socket
import signal
from multiprocessing.dummy import Pool as ThreadPool

# Settings that may require tuning
SocketTimeout = 1  # Seconds to wait on socket connections
DownCount = 5  # Keep the results of this many iterations. Also affects determination of down status.
SleepTimerSeconds = 55  # How long to wait between completion of one run and start of the next.
Threads = 20  # From experience 20 is often a good balance.
ReportPartialResults = True  # Report down/flapping with less than DownCount results recorded.
StrictFlappingDetection = False  # Require at least 3 consecutive alternating results.
# Notes on these two:
# StrictFlappingDetection:
# 1: False will report flapping on any mixture of up and down over the results.
#       This includes if the service recently went down or came back up.
# 2: True will report OK if the port recently changed state and stayed that way.
#       E.g. one success with the rest failures or vice-versa will both report OK.
# ReportPartialResults:
# 1: False gives no reports until DownCount iterations have completed.
# 2: True down and flappy reporting happens with less than DownCount iterations.
#       Does mean that a down report will happen with 1 to DownCount consecutive down results

# Global variables
# Flag for graceful exiting of worker threads
sigterm = False


def term_signal_handler(signal, frame):
    sigterm = True
    sys.exit(0)

signal.signal(signal.SIGTERM, term_signal_handler)
signal.signal(signal.SIGINT, term_signal_handler)


def process_input(clidata):
    # This assumes good data was provided by the SRE running this.
    # The port is the first CLI parameter and second item in the list.
    port = clidata.pop(1)
    # Get the host list from STDIN and process that into the data structure.
    # Assumes at least one valid hostname was supplied.
    HostDict = {}
    for thisline in sys.stdin:
        HostDict[thisline.strip().lower()] = []
    return int(port), HostDict


def check_individual_host(hostname):
    # Ensure quick exit if SIGTERM was received.
    if sigterm:
        sys.exit(0)
    # Get the connection result and append it to the list.
    try:
        # more expensive call but automatically handles IPv4 vs IPv6
        result = socket.create_connection((hostname, port))
    except:
        # record a failure
        HostDict[hostname].append(1)
    else:
        # success
        HostDict[hostname].append(0)
        # If we need to do a deeper query of the listening service add that here.
        result.close()
    # Expire old result values if any.
    if len(HostDict[hostname]) > DownCount:
        HostDict[hostname].pop(0)
    # This is a primitive but effective way to slightly slow thread execution if it's consuming too much CPU
    # Be sure to consider how this interacts with the main routine loop's sleep interval.
    #time.sleep(.05)
    return


def report_results(HostDict, Iterations):
    # Generate reports to STDOUT for the results once there is sufficient run history.
    if not ReportPartialResults and Iterations < DownCount:
        # configuration to not report on partial results
        return
    for ThisHost in HostDict.keys():
        if 1 in HostDict[ThisHost]:  # At least one failure result in ThisHost's history
            if 0 in HostDict[ThisHost]:  # Also at least one success in ThisHost's history
                if StrictFlappingDetection:
                    # Report only flapping if there is actual alternation of results.
                    if not (sorted(HostDict[ThisHost]) == HostDict[ThisHost]) and \
                            not (sorted(HostDict[ThisHost],reverse=True) == HostDict[ThisHost]):
                        # There is a condition of alternation
                        print('{} is flappy'.format(ThisHost))
                    else:
                        # It may be down but isn't strictly flapping
                        print('{} is reporting ok'.format(ThisHost))
                else:
                    # It may be down consistently but not for DownCount and we're considering that flappy.
                    print('{} is flappy'.format(ThisHost))
            else:
                # All failure
                print('{} is down'.format(ThisHost))
        else:
            # All success
            print('{} is reporting ok'.format(ThisHost))
    return


def check_hosts(HostDict):
    # controller routine to run the port check workers and call the report function.
    socket.setdefaulttimeout(SocketTimeout)
    # Create the thread pool with the desired number of threads.
    MyPool = ThreadPool(processes=Threads)
    Iterations = 0
    while True:
        Iterations += 1
        # Run the pool for this iteration. map blocks and for this purpose the odds of sync issues are low.
        MyPool.map(check_individual_host, HostDict.keys())
        # Report on the result
        report_results(HostDict, Iterations)
        time.sleep(SleepTimerSeconds)
    return


# main routine. Due to the simple nature of this I want these variables at the global level.
port, HostDict = process_input(sys.argv)
check_hosts(HostDict)
