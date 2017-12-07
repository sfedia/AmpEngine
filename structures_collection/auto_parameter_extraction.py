#!/usr/bin/python3


class HandlerStart:
    def __init__(self):
        self.param_extractors = {}

    def get_param_extractors(self, system_name, param_name=None):
        if param_name is not None:
            if (system_name, param_name) in self.param_extractors:
                return param_name, self.param_extractors[(system_name, param_name)]
            else:
                raise NoSuchExtractor()
        else:
            selected_extractors = []
            for key in self.param_extractors:
                if key[0] == system_name:
                    selected_extractors.append((key[1], self.param_extractors[key]))
            return selected_extractors

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