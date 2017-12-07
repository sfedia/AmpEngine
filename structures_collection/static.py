#!/usr/bin/python3


class HandlerStart:
    def __init__(self):
        self.funcs = {}
        self.params_affected = {}

    def get_funcs(self, func_name):
        if func_name in self.funcs:
            return self.funcs[func_name]
        else:
            raise NoSuchFunction()

    def add_func(self, func_name, params_affected, value):
        self.funcs[func_name] = value
        self.params_affected[func_name] = params_affected


# every function should return List


Handler = HandlerStart()


def new_func(func_name, params_affected):

    def segm_decorator(func):
        Handler.add_func(func_name, params_affected, func)

        def wrapped(function_arg1):
            return func(function_arg1)

        return wrapped

    return segm_decorator


@new_func('gram:case:set_loc')
def gram_case_set_loc(element):
    element.set_parameter('gram:case', 'loc')
    return element


class NoSuchFunction(Exception):
    pass
