# -*- coding: utf-8 -*-

import requests
import json

headers = {"API-VER": "2.0", "REQ-TYPE": "server", "SSP-NAME": "123", "ENCRYPTION ": "adusingEncryption"}

class HTTPSender(object):
  def __init__(self, url):
    self.url = url

  def __call__(self, *args):
    return self.Send(*args)

  def Send(self, payload):
    #print('payload:%s' % payload)
    try:
        body = json.dumps(payload)
    except:
        print('json dump failed!')
    #print('url:%s body:%s' % (self.url, body))
    response = requests.post(self.url, headers = headers, data = body)
    status = response.status_code
    data = response.json()
    
    return (status, data)
