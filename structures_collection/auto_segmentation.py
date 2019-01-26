#!/usr/bin/python3
import re
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


def re_split2co(text, split_regex, catch_group=0):
    split_ranges = [
        range(splitter.start(catch_group), splitter.end(catch_group)) for splitter in re.finditer(split_regex, text)
        if splitter.start(catch_group) != -1
    ]
    result = list()
    begin = 0
    for n, split_range in enumerate(split_ranges):
        from_, to_ = split_range
        if from_ != 0:
            result.append(
                structures_collection.char_level.CharOutline([begin, from_ - 1], attachment=text[begin:from_])
            )
            begin = to_ + 1
        elif n < len(split_ranges) - 1:
            b_from_ = split_ranges[n + 1][0]
            result.append(
                structures_collection.char_level.CharOutline([to_, b_from_ - 1], attachment=text[to_:b_from_])
            )
            begin = to_ + 1
        else:
            result.append(
                structures_collection.char_level.CharOutline([to_ + 1, len(text) - 1], attachment=text[to_ + 1:])
            )
    return result if result else [structures_collection.char_level.CharOutline([0, len(text) - 1], attachment=text)]


@segmentation('universal:input', 'universal:sentence')
def input_to_sentences(content, metadata=None):
    """
    :param content: IC element content
    :param metadata: incidental metadata (optional)
    :return: Array of CharOutline objects (with attachment)
    """
    return re_split2co(content, r'(^|[^\s]{2,})([\.!\?]\s*)', catch_group=2)


@segmentation('universal:sentence', 'universal:token')
def sentence_to_tokens(content, metadata=None):
    """
    :param content: IC element content
    :param metadata: incidental metadata (optional)
    :return: Array of CharOutline objects (with attachment)
    """

    return re_split2co(content, r'[!"#\$%&\'\(\)\*\+,\.\/\:\;<=>?\@[\\\]^_`{|}~«»„“–—\s]+')


class SegmentTemplateNotFound(Exception):
    pass
