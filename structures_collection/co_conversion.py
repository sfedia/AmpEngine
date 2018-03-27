#!/usr/bin/python3
import structures_collection.char_level
import string
import collections
import re
import grammar


class HandlerStart:
    def __init__(self):
        self.conversions = {}

    def conversions(self, from_, to_):
        if (from_, to_) in self.conversions:
            return self.conversions[(from_, to_)]
        else:
            raise SegmentTemplateNotFound()

    def add_conversion(self, from_, to_, func):
        self.conversions[(from_, to_)] = func

    def can_convert(self, from_, to_):
        return (from_, to_) in self.conversions

    def to_values(self):
        to_val = []
        for key in self.conversions:
            to_val.append(key[1])
        return list(set(to_val))


# every function should return List


Handler = HandlerStart()


class Conversion:
    def __init__(self):
        self.__match_fc = {}

    def add_match(self, a, b, regex_before=(0, None), regex_after=(0, None)):
        if not a:
            raise ValueError()
        if a[0] not in self.__match_fc:
            self.__match_fc[a[0]] = {}
        self.__match_fc[a[0]][(regex_before, a, regex_after)] = b

    def char_request(self, index, co_sequence):
        conv_actions = []

        for properties in self.__match_fc[co_sequence[index]]:
            if properties[2][0] < len(co_sequence[index + 1:]):
                continue
            elif not re.search(properties[2][1], co_sequence[index+1:index+1+properties[2][0]]):
                continue
            if properties[0][0] < len(co_sequence[:index]):
                continue
            elif not re.search(properties[0][1], co_sequence[index-properties[0][1]:index]):
                continue

            if index + len(properties[1]) >= len(co_sequence):
                continue

            conv_actions += ConvActionsGenerator(
                range(index, index + len(properties[1])),
                [x for x in self.__match_fc[co_sequence[index]][properties]]
            )

        if not conv_actions:
            return [ConvAction('Equal', [index], [co_sequence[index]])]
        else:
            return conv_actions


class ConvActionsGenerator:
    def __init__(self, int_list, rep_list):
        self.generated_ca = []
        if len(int_list) >= len(rep_list):
            x = int_list[0]
            for i in int_list:
                if i - x < len(rep_list):
                    self.generated_ca.append(ConvAction(i, rep_list[i - x], 'Equal'))
                else:
                    self.generated_ca.append(ConvAction(i, None, 'Remove'))
        else:
            x = int_list[0]
            for j, r in enumerate(rep_list):
                if j < len(int_list):
                    self.generated_ca.append(ConvAction(x + j, r, 'Equal'))
                else:
                    self.generated_ca.append(ConvAction(x + j, r, 'Add'))
        
    def get(self):
        return self.generated_ca
    
    
class ConvAction:
    def __init__(self, int_index, rep_char, action_type):
        if action_type not in ('Equal', 'Remove', 'Add'):
            raise ValueError
        self.__action_type = action_type
        self.__int_index = int_index
        self.__rep_char = rep_char

    def what(self):
        return self.__action_type

    @staticmethod
    def reverse_action(action):
        if action == 'Equal':
            return action
        return 'Add' if action == 'Remove' else 'Remove'

    def create_reversed(self, back_value):
        return ConvAction(
            self.__int_index,
            back_value,
            self.reverse_action(self.__action_type)
        )

    def get(self, shift=0):
        return (
            self.__action_type,
            self.__int_index + shift,
            self.__rep_char,
            0 if self.__action_type == 'Equal' else 1 if self.__action_type == 'Add' else -1
        )


