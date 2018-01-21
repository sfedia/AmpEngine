#!/usr/bin/python3

from json import dumps as json_dumps
from datetime import datetime


class New:
    def __init__(self):
        self.log_sectors = dict()

    def add_sector(self, purpose_key):
        if purpose_key not in self.log_sectors:
            self.log_sectors[purpose_key] = []
        else:
            raise LogSectorExistsAlready()

    def add_log(self, purpose_key, **props):
        if purpose_key not in self.log_sectors:
            raise LogSectorNotFound()
        self.log_sectors[purpose_key].append(props)

    def get_sector(self, purpose_key):
        if purpose_key not in self.log_sectors:
            return None
        else:
            return self.log_sectors[purpose_key]

    def get_log_sequence(self, purpose_key, **props):
        if purpose_key not in self.log_sectors:
            raise LogSectorNotFound()
        logs_found = []
        for log in self.log_sectors[purpose_key]:
            props_cnc = True
            for prop in props:
                if prop not in log or (prop in log and props[prop] != log[prop]):
                    props_cnc = False
                    break
            if not props_cnc:
                continue
            else:
                logs_found.append(log)
        return logs_found

    def get_all_keys(self):
        return self.log_sectors.keys()

    def create_json_backup(self, purpose_keys=['*']):
        backup_object = {
            'backup_datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'purpose_keys': purpose_keys,
            'seqs_by_keys': dict()
        }
        keys_list = self.get_all_keys() if purpose_keys == ['*'] else purpose_keys
        if purpose_keys == ['*']:
            for purpose_key in keys_list:
                backup_object['seqs_by_keys'][purpose_key] = self.get_log_sequence(purpose_key)
        return json_dumps(backup_object)


class LogSectorExistsAlready(Exception):
    pass


class LogSectorNotFound(Exception):
    pass
