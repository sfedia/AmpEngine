#!/usr/bin/python3

import re
import collections


class HandlerStart:
    def __init__(self):
        self.param_extractors = {}
        self.ext_wrap = collections.namedtuple('ExtractorWrapper', 'parameter extractor')

    def get_param_extractors(self, system_name=None, param_name=None):
        if system_name is not None and param_name is not None:
            extractors = [
                self.ext_wrap(key[1], self.param_extractors[key]) for key in self.param_extractors
                if (key[0] is None or key[0] == system_name) and (key[1] is None or key[1] == param_name)
            ]
        elif system_name is None and param_name is not None:
            extractors = [
                self.ext_wrap(key[1], self.param_extractors[key]) for key in self.param_extractors
                if (key[1] is None or key[1] == param_name)
            ]
        elif system_name is not None and param_name is None:
            extractors = [
                self.ext_wrap(key[1], self.param_extractors[key]) for key in self.param_extractors
                if (key[0] is None or key[0] == system_name)
            ]
        else:
            extractors = [self.ext_wrap(key[1], self.param_extractors[key]) for key in self.param_extractors]

        if extractors:
            return extractors
        else:
            raise ExtractorNotFound()

    def add_param_extractor(self, system_name, param_name, func):
        self.param_extractors[(system_name, param_name)] = func


class Arguments:
    def __init__(self, args):
        self.args = args

    def get_argument(self, name, allow_none=False):
        args = [arg['value'] for arg in self.args if arg['name'] == name]
        if args:
            return args[0]
        elif allow_none:
            return None
        else:
            raise ArgumentNotFound()


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
    return element.get_system_name().split(':')[-1]


@extract_parameter(None, 'universal:full_entity')
def full_entity_of_element(element, arguments=[], compared_value=None):
    return element.get_system_name()


@extract_parameter(None, 'universal:class')
def class_of_element(element, arguments=[], compared_value=None):
    if compared_value is None:
        raise ValueError("There should be a class name to compare with")
    return compared_value in element.get_class_names()


@extract_parameter(None, 'universal:reg_match')
def reg_match(element, arguments=[], compared_value=None):
    if compared_value is None:
        raise ValueError("Regex is empty")
    args = Arguments(arguments)
    pre_param = args.get_argument('pre', allow_none=True)
    min_strategy = True if args.get_argument('max_strategy', allow_none=True) is None else False
    if pre_param is None or pre_param not in element.get_content():
        return re.search(compared_value, element.get_content()) is not None
    else:
        cv_pattern = re.compile(pre_param)
        positions = [x.start() for x in cv_pattern.finditer(element.get_content())]
        if min_strategy:
            for pos in positions if min_strategy else reversed(positions):
                if re.search(compared_value, element.get_content[:pos]) is not None:
                    return True
            return False


class ExtractorNotFound(Exception):
    pass


class ArgumentNotFound(Exception):
    pass
