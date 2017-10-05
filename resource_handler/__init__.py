#!/usr/bin/python3

marked_functions = {}


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
            for key in marked_functions:
                if fn in marked_functions[key]:
                    if len(key) == 0:
                        raise BadProvidingDecorator()
                    if type(key[0]) != tuple:
                        new_key = (tuple(parameters), tuple(key))
                        if new_key in marked_functions:
                            if fn not in marked_functions[fn]:
                                marked_functions[new_key].append(fn)
                        else:
                            marked_functions[new_key] = fn



class NoCalledClassesFound(Exception):
    pass


class BadProvidingDecorator(Exception):
    pass
