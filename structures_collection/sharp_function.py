#!/usr/bin/python3

import log_handler.log_object

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
def token_in_input(element, container_element, container, input_container):
    if not input_container.ic_log.get_sector("ALL_POSITIONS"):
        input_container.ic_log.add_sector("ALL_POSITIONS")
    if not input_container.ic_log.get_sector("DEAD_POSITIONS"):
        input_container.ic_log.add_sector("DEAD_POSITIONS")
    positions = input_container.ic_log.get_log_sequence("ALL_POSITIONS",
                                                        element_id=element.get_ic_id(),
                                                        child_system='universal:token',
                                                        parent_system='universal:input')

    token_sequence = input_container.get_by_system_name('universal:input')[0].get_content().split()
    if not positions:
        position_numbers = [pos for pos, token in enumerate(token_sequence)]
        input_container.ic_log.add_log(
            "ALL_POSITIONS",
            element_id=element.get_ic_id(),
            child_system='universal:token',
            parent_system='universal:input',
            pos_list=position_numbers
        )
        input_container.ic_log.add_log(
            "DEAD_POSITIONS",
            element_id=element.get_ic_id(),
            child_system='universal:token',
            parent_system='universal:input',
            pos_list=[]
        )

    dead_pos = input_container.ic_log.get_log_sequence(
        "DEAD_POSITIONS",
        element_id=element.get_ic_id(),
        child_system='universal:token',
        parent_system='universal:input'
    )[0].get_prop('pos_list')

    sharp_return = False
    for n, token in enumerate(token_sequence):
        if n not in dead_pos and token == container_element.get_content():
            sharp_return = True
            dead_pos.append(n)
            input_container.ic_log.edit_log_document(
                "DEAD_POSITIONS",
                {
                    'element_id': element.get_ic_id(),
                    'child_system': 'universal:token',
                    'parent_system': 'universal:input'
                },
                0,
                dead_pos
            )
    return sharp_return


@new_sharp(parent_system='universal:token', child_system='universal:morpheme')
def morpheme_in_token(element, container_element, container, input_container):
    pass


class SharpFunctionNotFound(Exception):
    pass

