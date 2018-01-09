#!/usr/bin/python3


class HandlerStart:
    def __init__(self):
        self.segments = {}
        self.bound = {}

    def segment(self, from_, to_):
        if (from_, to_) in self.segments:
            return self.segments[(from_, to_)]
        else:
            raise NoSuchSegmentTemplate()

    def bound_functions(self, from_, to_):
        if (from_, to_) not in self.bound:
            return []
        else:
            return self.bound[(from_, to_)]

    def add_segment(self, from_, to_, func, bound_functions):
        self.segments[(from_, to_)] = func
        for fn in bound_functions:
            if (from_, to_) not in self.bound:
                self.bound = []
            self.bound[(from_, to_)].append(fn)

    def can_segment(self, from_, to_):
        return (from_, to_) in self.segments

    def to_values(self, to_):
        to_val = []
        for key in self.segments:
            to_val.append(key[1])
        return to_val


# every function should return List


Handler = HandlerStart()


def segmentation(from_, to_, bound_functions=[]):

    def segm_decorator(func):
        Handler.add_segment(from_, to_, func, bound_functions)

        def wrapped(function_arg1, function_arg2):
            return func(function_arg1, function_arg2)

        return wrapped

    return segm_decorator


@segmentation('universal:input', 'universal:token')
def input_to_tokens(content, metadata=None):
    return content.split()


class NoSuchSegmentTemplate(Exception):
    pass
