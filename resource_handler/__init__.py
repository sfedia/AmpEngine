#!/usr/bin/python3

marked_functions = {}


def mark_as(identifiers):
    def wrapper(cl):
        def wrapped(*args):
            marked_classes[tuple(identifiers)] = cl
        return wrapped
    return wrapper


class Prepare:

    def __init__(self, *args):
        self.called = []
        for tag_ in args:
            for identifiers in marked_classes:
                if tag_ in identifiers and not marked_classes[identifiers] in self.called:
                    self.called.append(marked_classes[identifiers])

        if len(self.called) == 0:
            raise NoCalledClassesFound()

    def get_parameter(self, key, element):
        for called in self.called:
            pass


class Void:
    def __init__(self):
        pass

    @staticmethod
    def get_parameter(key, element):
        return False


def tag(strings):
    def wrapper(fn):
        def wrapped(*args):
            if not tuple(strings) in marked_functions:
                marked_functions[tuple(strings)] = [fn]
            else:
                marked_functions[tuple(strings)].append(fn)
        return wrapped
    return wrapper

def provides(parameters):
    def wrapper(fn):
        def wrapped(*args):
            #for


def makeitalic(fn):
    def wrapper(fn):
        return "<i>" + fn() + "</i>"

    return wrapped


class NoCalledClassesFound(Exception):
    pass

