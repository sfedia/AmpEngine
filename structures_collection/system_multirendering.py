#!/usr/bin/python3


class HandlerStart:
    def __init__(self):
        self.multirenderers = {}
        self.renderable = {}

    def is_renderable(self, a_system):
        return a_system in self.renderable

    def render(self, from_, mc_element):
        if self.is_renderable(from_):
            return self.multirenderers[self.renderable[from_]](mc_element)
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


@multirenderer('mansi:VowMorpheme', 'universal:morpheme')
def mansi_vowmorpheme(mce_type, mce_content, mce_id):
    """
    mansi:VowMorpheme -> universal:morpheme
    :param mc_element: MC container element which belongs to A system
    :param mce_type: system name of MC container element
    :param mce_content: content of MC container element
    :param mce_id: ID of MC container element
    :return: List of (MCE_TYPE, MCE_CONTENT, MCE_ID) properties rendered from the source (T,C,I)
    """

    ...


class MultirenderingTemplateNotFound(Exception):
    pass
