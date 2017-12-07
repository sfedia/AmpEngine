#!/usr/bin/python3


class HandlerStart:
    def __init__(self):
        self.param_extractors = {}

    def get_param_extractor(self, system_name, param_name):
        if (system_name, param_name) in self.param_extractors:
            return self.param_extractors[(system_name, param_name)]
        else:
            raise NoSuchExtractor()

    def add_param_extractor(self, system_name, param_name, func):
        self.param_extractors[(system_name, param_name)] = func


# every function should return List


Handler = HandlerStart()


def extract_parameter(system_name, param_name):

    def segm_decorator(func):
        Handler.add_param_extractor(system_name, param_name, func)

        def wrapped(function_arg1):
            return func(function_arg1)

        return wrapped

    return segm_decorator


@extract_parameter('universal:token', 'universal:length')
def length_of_token(content):
    return len(content)


class NoSuchExtractor(Exception):
    pass