class ConvSubHistory:
    def __init__(self, conversion, input_container):
        self.__conversion = conversion
        self.__input_container = input_container
        self.__subhistory = []
        self.__back = []
        self.__shifts = []
        input_sequence = self.__input_container.get_system_name('universal:input')[0].get_content()
        skip_char = 0
        for j, char in enumerate(input_sequence):
            if skip_char:
                skip_char -= 1
                continue
            creq = self.__conversion.char_request(j, input_sequence)
            for x, ca in enumerate(creq):
                self.__shifts.append(ca.get(sum(self.__shifts))[3])
                self.__subhistory.append(ca)
                if ca.get()[0] in ('Equal', 'Remove'):
                    self.__back.append(input_sequence[j + x])
                else:
                    self.__back.append(None)
            skip_char = len(creq) - 1

    def get_whole(self, rev=False):
        subhistory = collections.namedtuple('SubHistory', 'subhistory, back, shifts')
        if not rev:
            return subhistory(
                self.__subhistory,
                self.__back,
                self.__shifts
            )
        else:
            revb = reversed(self.__back)
            return subhistory(
                [ca.create_reversed(revb[j]) for j, ca in enumerate(self.__subhistory)],
                revb,
                reversed(self.__shifts)
            )


class LayerConversion:
    def __init__(self, subhistory, input_container):
        self.layers = input_container.get_system_names()
        self.subhistory = subhistory
        self.input_container = input_container

    def convert_layer(self, layer_name, rev=False):
        layer_elements = self.input_container.get_by_system_name(layer_name)
        if not layer_elements:
            return []
        clusters = {}
        for le in layer_elements:
            if le.get_parent_ic_id() not in clusters:
                clusters[le.get_parent_ic_id()] = []
            clusters[le.get_parent_ic_id()].append(le)

        clustered_gc = [grammar.GroupCollection(clusters[x], x, self.input_container) for x in clusters]

        cum_shift = 0

        for j, a in enumerate(self.subhistory):
            act_type, act_index, act_rc, act_shift = a.get(cum_shift)
            cum_shift += act_shift
            for n, pid_gc in enumerate(clustered_gc):
                for i, group in pid_gc.group(index_pair=True):
                    for l, elem in enumerate(group):
                        start_index = None
                        for num, index in en

        for j, a in enumerate(self.subhistory):
            act_type, act_indices, act_repls, act_shift = a.get(cum_shift)
            cum_shift += act_shift
            for n, pid_gc in enumerate(clustered_gc):
                for i, group in pid_gc.groups(index_pair=True):
                    for l, elem in enumerate(group):
                        start_index = None
                        for num, index in enumerate(elem.get_char_outline()):
                            if index in act_indices:
                                start_index = index
                                break
                            if act_type == 'Divide':
                                ...

                left_margin = pid_gc.group(0)[0].get_char_outline().get_groups()[0][0]
                right_margin = pid_gc.group(0)[-1].get_char_outline().get_groups()[0][-1]
                if left_margin <= act_indices[0] <= right_margin:
                    for i, group in pid_gc.groups(index_pair=True):
                        if act_type == 'Divide':
                            clustered_gc[n].groups[i]


            for n, pid_gc in enumerate(clustered_gc):



        """for j, gc in enumerate(clustered_gc):
            for i, group in gc.groups(True):
                clustered_gc[j].groups[i] = ..."""

    @staticmethod
    def shift(group, shift_int, start_int, rev=False, elem_index=None):
        """
        :param group: [List] group containing IC elements
        :param shift_int:
        :param start_int:
        :param rev: [Bool] reverse mode
        :param elem_index:
        :return: changed group
        """
        if not rev:
            shift_set = group if not elem_index else group[elem_index:]
        else:
            shift_set = group if not elem_index else group[:elem_index+1]

        for elem in shift_set:
            elem_co = elem.get_char_outline()
            elem_co.shift_group(0, shift_int, start_int, rev)
            elem.char_outline = elem_co

        if not rev:
            return group[:elem_index] + shift_set
        else:
            return shift_set + group[elem_index+1:]


def regressive_conversion(from_, to_):
    def rc_decorator(func):
        Handler.add_conversion(from_, to_, func)

        def wrapped(function_arg1, function_arg2):
            return func(function_arg1, function_arg2)

        return wrapped
    return rc_decorator


class SegmentTemplateNotFound(Exception):
    pass
