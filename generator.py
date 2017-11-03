# -*- coding: utf-8 -*-

request_send = {\
    #"pubid": "82ac5c568",\
    "pubid": "3-10007",\
    "adunitid": "175-10010",\
    "network": 0,\
    "pkg": "com.adusing.adsdemo",\
    "devw": 640,\
    "devh": 1136,\
    "screen": True,\
    "androidid": "403a66c10b9dec23",\
    "model": "MX4",\
    "osv": "5.1",\
    "mac": "02:00:6B:16:C6:2A",\
    "version": "2.0",\
    "ua": "Mozilla/5.0 (Linux; Android 4.4.4; MI 3C Build/KTU84P) AppleWebKit/537.36 (KHTML,like Gecko) Version/4.0 Chrome/33.0.0.0 Mobile Safari/537.36",\
    "ip": "171.84.52.67",\
    "os": 1,\
    "idfa": "123"\
}

class BidRequestGenerator(object):
    def __init__(self):
        pass

    def GenerateRequest(self):
        global request_send
        return request_send