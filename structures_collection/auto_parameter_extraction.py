#!/usr/bin/python3


class HandlerStart:
    def __init__(self):
        self.param_extractors = {}

    def get_param_extractors(self, system_name=None, param_name=None):
        if system_name is not None and param_name is not None:
            extractors = [
                (key[1], self.param_extractors[key]) for key in self.param_extractors
                if (key[0] is None or key[0] == system_name) and (key[1] is None or key[1] == param_name)
            ]
        elif system_name is None and param_name is not None:
            extractors = [
                (key[1], self.param_extractors[key]) for key in self.param_extractors
                if (key[1] is None or key[1] == param_name)
            ]
        elif system_name is not None and param_name is None:
            extractors = [
                (key[1], self.param_extractors[key]) for key in self.param_extractors
                if (key[0] is None or key[0] == system_name)
            ]
        else:
            extractors = self.param_extractors

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


@extract_parameter(None, 'universal:length')
def length_of_element(element, arguments=[], compared_value=None):
    """
    :param element: IC element
    :param arguments: arguments which are passed within ParameterPair
    :param compared_value: value which is passed within ParameterPair
    :return: parameter value
    """
    return len(element.get_content())


@extract_parameter(None, 'universal:entity')
def entity_of_element(element, arguments=[], compared_value=None):
    return element.get_type().split(':')[-1]


@extract_parameter(None, 'universal:full_entity')
def full_entity_of_element(element, arguments=[], compared_value=None):
    return element.get_type()


@extract_parameter(None, 'universal:class')
def class_of_element(element, arguments=[], compared_value=None):
    if compared_value is None:
        raise ValueError("There should be a class name to compare with")
    return compared_value in element.get_class_names()


class ExtractorNotFound(Exception):
    pass
