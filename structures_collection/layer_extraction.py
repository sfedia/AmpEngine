#!/usr/bin/python3

'''
Layer extraction functions should require parent `element` and new `content` arguments
Return: ic_id of extracted input container element
'''


class HandlerStart:
    def __init__(self):
        self.extracts = {}

    def extract(self, from_, to_):
        if (from_, to_) in self.extracts:
            return self.extracts[(from_, to_)]
        else:
            raise NoSuchSegmentTemplate()

    def add_extract(self, from_, to_, func):
        self.extracts[(from_, to_)] = func


Handler = HandlerStart()


def extraction(from_, to_):

    def segm_decorator(func):
        Handler.add_extract(from_, to_, func)

        def wrapped(function_arg1):
            return func(function_arg1)

        return wrapped

    return segm_decorator


@extraction('universal:token', 'universal:morpheme')
def token_to_morphemes(parent_element, content):
    # remove all elements that are childs of parent_element (ic_id)
    # get parent ic_id logs and sort the positions
    # segment_element with the new `content` again
    pass


class NoSuchSegmentTemplate(Exception):
    pass
