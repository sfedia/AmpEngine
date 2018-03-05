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
        self.__match_from = {}

    def add_match(self, a, b, regex_before=(0, None), before_strict=False, regex_after=(0, None), after_strict=False):
        mf_key = tuple(x for x in a)
        if mf_key not in self.__match_from:
            self.__match_from[mf_key] = {}
        self.__match_from[mf_key][(regex_before, regex_after)] = b

    def char_replace(self, char, before=[], after=[]):
        return [
            self.__match_from[char][x] for x in self.__match_from[char]
            if x[0][0] == len(before) and re.search(x[0][1], ''.join(before))
            and x[1][0] == len(after) and re.search(x[1][1], ''.join(after))
        ]




def regressive_conversion(from_, to_):
    def rc_decorator(func):
        Handler.add_conversion(from_, to_, func)

        def wrapped(function_arg1, function_arg2):
            return func(function_arg1, function_arg2)

        return wrapped
    return rc_decorator


class SegmentTemplateNotFound(Exception):
    pass
