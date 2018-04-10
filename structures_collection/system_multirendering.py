#!/usr/bin/python3

import collections
import re


class HandlerStart:
    def __init__(self):
        self.multirenderers = {}
        self.renderable = {}

    def is_renderable(self, a_system):
        return a_system in self.renderable

    def render(self, from_, mc_c, mc_id):
        if self.is_renderable(from_):
            return self.multirenderers[self.renderable[from_]](from_, mc_c, mc_id)
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
    rend_object = collections.namedtuple('RenderedMC', 'type content id')

    if mce_content.startswith('^'):
        mce_spec = '^'
        rendered_content = mce_content[1:]
        dfix_search = re.search(r'^\$\[([^\]]+)\]', rendered_content)
        start_vow = [x for x in 'ёуеыаоэяию']
        jot_subst = {
            'э': 'е',
            'о': 'ё',
            'а': 'я',
            'у': 'ю',
            'ы': 'и',
            'и': 'ы',
            'е': 'э'
        }
        jot_vow = [x for x in 'эоауыеи']
        sv_length = len(start_vow)
        if dfix_search:
            fixed_vow = dfix_search.group(1)
            final_part = rendered_content[len(dfix_search.group(0)):]
            return [
                rend_object(
                    'universal:morpheme',
                    mce_spec + fixed_vow + final_part,
                    mce_id + generate_renderer_postfix(renderer_code, 0)
                ),
                rend_object(
                    'universal:morpheme',
                    mce_spec + final_part,
                    mce_id + generate_renderer_postfix(renderer_code, 1)
                ),
            ]
        else:
            if rendered_content[0] not in jot_vow:
                return [rend_object(
                    'universal:morpheme',
                    mce_spec + vow + rendered_content,
                    mce_id + generate_renderer_postfix(renderer_code, n)
                ) for n, vow in enumerate(start_vow)] + [
                    rend_object(
                        'universal:morpheme',
                        mce_spec + rendered_content,
                        mce_id + generate_renderer_postfix(renderer_code, sv_length)
                    )
                ]
            else:
                return [
                    rend_object(
                        'universal:morpheme',
                        mce_spec + jot_subst[rendered_content[0]] + rendered_content[1:],
                        mce_id + generate_renderer_postfix(renderer_code, 0)
                    ),
                    rend_object(
                        'universal:morpheme',
                        mce_spec + rendered_content,
                        mce_id + generate_renderer_postfix(renderer_code, 1)
                    )
                ]

class MultirenderingTemplateNotFound(Exception):
    pass
