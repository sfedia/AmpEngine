#!/usr/bin/python3

import collections


class HandlerStart:
    def __init__(self):
        self.multirenderers = {}
        self.renderable = {}

    def is_renderable(self, a_system):
        return a_system in self.renderable

    def render(self, from_, mc_t, mc_c, mc_id):
        if self.is_renderable(from_):
            return self.multirenderers[self.renderable[from_]](mc_t, mc_c, mc_id)
        else:
            raise MultirenderingTemplateNotFound()

    def add_multirenderer(self, from_, to_, func):
        self.multirenderers[(from_, to_)] = func
        self.renderable[from_] = (from_, to_)


Handler = HandlerStart()


def multirenderer(from_, to_):
    def mrr_decorator(func):
        Handler.add_multirenderer(from_, to_, func)

        def wrapped(function_arg1, function_arg2):
            return func(function_arg1, function_arg2)

        return wrapped
    return mrr_decorator


def generate_renderer_postfix(code, n):
    return '@gen_%s_%i' % (code, n)


@multirenderer('mansi:VowMorpheme', 'universal:morpheme')
def mansi_vowmorpheme(mce_type, mce_content, mce_id):
    """
    mansi:VowMorpheme -> universal:morpheme
    (MC ID must look like ...@gen_CODE_n)
    :param mc_element: MC container element which belongs to A system
    :param mce_type: system name of MC container element
    :param mce_content: content of MC container element
    :param mce_id: ID of MC container element
    :return: List of namedtuple -> (.type, .content, .id) properties rendered from the source (T,C,I)
    """

    renderer_code = 'MWM'
    ...


class MultirenderingTemplateNotFound(Exception):
    pass
