# -*- coding: utf-8 -*-

import requests
import threading


class Record(object):
    def __init__(self, bid_request, status_code, payload):
        #请求
        self.bid_request = bid_request
        #返回码
        self.status = status_code
        #返回的原始信息
        self.payload = payload
        #统计问题的列表
        self.problems = []
        #返回的proto 对象
        self.bid_response = None

class LoggerException(Exception):
    """ Logger 抛出的异常"""
    pass


class Logger(object):
    """ 记录竞价的相关信息"""
    def __iter__(self):
        if not self._done:
            raise LoggerException('Only locked Loggers are iterable.')
        return self

    def __getitem__(self, item):
        if not self._done:
            raise LoggerException('Only locked Loggers are iterable.')
        return self._records[item]

    def __next__(self):
        if not self._done:
            raise LoggerException('Only locked Loggers can are iterable.')
        if self._current_iteration >= len(self._records):
            self._current_iteration = 0
            raise StopIteration
        c = self._current_iteration
        self._current_iteration += 1
        return self._records[c]

    def __init__(self):
        self._records = []
        self._record_lock = threading.Lock()
        self._current_iteration = 0
        self._done = False

    def Done(self):
        self._record_lock.acquire()
        try:
            self._done = True
        finally:
            self._record_lock.release()

    def IsDone(self):
        self._record_lock.acquire()
        try:
            return self._done
        finally:
            self._record_lock.release()

    def LogSynchronousRequest(self, bid_request, status_code, payload):
        """ 
        @note:  记录竞价的请求和返回
        @params: 
            bid_request: 竞价请求 
            status_code: 响应的返回的状态码
            payload: 响应返回的原始信息 
        @return: 记录成功返回True, 否则返回false
        """
        if self.IsDone():
            return False

        self._record_lock.acquire()
        try:
            record = Record(bid_request, status_code, payload)
            self._records.append(record)
        finally:
            self._record_lock.release()
        return True



class LogSummarizer(object):
    """ 统计竞价并输出到文件中"""
    REQUEST_ERROR_MESSAGES = {
          'not-ok': 'The HTTP response code was not 200/OK.',
          }

    RESPONSE_ERROR_MESSAGES = {
          'empty': 'Response is empty (0 bytes).',
          'parse-error': 'Response could not be parsed.',
          'code-error': 'Response code is not ok.',
          }

    def __init__(self, logger):
        """
        @note:  初始化
        @param:  
            logger: 记录的logger

        """
        self._logger = logger
        self._requests_sent = 0
        self._responses_ok = 0
        self._responses_successful_without_bids = 0

        # 保存正确的返回
        self._good = []
        # 保存可解析，但存在问题的返回
        self._problematic = []
        # 保存不可解析的返回
        self._invalid = []
        # 保存 返回码非200的返回
        self._error = []


    def Summarize(self):
        """
        @note: 统计竞价
        """
        for record in self._logger:
            self._requests_sent += 1
            if record.status == 200:
                self._responses_ok += 1
            else:
                record.problems.append(self.REQUEST_ERROR_MESSAGES['not-ok'])
                self._error.append(record)
                continue
    
            if not record.payload:
                record.problems.append(self.RESPONSE_ERROR_MESSAGES['empty'])
                self._invalid.append(record)
                continue

            if record.payload['code'] != 0:
                record.problems.append(self.RESPONSE_ERROR_MESSAGES['code-error'])
                self._problematic.append(record)
            else:
                self._good.append(record)

    def WriteLogFiles(self, good_log, problematic_log, invalid_log, error_log):
        """
        @note: 输出 successful/error/problematic/invalid requests 到文件中
        @param:
            good_log: 记录正确竞价的文件描述符 
            problematic_log: 记录存在问题竞价的文件描述符 
            invalid_log: 记录无法解析的竞价文件描述符 
            error_log: 记录返回值不是200的竞价的文件描述符 
        """

        if self._problematic:
            problematic_log.write('=== Responses that parsed but had problems ===\n')
        for record in self._problematic:
            problematic_log.write('BidRequest:\n')
            problematic_log.write(str(record.bid_request))
            problematic_log.write('\nBidResponse:\n')
            problematic_log.write(str(record.bid_response))
            problematic_log.write('\nProblems:\n')
            for problem in record.problems:
                problematic_log.write('\t%s\n' % problem)

        if self._good:
            good_log.write('=== Successful responses ===\n')
        for record in self._good:
            good_log.write('BidRequest:\n')
            good_log.write(str(record.bid_request))
            good_log.write('\nBidResponse:\n')
            good_log.write(str(record.bid_response))


        if self._invalid:
            invalid_log.write('=== Responses that failed to parse ===\n')
        for record in self._invalid:
            invalid_log.write('BidRequest:\n')
            invalid_log.write(str(record.bid_request))
            invalid_log.write('\nPayload represented as a python list of bytes:\n')
            byte_list = [ord(c) for c in record.payload]
            invalid_log.write(str(byte_list))

        if self._error:
            error_log.write('=== Requests that received a non 200 HTTP response ===\n')
        for record in self._error:
            error_log.write('BidRequest:\n')
            error_log.write(str(record.bid_request))
            error_log.write('HTTP response status code: %d\n' % record.status)
            #error_log.write('\nPayload represented as a python list of bytes:\n')
            #byte_list = [ord(c) for c in record.payload]
            #error_log.write(str(byte_list))


    def PrintReport(self):
        """Prints a summary report."""
        print('=== Summary of Baidu Real-time Bidding test ===')
        print('Requests sent: %d' % self._requests_sent)
        print('Responses with a 200/OK HTTP response code: %d' % self._responses_ok)
        print('Responses with a non-200 HTTP response code: %d' % len(self._error))
        print('Good responses (no problems found): %d' % len(self._good))
        print('Invalid (unparseable) with a 200/OK HTTP response code: %d' % len( self._invalid))
        print('Parseable responses with problems: %d' % len(self._problematic))
        if self._responses_successful_without_bids == self._requests_sent:
            print('ERROR: None of the responses had bids!')
