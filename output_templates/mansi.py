#!/usr/bin/python3
import grammar
import json


class Template:
    def __init__(self, container):
        self.container = container

    def run(self, input_container, **kwargs):
        result = ""
        sentences = input_container.get_by_system_name('universal:sentence')
        if not sentences:
            raise InputContainerIsEmpty()
        for sentence in sentences:
            tokens = sentence.get_childs(lambda tkn: tkn.get_system_name() == 'universal:token')
            for token in tokens:
                print("Token: %s" % (token.get_content()))
                token_gc = grammar.GroupCollection(
                    token.get_childs(lambda tkn: tkn.get_system_name() == 'universal:morpheme')
                )
                for group in token_gc.groups():
                    for element in group:
                        ...


class InputContainerIsEmpty(Exception):
    pass

