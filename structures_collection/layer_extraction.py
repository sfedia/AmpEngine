#!/usr/bin/python3


class HandlerStart:
    def __init__(self):
        self.segments = {}

    def segment(self, from_, to_):
        if (from_, to_) in self.segments:
            return self.segments[(from_, to_)]
        else:
            raise NoSuchSegmentTemplate()

    def add_segment(self, from_, to_, func):
        self.segments[(from_, to_)] = func


# every function should return List


Handler = HandlerStart()


def segmentation(from_, to_):

    def segm_decorator(func):
        Handler.add_segment(from_, to_, func)

        def wrapped(function_arg1):
            return func(function_arg1)

        return wrapped

    return segm_decorator


@segmentation('universal:input', 'universal:token')
def input_to_tokens(content, metadata=None):
    return content.split()


class NoSuchSegmentTemplate(Exception):
    pass