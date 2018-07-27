# -*- coding: utf-8 -*-

def main():
  import json
  import random
  import logging
  import requests
  import dateutil.parser
  from datetime import datetime
  from requests.auth import HTTPBasicAuth

  # Set up logging
  logger = logging.getLogger(__name__)
  # Set to 'INFO' to actually delete the inbox items. 'DEBUG' will list what is going
  # to be deleted, but not delete anything
  logger.setLevel(logging.DEBUG)

  # Logging file handler
  handler = logging.FileHandler('<PATH TO LOG FILE>/inbox_delete.log')
  # Set to 'INFO' to actually delete the inbox items. 'DEBUG' will list what is going
  # to be deleted, but not delete anything
  handler.setLevel(logging.DEBUG)

  # Logging format added to handler
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %H:%M:%S')
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  logger.info('*** STARTING ***')

  api_key      = "<YOUR API KEY>"  
  url_base	   = "https://api.flowdock.com/flows"
  organization = "<YOUR ORGANIZATION>"
  flow         = "<YOUR FLOW>"
  headers      = {"X-flowdock-wait-for-message":"true","content-type":"application/json","accept":"application/json"}
  
  # Posts from external resources, oldest first.
  payload = json.dumps({"sort":"asc","limit":"200","event":"discussion,activity","since_id":"1"}) 
  
  try:
    # Instantiate a session with some default configuration params
    session = requests.Session()

    logger.info('Looking for Inbox Items')
    # Get Messages.
    url = '%s/%s/%s/messages' % (url_base, organization, flow)
    logger.debug(url)

    response = session.get(url, headers=headers, data=payload, auth=HTTPBasicAuth(api_key,'DUMMY'))
    logger.debug(response.json())
    
    for node in response.json():
      logger.debug(node['content'])
      logger.debug('Event: %s  Title: %s' % (node['event'],node['title']))
      logger.debug('%s at %s' % (node['author']['name'],node['created_at']))
      
      # Set to remove before a specific date, or just anything before 'now'
      date1 = datetime.now()
      # date1 = datetime.strptime('2016-03-01T00:00:00.000Z','%Y-%m-%dT%H:%M:%S.%fZ') # In UTC
      date2 = datetime.strptime(node['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ') # In UTC
      logger.debug('date1: %s  date2: %s' % (date1,date2))

      if date2 < date1:
        if logger.getEffectiveLevel() == 10:
          logger.debug('Printing what will be removed - EVENT TYPE: %s with ID: %s' % (node['event'],node['id']))
        else:
          logger.info('Removing EVENT TYPE: %s with ID: %s' % (node['event'],node['id']))
          url = '%s/%s/%s/messages/%s' % (url_base, organization, flow, node['id'])

          response = session.delete(url, headers=headers, auth=HTTPBasicAuth(api_key,'DUMMY'))
          logger.info('Response from Flowdock: %s\n' % response)

    session.close()
    logger.info('*** DONE ***')

  except Exception, e:
    session.close()
    logger.error('There was an ERROR: ',exc_info=True)

main()
