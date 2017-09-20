#!/usr/bin/python3


class RelativeDatabase:

    references = {}

    def undirected(self, st_a, st_b):
        def wrapper(function):
            def wrapped(*args):
                self.references[(st_a, st_b)] = function
                self.references[(st_b, st_a)] = function
            return wrapped
        return wrapper

    def directed(self, st_a, st_b):
        def wrapper(function):
            def wrapped(*args):
                self.references[(st_a, st_b)] = function
            return wrapped
        return wrapper


def convertible(st_a, st_b):
    return (st_a, st_b) in RelativeDatabase.references


def convert(st_a, st_b, value):
    if convertible(st_a, st_b):
        try:
            return RelativeDatabase.references[(st_a, st_b)](value)
        # too broad!
        except:
            pass

    raise CannotConvertSystemTypes()


def convert_param_pair(st_a, value):
    variants = []

    for k in RelativeDatabase.references:
        if k[0] == st_a:
            try:
                variants.append((k[1], convert(st_a, k[1], value)))
            except CannotConvertSystemTypes:
                pass
    return variants


class CannotConvertSystemTypes(Exception):
    pass