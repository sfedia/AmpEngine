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
            raise LogSectorAlreadyExists()

    def add_log(self, purpose_key, **props):
        if purpose_key not in self.log_sectors:
            raise LogSectorNotFound()
        log_document = LogDocument(props)
        log_document.set_sector_name(purpose_key)
        self.log_sectors[purpose_key].append(log_document)

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
                if not log.prop_in_log(prop) or (log.prop_in_log(prop) and props[prop] != log.get_prop(prop)):
                    props_cnc = False
                    break
            if not props_cnc:
                continue
            else:
                logs_found.append(log)
        return logs_found

    def remove_logs_from_sector(self, purpose_key, log_sequence):
        if purpose_key not in self.log_sectors:
            raise LogSectorNotFound()
        self.log_sectors[purpose_key] = [ls for ls in self.log_sectors[purpose_key] if ls not in log_sequence]

    def edit_log_document(self, purpose_key, filter_props, index, props2edit):
        sector_logs = self.get_log_sequence(purpose_key, **filter_props)
        if index >= len(sector_logs):
            raise WrongLogIndex()
        for prop in props2edit:
            sector_logs[index].set_prop(prop, props2edit[prop])

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


class LogDocument:
    def __init__(self, props):
        self.props = props
        self.sector_name = None

    def get_all_props(self):
        return self.props

    def prop_in_log(self, prop_name):
        return prop_name in self.props

    def get_prop(self, prop_name):
        if prop_name not in self.props:
            raise PropNotFound()
        return self.props[prop_name]

    def set_prop(self, prop_name, prop_value):
        if prop_name not in self.props:
            raise PropNotFound()
        self.props[prop_name] = prop_value

    def set_sector_name(self, sector_name):
        self.sector_name = sector_name


class LogSectorAlreadyExists(Exception):
    pass


class LogSectorNotFound(Exception):
    pass


class PropNotFound(Exception):
    pass


class WrongLogIndex(Exception):
    pass
