#!/usr/bin/python3
import structures_collection.char_level
import string


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


def regressive_conversion(from_, to_):
    def rc_decorator(func):
        Handler.add_conversion(from_, to_, func)

        def wrapped(function_arg1, function_arg2):
            return func(function_arg1, function_arg2)

        return wrapped
    return rc_decorator


class SegmentTemplateNotFound(Exception):
    pass
