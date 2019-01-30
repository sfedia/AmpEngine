#!/usr/bin/python3

import output_templates.tsakorpus_encode as tsa_encode
import grammar
import json
import string


class Template:
    def __init__(self, container):
        self.container = container

    def run(self, input_container, **kwargs):
        sentences = input_container.get_by_system_name('universal:sentence')
        tsa_encoder = tsa_encode.Encode()
        if not sentences:
            raise InputContainerIsEmpty()
        document_object = {
            "meta": kwargs["meta"],
            "sentences": []
        }
        for sentence in sentences:
            start_point = sentence.get_char_outline().get_groups()[0]
            print('SP', start_point)
            sentence_gc = grammar.GroupCollection(
                sentence.get_ic_id(),
                input_container,
                elements=sentence.get_childs(lambda el: el.get_system_name() == 'universal:token')
            )
            sentence_object = {
                "text": sentence.get_content() + ".",
                "words": [],
                "lang": 0,
                "meta": kwargs["meta"]
            }
            for token in sentence_gc.group(0):
                off_start, off_end = token.get_char_outline().get_groups()
                print(off_start, off_end)
                token_object = {
                    "wf": token.get_content(),
                    "wtype": "word",
                    "off_start": off_start,
                    "off_end": off_end + 1,
                    "next_word": -1,
                    "sentence_index": -1
                }
                ana_elements = [token] + input_container.get_by_fork_id(token.get_ic_id())
                analyses = []
                for e, element in enumerate(ana_elements):
                    element_morph = grammar.GroupCollection(
                        element.get_ic_id(),
                        input_container,
                        elements=token.get_childs(lambda tkn: tkn.get_system_name() == 'universal:morpheme')
                    )
                    em_itergroups = element_morph.itergroups(index_pair=True)
                    if not em_itergroups:
                        try:
                            translation = token.get_parameter('mansi:translation')
                            analyses.append({
                                "trans_ru": translation
                            })
                        except grammar.ParameterNotFound:
                            pass
                    for j, group in em_itergroups:
                        try:
                            log_stem = input_container.ic_log.get_log_sequence(
                                "STEMS_EXTRACTED", element_id=token.get_ic_id(), group=e if e else None
                            )[0].get_prop('positions')
                            lex_stem = token.get_content()[log_stem[0]:log_stem[-1] + 1]
                        except IndexError:
                            lex_stem = token.get_content()
                        full_lemma = token.get_parameter('mansi:full_lemma')
                        group_text = ""
                        group_props = {}
                        group_gloss = ""
                        group_parts = ""
                        try:
                            translation = token.get_parameter('mansi:translation')
                        except grammar.ParameterNotFound:
                            translation = ""
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
                            group_gloss += "-" + ".".join(markers)
                            group_text += "{%s}" % (morpheme.get_content())
                            group_parts += "-" + morpheme.get_content()
                        group_text += "-"

                        print("Group:")
                        group_object = dict()
                        group_object['lex'] = full_lemma
                        group_object['parts'] = lex_stem + group_parts
                        group_object['gloss'] = "STEM" + group_gloss
                        group_object['gloss_index'] = "STEM{%s}" % lex_stem + group_text
                        for gprop in group_props:
                            group_object[gprop] = group_props[gprop]
                        group_object['trans_ru'] = translation
                        print(group_object)
                        analyses.append(group_object)
                        #print(group_text)
                        #print(group_parts)
                        #print(group_gloss)
                        #print(group_props)
                        #print(lex_stem)
                        #print(translation)
                if analyses:
                    token_object["ana"] = analyses
                print(token_object)
                sentence_object["words"].append(token_object)
            for j, char in enumerate(sentence.get_content()):
                if char in string.punctuation:
                    sentence_object["words"].append({
                        "wf": char,
                        "wtype": "punct",
                        "off_start": j,
                        "off_end": j + 1,
                        "next_word": -1,
                        "sentence_index": -1
                    })
            sentence_object["words"] = sorted(sentence_object["words"], key=lambda w: w["off_start"])
            start_index = 0
            if sentence_object["words"][0]["wtype"] == "punct":
                start_index = 1
            g = 0
            for i in range(start_index, len(sentence_object["words"])):
                sentence_object["words"][i]["next_word"] = i + 1
                sentence_object["words"][i]["sentence_index"] = g
                g += 1
            sentence_object["words"].append({
                "wf": ".",
                "wtype": "punct",
                "off_start": sentence_object["words"][-1]["off_end"] + 1,
                "off_end": sentence_object["words"][-1]["off_end"] + 2,
                "next_word": sentence_object["words"][-1]["next_word"] + 1
            })
            document_object["sentences"].append(sentence_object)
        return json.dumps(document_object, indent=2)



class InputContainerIsEmpty(Exception):
    pass
