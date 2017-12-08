#!/usr/bin/python3


class LogData:
    def __init__(self):
        self.logs = {}

    def add_log(self, key, json_message):
        self.logs[key] = json_message

    def get_all_logs(self):
        return self.logs

    def get_log(self, key):
        return self.logs[key]


Logger = LogData()