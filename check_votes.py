import math
import os
import re
import time

import requests

POLL_ID = os.environ.get("POLL_ID") #Andrew's poll #10550539 is the original poll id

def get_lead():
    result = requests.get('https://poll.fm/' + POLL_ID + '/results')
    text = result.text

    end = re.search(os.environ.get("OUR_NAME"), text).span()[1]
    us = int(text[end+148:].split(" ")[0].replace(",",""))

    end = re.search(os.environ.get("COMPETITOR_NAME"), text).span()[1]
    competitor = int(text[end+148:].split(" ")[0].replace(",",""))

    lead = us - competitor
    return lead

sample_interval = 120.0
min_lead = 1000
big_sample_interval = 1000.0
bot_period = 5.4


while True:
    initial = get_lead()
    print("Initial: " + str(initial))
    time.sleep(sample_interval)
    final = get_lead()
    print("Final: "+ str(final))

    pace = float(final - initial)/sample_interval
    bots_needed = int(math.ceil(-1*pace*bot_period)) + 1 #One to two more bots than needed to keep pace

    if final < min_lead:
        print("Pace: " + str(pace))
        print("Bots Needed: " + str(bots_needed))
        if final > 700:
            bots_called = max(1, bots_needed)
        else:
            bots_called = max(2, bots_needed)
        bots_called = min(10, bots_needed) #just to be sure it doesn't go crazy, set a max number of bots heres
        print("Bots Called = " + str(bots_called))


        t = 0
        votes_per_bot = 1
        while t < big_sample_interval:
            if votes_per_bot % 25 == 0:
                t += 60
                while t > big_sample_interval:
                    t -= 3
                    votes_per_bot -= 1
            else:
                t += 3
            votes_per_bot += 1
        print("Votes Per Bot: " + str(votes_per_bot))
        for i in range(2*bots_needed):
            requests.get(os.environ.get("LAMBDA_ENDPOINT") + "?n=" + str(votes_per_bot))

    time.sleep(big_sample_interval - sample_interval)
