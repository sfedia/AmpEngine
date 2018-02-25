#!/usr/bin/python3


class HandlerStart:
    def __init__(self):
        self.param_extractors = {}

    def get_param_extractors(self, system_name=None, param_name=None):
        if param_name is not None:
            extractors = [
                (key[1], self.param_extractors[key]) for key in self.param_extractors
                if (param_name is None and key[0] == system_name) or key[1] == param_name
            ]
        else:
            extractors = [
                (key[1], self.param_extractors[key]) for key in self.param_extractors
                if system_name is None or key[0] == system_name
            ]

        if extractors:
            return extractors
        else:
            raise ExtractorNotFound()

    def add_param_extractor(self, system_name, param_name, func):
        self.param_extractors[(system_name, param_name)] = func


Handler = HandlerStart()


def extract_parameter(system_name, param_name):

    def segm_decorator(func):
        Handler.add_param_extractor(system_name, param_name, func)

        def wrapped(function_arg1):
            return func(function_arg1)

        return wrapped

    return segm_decorator


@extract_parameter('universal:token', 'universal:length')
def length_of_token(element, arguments=[]):
    """
    :param element: IC element
    :param arguments: arguments which are passed within ParameterPair
    :return: parameter value
    """
    return len(element.get_content())


class ExtractorNotFound(Exception):
    pass
