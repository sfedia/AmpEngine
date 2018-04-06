#!/usr/bin/python3
import structures_collection.char_level
import string


class HandlerStart:
    def __init__(self):
        self.segments = {}

    def segment(self, from_, to_):
        if (from_, to_) in self.segments:
            return self.segments[(from_, to_)]
        else:
            raise SegmentTemplateNotFound()

    def is_auto(self, system_name):
        for key in self.segments:
            if key[0] == system_name:
                return True
        return False

    def add_segment(self, from_, to_, func):
        self.segments[(from_, to_)] = func

    def can_segment(self, from_, to_):
        return (from_, to_) in self.segments

    def to_values(self):
        to_val = []
        for key in self.segments:
            to_val.append(key[1])
        return list(set(to_val))


# every function should return List


Handler = HandlerStart()


def segmentation(from_, to_):
    def segm_decorator(func):
        Handler.add_segment(from_, to_, func)

        def wrapped(function_arg1, function_arg2):
            return func(function_arg1, function_arg2)

        return wrapped
    return segm_decorator


def split_string(content, split_syms, alternate=[]):
    """
    `split_string` function
    :param content: string to split
    :param split_syms: symbol patterns to ignore and split
    :param alternate: symbol to be ignored before/after the main symbol group
    :return: Array of CharOutline objects (with attachment)
    """

    start = 0
    extracted_values = []
    after_ss = False
    addition_state = False
    for e, char in enumerate(content):
        if e > 0 and char in split_syms or (char in alternate and after_ss):
            if char in split_syms:
                after_ss = True
            if not addition_state:
                extracted_values.append(
                    structures_collection.char_level.CharOutline([start, e - 1], attachment=content[start:e])
                )
                addition_state = True
            start = e + 1
        elif char not in split_syms:
            addition_state = False
            after_ss = False
    if start < len(content) - 1:
        extracted_values.append(
            structures_collection.char_level.CharOutline([start, len(content) - 1], attachment=content[start:])
        )
    return extracted_values


@segmentation('universal:input', 'universal:sentence')
def input_to_sentences(content, metadata=None):
    """
    :param content: IC element content
    :param metadata: incidental metadata (optional)
    :return: Array of CharOutline objects (with attachment)
    """
    return split_string(content, [".", "!", "?"], alternate=[" "])


@segmentation('universal:sentence', 'universal:token')
def sentence_to_tokens(content, metadata=None):
    """
    :param content: IC element content
    :param metadata: incidental metadata (optional)
    :return: Array of CharOutline objects (with attachment)
    """

    return split_string(content, [x for x in string.punctuation], alternate=[" "])


class SegmentTemplateNotFound(Exception):
    pass
