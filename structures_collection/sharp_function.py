#!/usr/bin/python3

from log_handler import LogData

'''
Sharp function should return a Bool
'''


class HandlerStart:
    def __init__(self):
        self.segments = {}
        self.log = LogData()

    def get_sharp(self, parent_system, child_system):
        if (parent_system, child_system) in self.segments:
            return self.segments[(parent_system, child_system)]
        else:
            raise SharpFunctionNotFound()

    def add_sharp(self, parent_system, child_system, func):
        self.segments[(parent_system, child_system)] = func


Handler = HandlerStart()


def new_sharp(parent_system, child_system):

    def sharp_decorator(func):
        Handler.add_sharp(parent_system, child_system, func)

        def wrapped(function_arg1):
            return func(function_arg1)

        return wrapped

    return sharp_decorator


@new_sharp(parent_system='universal:input', child_system='universal:token')
def token_in_input(element, container, input_container):
    pass


@new_sharp(parent_system='universal:token', child_system='universal:morpheme')
def morpheme_in_token(element, container, input_container):
    pass


class SharpFunctionNotFound(Exception):
    pass

