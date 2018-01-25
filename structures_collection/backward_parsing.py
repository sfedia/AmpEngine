#!/usr/bin/python3

import itertools


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

    morpheme_maps = {}
    
    def segment_forward(chars, start, dead_pos, position):
        if start >= len(chars):
            raise InternalParserException()
        
        morphemes = container.iter_content_filter(
            lambda x: x.startswith(chars[start]), sort_desc=True, system_filter='universal:morpheme'
        )
        if not morphemes:
            raise InternalParserException()
        
        morpheme_found = False
        position_index = 0
        
        for morph_object in morphemes:
            morpheme_pos = []
            catch_pos = []

            for j in range(start, len(chars)):
                if j in dead_pos:
                    continue
                if (j - start) == len(morph_object.get_content()):
                    break

                if chars[j] == morph_object.get_content()[j - start] and len(catch_pos) < len(morph_object.get_content()):
                    catch_pos.append(j)
                elif len(catch_pos) < len(morph_object.get_content()):
                    catch_pos = []
                elif len(catch_pos) == len(morph_object.get_content()):
                    morpheme_pos.append(catch_pos)
                    catch_pos = []
                else:
                    raise InternalParserException()

            if len(catch_pos) == len(morph_object.get_content()):
                morpheme_pos.append(catch_pos)

            if not morpheme_pos:
                continue
            morpheme_found = True

            for e, _ in enumerate(morpheme_pos):
                perms = list(itertools.permutations(morpheme_pos, e + 1))
                for perm in perms:
                    local_new_key = tuple(list(position) + [position_index])
                    morpheme_maps[local_new_key] = {morph_object.get_id(): perm}

                    local_dead_pos = dead_pos[:]
                    local_dead_pos += itertools.chain(*perm)
                    local_dead_pos = list(set(local_dead_pos))
                    local_dead_pos.sort()

                    start_integer = None
                    for ii, i in enumerate(local_dead_pos):
                        if not ii:
                            continue
                        if local_dead_pos[ii - 1] - local_dead_pos[ii] > 1:
                            start_integer = local_dead_pos[ii - 1] + 1
                            break

                    if not start_integer:
                        start_integer = local_dead_pos[-1] + 1

                    try:
                        segment_forward(chars, start_integer, local_dead_pos, local_new_key)
                    except InternalParserException:
                        morpheme_maps[tuple(list(local_new_key) + [0])] = None
                    position_index += 1

        if not morpheme_found:
            raise InternalParserException()


class ParserNotFound(Exception):
    pass


class InternalParserException(Exception):
    pass
