#!/usr/bin/python3

import log_handler.log_object

'''
Sharp function should return a Bool
'''


class HandlerStart:
    def __init__(self):
        self.parsers = {}

    def get_parser(self, parent_system, child_system):
        if (parent_system, child_system) in self.parsers:
            return self.parsers[(parent_system, child_system)]
        else:
            raise ParserNotFound()

    def add_parser(self, parent_system, child_system, func):
        self.parsers[(parent_system, child_system)] = func


Handler = HandlerStart()


def new_parser(parent_system, child_system):

    def parser_decorator(func):
        Handler.add_parser(parent_system, child_system, func)

        def wrapped(function_arg1):
            return func(function_arg1)

        return wrapped

    return parser_decorator


@new_parser(parent_system='universal:token', child_system='universal:morpheme')
def morpheme_in_token(input_container_element, container, input_container):
    if not input_container.ic_log.get_sector("STEMS_EXTRACTED"):
        raise InternalParserException('No stem extractor provided')
    stems = input_container.ic_log.get_log_sequence("STEMS_EXTRACTED", element_id=input_container_element.get_ic_id())
    if not stems:
        raise InternalParserException('No stems found for <{}>'.format(input_container_element.get_ic_id()))
    for n, stem in enumerate(stems):
        input_container_element.ic_log.add_log(
            "POS_PROHIB",
            element_id=input_container_element.get_ic_id(),
            child_system='universal:morpheme',
            parent_system='universal:token',
            spec_name='stem',
            option_number=n,
            positions=stem.get_prop('positions')
        )
    



class ParserNotFound(Exception):
    pass


class InternalParserException(Exception):
    pass
