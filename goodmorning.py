# -*- coding: utf-8 -*-
# !/usr/bin/env python3.7

def main():
    import os
    import json
    import random
    import logging
    import datetime
    import requests
    import dateutil.parser
    from requests.auth import HTTPBasicAuth

    # Set up logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Logging file handler
    handler = logging.FileHandler("./logs/morning.log")
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
    utc_time = datetime.datetime.utcnow()

    if current_time.weekday() != 4:
        friday = False
    else:
        friday = True

    greeting = ["Good morning", "#morning", "Morning", "Mornin'", "#goodmorning"]
    # greeting = ["Howdy!","#howdy","Howdy do","Hoooow Dee Do"]
    emoji = [":tada:", ":beers:", ":taco:", ":pow:", ":booyah:"]
    friday_message = ["Friday", "Happy Friday", "TGIF", "Weekend"]

    logger.debug('IS TODAY FRIDAY? {}'.format(friday))

    # Instantiate a session with some default configuration params
    session = requests.Session()

    try:
        logger.info('Searching for Good morning thread.')

        url = 'https://api.flowdock.com/flows/%s/%s/messages?limit=5&search=morning' % (flowdock_org, flowdock_flow)
        headers = {"content-type": "application/json", "accept": "application/json"}
        response = session.get(url, headers=headers, auth=HTTPBasicAuth(flowdock_api_key, 'DUMMY'))
        logger.debug('HEADERS: {}\n'.format(response.headers))
        logger.debug('URL: {}\n'.format(url))
        logger.debug('FULL RESPONSE JSON: {}\n'.format(response.json()))

        threads = []

        for node in response.json():
            logger.debug('RESPONSE JSON: {}\n'.format(node))
            logger.debug('Time difference less than or equal to 10 minutes? {}'.format(
                utc_time - dateutil.parser.parse(node['created_at'], ignoretz=True) <= datetime.timedelta(minutes=10)))
            logger.debug('USER ON POST: {}'.format(node['user']))
            logger.debug('INITIAL MESSAGE ID: {}'.format(node['thread']['initial_message']))
            logger.debug('MESSAGE ID: {}'.format(node['id']))
            logger.debug('Message: {} - Created at: {}\n'.format(node['content'].encode("utf-8"), node['created_at']))

            if utc_time - dateutil.parser.parse(node['created_at'], ignoretz=True) <= datetime.timedelta(minutes=10) \
                    and node['thread']['initial_message'] == node['id']:
                logger.debug('Adding THREAD {}'.format(node['thread_id']))

                url = 'https://api.flowdock.com/users/{}'.format(node['user'])
                logger.debug(url)

                response = session.get(url, headers=headers, auth=HTTPBasicAuth(flowdock_api_key, 'DUMMY'))

                logger.debug('NICKNAME FOR @MENTION: {}'.format(response.json()['nick']))
                threads.append('{{"thread_id": "{}","nickname": "{}"}}'.format(node['thread_id'],
                                                                               response.json()['nick']))

        logger.debug(threads)
        logger.debug('LENGTH OF THREADS: {}'.format(len(threads)))

        headers = {'X-flowdock-wait-for-message': 'true', 'content-type': 'application/json',
                   'Accept': 'application/json'}
        session.headers.update(headers)
        logger.debug('Session headers: {}'.format(session.headers))

        if len(threads) > 0:
            logger.info('Posting to THREAD(S)')

            for thread in threads:
                info = json.loads(thread)
                content = '{} @{}'.format(random.choice(greeting), info['nickname'])
                if friday:
                    content += '! {}! {}'.format(random.choice(friday_message), random.choice(emoji))

                payload = {"content": content, "event": "message"}
                logger.debug(payload)

                url = 'https://api.flowdock.com/flows/{}/{}/threads/{}/messages'.format(
                    flowdock_org, flowdock_flow, info['thread_id'])
                logger.debug(url)

                response = session.post(url, data=json.dumps(payload), headers=headers,
                                        auth=HTTPBasicAuth(flowdock_api_key, 'DUMMY'))
                logger.info('Response from Flowdock: {}'.format(response.headers['Status']))
        else:
            logger.info('Posting to CHAT')

            content = random.choice(greeting)
            if friday:
                content += ' {}! {}'.format(random.choice(friday_message), random.choice(emoji))

            payload = {"content": content, "event": "message"}
            logger.debug(payload)

            url = 'https://api.flowdock.com/flows/{}/{}/messages'.format(flowdock_org, flowdock_flow)

            logger.debug(url)
            response = session.post(url, data=json.dumps(payload), headers=headers,
                                    auth=HTTPBasicAuth(flowdock_api_key, 'DUMMY'))
            logger.info('Response from Flowdock: {}'.format(response.headers['Status']))

        logger.debug('Response headers: {}'.format(response.headers))
        logger.debug('Response content: {}'.format(response.content))
        logger.info('*** DONE ***')

    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting: ", errc)
    except Exception as err:
        logger.error('There was an ERROR: ', exc_info=True)
    finally:
        session.close()


main()
