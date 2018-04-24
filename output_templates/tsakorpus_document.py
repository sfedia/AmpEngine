#!/usr/bin/python3

import output_templates.tsakorpus_encode as tsa_encode
import grammar
import json


class Template:
    def __init__(self, container):
        self.container = container

    def run(self, input_container, **kwargs):
        sentences = input_container.get_by_system_name('universal:sentence')
        tsa_encoder = tsa_encode.Encode()
        if not sentences:
            raise InputContainerIsEmpty()
        for sentence in sentences:
            sentence_gc = grammar.GroupCollection(
                sentence.get_ic_id(),
                input_container,
                elements=sentence.get_childs(lambda el: el.get_system_name() == 'universal:token')
            )
            for token in sentence_gc.group(0):
                ana_elements = [token] + input_container.get_by_fork_id(token.get_ic_id())
                for e, element in enumerate(ana_elements):
                    element_morph = grammar.GroupCollection(
                        element.get_ic_id(),
                        input_container,
                        elements=token.get_childs(lambda tkn: tkn.get_system_name() == 'universal:morpheme')
                    )
                    for j, group in element_morph.itergroups(index_pair=True):
                        try:
                            log_stem = input_container.ic_log.get_log_sequence(
                                "STEMS_EXTRACTED", element_id=token.get_ic_id(), group=e if e else None
                            )[0].get_prop('positions')
                            lex_stem = token.get_content()[log_stem[0]:log_stem[-1]+1]
                        except IndexError:
                            lex_stem = token.get_content()
                        group_text = ""
                        group_props = {}
                        group_parts = ""
                        for morpheme in group:
                            morpheme_markers = []
                            for action in self.container.get_by_id(morpheme.mc_id_link).get_actions():
                                morpheme_markers.append(tsa_encoder.tsa_encode(action))
                            for m_group in morpheme_markers:
                                for m in m_group:
                                    group_props["gr." + m[1]] = m[0]
                            if morpheme.get_content() == grammar.Temp.NULL:
                                continue
                            markers = []
                            for marker in morpheme_markers:
                                print('Marker:', marker)
                                markers.append(".".join([x[0] for x in marker]))
                            group_text += "-" + ".".join(markers)
                            group_text += "{%s}" % (morpheme.get_content())
                            group_parts += "-" + morpheme.get_content()
                        group_text += "-"

                        print("Group:")
                        print(group_text)
                        print(group_parts)
                        print(group_props)
                        print(lex_stem)

class InputContainerIsEmpty(Exception):
    pass
