#!/usr/bin/python3

'''
Should return
{
    'response_type': 'data' or 'parameter',
    'response_metadata': ?, (parameter name can be transmitted through metadata)
    'response_value': data or parameter value
}

Functions which provide parameters should take element as an argument
'''


class HandlerStart:
    def __init__(self):
        self.funcs = {}
        self.params_provided = {}

    def get_func(self, func_name):
        if func_name in self.funcs:
            return self.funcs[func_name]
        else:
            raise FunctionNotFound()

    def add_func(self, func_name, value, params=None):
        self.funcs[func_name] = value
        if params is not None:
            for param in params:
                if param not in self.params_provided:
                    self.params_provided[param] = [value]
                else:
                    self.params_provided[param].append(value)

    def get_all_funcs(self):
        return self.funcs.values()

    def get_parameter(self, param_name, element):
        if param_name not in self.params_provided:
            return False

        return self.params_provided[param_name][0](element=element)


# every function should return List


Handler = HandlerStart()


def new_func(func_name, provides_params=None):

    def segm_decorator(func):
        if provides_params is None:
            Handler.add_func(func_name, func)
        else:
            Handler.add_func(func_name, func, provides_params)

        def wrapped(function_arg1):
            return func(function_arg1)

        return wrapped

    return segm_decorator


@new_func('mansi:get_basic_pos')
def mansi_get_basic_pos(**kwargs):
    pass


class FunctionNotFound(Exception):
    pass
