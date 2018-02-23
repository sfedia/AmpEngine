#!/usr/bin/python3
import grammar
from output_templates import lgr_action as lgr
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
                    token.get_childs(lambda tkn: tkn.get_system_name() == 'universal:morpheme'),
                    token.get_ic_id(),
                    input_container
                )
                for group in token_gc.groups():
                    # get stem and print it
                    group_text = ""
                    group_markers = ""
                    for morpheme in group:
                        group_text += "-" + morpheme.get_content()
                        morpheme_markers = []
                        for action in self.container.get_by_id(morpheme.mc_id_link).get_actions():
                            morpheme_markers.append(
                                lgr.lgr_values[action](action) if action.get_path() in lgr.lgr_values else '?'
                            )
                        group_markers += "-" + ".".join(morpheme_markers)
                    print("Group:")
                    print(group_text)
                    print(group_markers)




class InputContainerIsEmpty(Exception):
    pass

