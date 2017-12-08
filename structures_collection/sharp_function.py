#!/usr/bin/python3

'''
Sharp function should return a Bool
'''


class HandlerStart:
    def __init__(self):
        self.segments = {}

    def get_sharp(self, parent_system, child_system):
        if (parent_system, child_system) in self.segments:
            return self.segments[(parent_system, child_system)]
        else:
            raise NoSuchSharpFunction()

    def add_sharp(self, parent_system, child_system, func):
        self.segments[(parent_system, child_system)] = func


# every function should return List


Handler = HandlerStart()


def new_sharp(parent_system, child_system):

    def sharp_decorator(func):
        Handler.add_sharp(parent_system, child_system, func)

        def wrapped(function_arg1):
            return func(function_arg1)

        return wrapped

    return sharp_decorator


@new_sharp(parent_system='universal:token', child_system='universal:morpheme')
def token_to_morpheme(**kwargs):
    pass


class NoSuchSharpFunction(Exception):
    pass

