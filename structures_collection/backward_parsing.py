#!/usr/bin/python3

import itertools
import grammar
import structures_collection.char_level
import structures_collection.minor as mnr


class HandlerStart:
    def __init__(self):
        self.parsers = {}

    def get_parser(self, parent_system, child_system):
        if (parent_system, child_system) in self.parsers:
            return self.parsers[(parent_system, child_system)]
        else:
            raise ParserNotFound(parent_system, child_system)

    def add_parser(self, parent_system, child_system, func):
        self.parsers[(parent_system, child_system)] = func

    def to_values(self, parent_system):
        return [x[1] for x in self.parsers if x[0] == parent_system]


Handler = HandlerStart()


def new_parser(parent_system, child_system):
    def parser_decorator(func):
        Handler.add_parser(parent_system, child_system, func)

        def wrapped(function_arg1):
            return func(function_arg1)

        return wrapped
    return parser_decorator


class SegmentForward:
    def __init__(self, container):
        self.__maps = {}
        self.container = container

    def generate_map(self, chars, start, dead_pos, position):
        print('DP', dead_pos)
        while start in dead_pos:
            start += 1

        if start >= len(chars):
            raise InternalParserException()

        morphemes = self.container.iter_content_filter(
            lambda x: mnr.Clear.remove_spec_chars('universal:morpheme', x).startswith(chars[start]),
            sort_desc=True,
            system_filter='universal:morpheme'
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
                if (j - start) == len(morph_object.get_clear_content()):
                    break

                mcnt = morph_object.get_clear_content()
                if len(catch_pos) < len(mcnt) and chars[j] == mcnt[j - start]:
                    catch_pos.append(j)
                elif len(catch_pos) < len(morph_object.get_clear_content()):
                    catch_pos = []
                elif len(catch_pos) == len(morph_object.get_clear_content()):
                    morpheme_pos.append(catch_pos)
                    catch_pos = []
                else:
                    raise InternalParserException()

            if len(catch_pos) == len(morph_object.get_clear_content()):
                morpheme_pos.append(catch_pos)

            if not morpheme_pos:
                continue
            morpheme_found = True

            for e in range(len(morpheme_pos)):
                perms = list(itertools.permutations(morpheme_pos, e + 1))
                for perm in perms:
                    local_new_key = position + (position_index,)
                    self.__maps[local_new_key] = {morph_object.get_id(): perm}

                    local_dead_pos = dead_pos[:] + list(itertools.chain(*perm))
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
                        self.generate_map(chars, start_integer, local_dead_pos, local_new_key)
                    except InternalParserException:
                        self.__maps[local_new_key + (0,)] = None
                    position_index += 1

        if not morpheme_found:
            raise InternalParserException()

    def get_result(self):
        return self.__maps

    @staticmethod
    def create_map_sequence(maps, key):
        sequence = []
        while len(key) >= 2:
            sequence.insert(0, maps[key])
            key = tuple(x for x in key[:-1])
        return sequence


def decode_asterisk_pattern(pattern):
    pattern = pattern.replace('\\', '')
    return 'class' if pattern[1] == '.' else 'id', pattern[2:-1]


def get_null_id(decoded_value, container):
    if decoded_value[0] == 'id':
        return decoded_value[1]
    elif decoded_value[0] == 'class':
        class_elements = container.get_class(decoded_value[1])
        for element in class_elements:
            if element == grammar.Temp.NULL:
                return element.get_id()
        return None
    else:
        raise ValueError()


@new_parser(parent_system='universal:token', child_system='universal:morpheme')
def morpheme_in_token(input_container_element, container, input_container):
    if input_container.ic_log.get_sector("STEMS_EXTRACTED") is None:
        raise InternalParserException('No stem extractor provided')
    stems = input_container.ic_log.get_log_sequence("STEMS_EXTRACTED", element_id=input_container_element.get_ic_id())
    if not stems:
        raise InternalParserException(
            'No stems found for <{}> (={})'.format(
                input_container_element.get_ic_id(), input_container_element.get_content()
            )
        )

    group_index = 0
    for n, stem in enumerate(stems):
        sf_object = SegmentForward(container)
        # should be spec-dependent
        print((input_container_element.get_content(), 0, stem.get_prop('positions'), (0,)))
        sf_object.generate_map(
            input_container_element.get_content(), start=0, dead_pos=stem.get_prop('positions'), position=(0,)
        )
        morpheme_maps = sf_object.get_result()
        morpho_seqs = []
        for morph_key in morpheme_maps:
            if morpheme_maps[morph_key] is None:
                continue
            [(v, group_holder)] = morpheme_maps[morph_key].items()
            for group in reversed(group_holder):
                if group[-1] == len(input_container_element.get_content()) - 1:
                    morpho_seqs.append(sf_object.create_map_sequence(morpheme_maps, morph_key))
                    break

        # seq: List of Dict(a => b, c => d)
        filtered_seqs = []
        grammar_nulls = container.iter_content_filter(lambda x: x == grammar.Temp.NULL, system_filter='universal:morpheme')
        for seq in morpho_seqs:
            id_list = [container.get_by_id(list(x.keys())[0]) for x in seq]
            available_nulls = []
            bsid_obj = id_list
            for null in grammar_nulls:
                for link in null.get_applied()['links']:
                    # BS Array
                    lc_bool, bsid_obj, input_container_element = link.check(
                        input_container_element, bsid_obj, lambda x: True, return_bs=True
                    )
                    if lc_bool:
                        available_nulls.append(null)

            subcl_orders = container.get_system('universal:morpheme').get_subcl_orders_affecting_ids(id_list)
            strict_prohib = False
            for order in subcl_orders:
                order_check = order.check_sequence(order, available_nulls)
                if not order_check['check'] and order.is_strict():
                    strict_prohib = True
                elif order.is_strict() and strict_prohib:
                    strict_prohib = False
                if strict_prohib:
                    continue
                if order_check['nulls']:
                    for null in order_check['nulls']:
                        if null['pre']:
                            for pre in null['pre']:
                                dec_value = decode_asterisk_pattern(pre)
                                for j, seq_el in enumerate(seq):
                                    if (dec_value[0] == 'id' and seq_el == dec_value[1]) or \
                                    (dec_value[0] == 'class' and dec_value[1] in container.get_by_id(seq_el).get_class_names()):
                                        prev_elem_pos = list(seq[j].keys())[0]
                                        virtual_list = [-1, (prev_elem_pos[0] if prev_elem_pos[0] != -1 else prev_elem_pos[1])]
                                        if j < len(seq) - 1:
                                            next_elem_pos = list(seq[j + 1].keys())[0]
                                            virtual_list.append(next_elem_pos[0] if next_elem_pos[0] != -1 else next_elem_pos[1])
                                        seq.insert(
                                            j + 1,
                                            {
                                                get_null_id(decode_asterisk_pattern(null['rx']), container): [virtual_list]
                                            }
                                        )
                        elif null['post']:
                            for post in null['post']:
                                dec_value = decode_asterisk_pattern(post)
                                for j, seq_el in enumerate(seq):
                                    if j == 0:
                                        continue
                                    if (dec_value[0] == 'id' and seq_el == dec_value[1]) or \
                                    (dec_value[0] == 'class' and dec_value[1] in container.get_by_id(seq_el).get_class_names()):
                                        next_elem_pos = list(seq[j].keys())[0]
                                        virtual_list = [-1, (next_elem_pos[0] if next_elem_pos[0] != -1 else next_elem_pos[1])]
                                        if j > 0:
                                            prev_elem_pos = list(seq[j - 1].keys())[0]
                                            virtual_list.append(prev_elem_pos[0] if prev_elem_pos[0] != -1 else prev_elem_pos[1])
                                        seq.insert(
                                            j - 1,
                                            {
                                                get_null_id(decode_asterisk_pattern(null['rx']), container): [virtual_list]
                                            }
                                        )
                        else:
                            # UNALLOCATED
                            ...

            if strict_prohib:
                continue

            filtered_seqs.append(seq)

        lnk_filtered_seqs = []
        for seq in filtered_seqs:
            add_to_lfs = True
            el_seq = [container.get_by_id(list(x.keys())[0]) for x in seq]
            for mc_element in el_seq:
                for link in mc_element.get_applied()['links']:
                    # BS Array
                    if not link.check(input_container_element, el_seq, lambda: True):
                        add_to_lfs = False
                        break
                if not add_to_lfs:
                    break
            if add_to_lfs:
                lnk_filtered_seqs.append(seq)

        for j, seq in enumerate(lnk_filtered_seqs):
            co_list = []
            for seq_element in seq:
                element_id = list(seq_element.keys())[0]
                co_local = structures_collection.char_level.CharOutline(
                    [],
                    attachment=container.get_by_id(element_id).get_content(),
                    metadata={'mc_id': element_id}
                )
                for ci in seq_element[element_id]:
                    if ci[0] != -1:
                        co_local.add_group(structures_collection.char_level.CharIndexGroup(ci))
                    else:
                        co_local.add_group(structures_collection.char_level.CharIndexGroup(ci[1:], is_virtual=True))

            input_container.segment_element(input_container_element, 'universal:morpheme', co_list, set_group=group_index)
            group_index += 1

        group_index += 1


class ParserNotFound(Exception):
    pass


class InternalParserException(Exception):
    pass
