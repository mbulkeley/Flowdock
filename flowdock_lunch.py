# -*- coding: utf-8 -*-
# !/usr/bin/env python3.7

def main():
    import os
    import json
    import time
    import random
    import logging
    import datetime
    import requests
    from requests.auth import HTTPBasicAuth

    # Set up logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Logging file handler
    handler = logging.FileHandler("./logs/lunch.log")
    handler.setLevel(logging.DEBUG)

    # Logging format added to handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('*** STARTING ***')

    flowdock_api_key = os.environ.get("FLOWDOCK_API_KEY")
    flowdock_org = os.environ.get("FLOWDOCK_ORG")
    flowdock_flow = os.environ.get("FLOWDOCK_FLOW")

    current_time = datetime.datetime.now()

    if current_time.weekday() != 4:
        friday = False
    else:
        friday = True

    logger.debug('IS TODAY FRIDAY? %s' % friday)

    # Instantiate a session with some default configuration params
    session = requests.Session()

    try:
        headers = {'X-flowdock-wait-for-message': 'true', 'content-type': 'application/json',
                   'Accept': 'application/json'}
        session.headers.update(headers)
        logger.debug('Session headers: %s' % session.headers)

        logger.debug('Taking a bit of a snooze.')
        snooze = (random.randint(1, 10) * 60)
        logger.info('Snoozing at: %s for %s minutes.' % (datetime.datetime.now(), (snooze / 60)))
        time.sleep(snooze)  # Sleep 1-10 some-odd minutes.
        logger.info('Awake at: %s' % (datetime.datetime.now()))

        logger.info('Posting to CHAT')

        if not friday:
            emoji = [":bento:", ":ramen:", ":hamburger::fries:", ":cheeseburger::fries:", ":pizza:", ":spaghetti:",
                     ":curry:", ":stew:", ":sushi:", ":sandwich:"]
            content = '%s %s' % ("#lunch", random.choice(emoji))
        else:
            emoji = [":hamburger::fries::beer:", ":spaghetti::wine_glass:", ":cocktail::cocktail:",
                     ":cheeseburger::fries::beer:", ":bento::sake:", ":sushi::sake:", ":ramen::sake:", ":pizza::beer:"]
            content = '%s %s' % ("#longlunch", random.choice(emoji))

        payload = {"content": content, "event": "message"}
        logger.debug('Payload: %s' % payload)

        url = 'https://api.flowdock.com/flows/%s/%s/messages' % (flowdock_org, flowdock_flow)

        logger.debug('URL: %s' % url)
        response = session.post(url, data=json.dumps(payload), headers=headers,
                                auth=HTTPBasicAuth(flowdock_api_key, 'DUMMY'))
        logger.info('Response from Flowdock: %s' % response.headers['Status'])
        logger.debug('Response headers: %s' % response.headers)
        logger.debug('Response content: %s' % response.content)

        thread = response.json()['thread_id']
        logger.debug('Thread ID: %s' % thread)

        snooze = (random.randint(30, 39) * 60)
        logger.info('Sleeping at: %s for %s minutes.' % (datetime.datetime.now(), (snooze / 60)))
        time.sleep(snooze)  # Sleep 30 some-odd minutes.
        logger.info('Awake at: %s' % (datetime.datetime.now()))

        logger.info('Posting to THREAD')
        payload = {"content": "#back", "event": "message"}

        url = 'https://api.flowdock.com/flows/%s/%s/threads/%s/messages' % (flowdock_org, flowdock_flow, thread)
        logger.debug(url)

        response = session.post(url, data=json.dumps(payload), headers=headers,
                                auth=HTTPBasicAuth(flowdock_api_key, 'DUMMY'))
        logger.info('Response from Flowdock: %s' % response.headers['Status'])
        logger.info('*** DONE ***')

    except Exception as err:

        logger.error(err)
        logger.error('There was an ERROR: ', exc_info=True)

    finally:
        session.close()


main()
