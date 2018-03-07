#!/usr/bin/python3
import structures_collection.char_level
import string
import re


class HandlerStart:
    def __init__(self):
        self.conversions = {}

    def conversions(self, from_, to_):
        if (from_, to_) in self.conversions:
            return self.conversions[(from_, to_)]
        else:
            raise SegmentTemplateNotFound()

    def add_conversion(self, from_, to_, func):
        self.conversions[(from_, to_)] = func

    def can_convert(self, from_, to_):
        return (from_, to_) in self.conversions

    def to_values(self):
        to_val = []
        for key in self.conversions:
            to_val.append(key[1])
        return list(set(to_val))


# every function should return List


Handler = HandlerStart()


class Conversion:
    def __init__(self):
        self.__match_fc = {}

    def add_match(self, a, b, regex_before=(0, None), regex_after=(0, None)):
        if not a:
            raise ValueError()
        if a[0] not in self.__match_fc:
            self.__match_fc[a[0]] = {}
        self.__match_fc[a[0]][(regex_before, a, regex_after)] = b

    def char_request(self, index, co_sequence):
        for properties in self.__match_fc[co_sequence[index]]:
            if properties[2][0] < len(co_sequence[index + 1:]):
                continue
            elif not re.search(properties[2][1], co_sequence[index+1:index+1+properties[2][0]]):
                continue
            if properties[0][0] < len(co_sequence[:index]):
                continue
            elif not re.search(properties[0][1], co_sequence[index-properties[0][1]:index]):
                continue

            if index + len(properties[1]) >= len(co_sequence):
                continue

            return ConvAction(
                list(range(index, index + len(properties[1]))),
                [x for x in self.__match_fc[co_sequence[index]][properties]]
            )

        return ConvAction('Equal', [index], [co_sequence[index]])


class ConvAction:
    def __init__(self, int_list, rep_list, action_type=None):
        if action_type is None:
            if len(rep_list) - len(int_list) > 0:
                self.__action_type = 'Divide'
            elif len(rep_list) == len(int_list):
                self.__action_type = 'Equal'
            elif len(rep_list) - len(int_list) < 0:
                self.__action_type = 'Merge'
        elif action_type not in ('Equal', 'Divide', 'Merge'):
            raise ValueError
        self.__action_type = action_type
        self.__int_list = int_list
        self.__rep_list = rep_list

    def what(self):
        return self.__action_type

    def get(self, shift=0):
        return (
            self.__action_type,
            [x + shift for x in self.__int_list],
            self.__rep_list,
            len(self.__rep_list) - len(self.__int_list)
        )


def regressive_conversion(from_, to_):
    def rc_decorator(func):
        Handler.add_conversion(from_, to_, func)

        def wrapped(function_arg1, function_arg2):
            return func(function_arg1, function_arg2)

        return wrapped
    return rc_decorator


class SegmentTemplateNotFound(Exception):
    pass
