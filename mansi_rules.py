#!/usr/bin/python3
import grammar
import log_handler
from collections import Counter
from trie_stemmer.word_entry import WordEntry
import trie_stemmer.stemmer
import copy
import os
import json
import structures_collection as coll
import output_templates
import re

# ...
# first we should check if the whole token exists in dictionaries
# parent layer switching due to [time limits] like universal:token < [universal:input -> mansi:SH_MOD] (like сь -> щ)
# analytic forms: free morphemes like {A B}
# mansi:VowMorpheme info see in prodotiscus/Research-Mansi
#
rombandeeva = grammar.Container()

# universal:syl_count OR mansi:syl_count ???
# should `syl_count` be used together with pre=() or it is set by default
# - universal:syl_count:* for VERBS, PRONOUNS etc.

# and other need-forms for other POS

#####

rombandeeva.add_element('universal:morpheme', '^та̄л', 'tāl_suffix').applied(
    *[
        grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
        [grammar.Action('sem:make_opposite')]  # CAR
    ]
)
#
rombandeeva.add_element('universal:morpheme', '^т', 't_caus_suffix').add_class('caus_suffixes') # CAUS
rombandeeva.add_element('mansi:VowMorpheme', '^лт', 'lt_caus_suffix').add_class('caus_suffixes') # CAUS
rombandeeva.add_element('universal:morpheme', '^пт', 'pt_caus_suffix').add_class('caus_suffixes')
rombandeeva.add_element('universal:morpheme', '^лтт', 'ltt_caus_suffix').add_class('caus_suffixes')
rombandeeva.add_element('universal:morpheme', '^тт', 'tt_caus_suffix').add_class('caus_suffixes')
for element in rombandeeva.get_by_class_name('caus_suffixes'):
    # or just element.applied ??
    rombandeeva.get_by_id(element.get_id()).applied(
        *[
            grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
            [
                grammar.Action('sem:make_causative')
            ]
        ]
    )

rombandeeva.add_element('universal:morpheme', '^л', 'l_trans_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:intransitive=()'),
    [
        grammar.Action('gram:make_transitive')
    ]
).add_class('trans_suffixes')

rombandeeva.get_system('universal:morpheme').subclasses_order(
   '? < .number_suffix <<>> .lps >> .case_suffix >> ?',
   # the next argument is optional
   parent_filter=grammar.LinkSentence(
      'universal:entity=(token) & mansi:basic_pos=(noun)',
      rombandeeva
   )
)

"""
rombandeeva.get_system('universal:morpheme').subclasses_order(
    '''
        :prefix +<<
        :root >>+
        .word_building_suffix & APPLIED~=(pos:(verb)) >>+
        .word_inflection_suffix & APPLIED~=(pos:(verb))
    ''',
    parent_filter=grammar.LinkSentence(
        'universal:entity=(token) & mansi:basic_pos=(verb)',
        rombandeeva
    )
)

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '? << :root >> ? >> .word_building_suffix >> .case_suffix >> ?',
    parent_filter=grammar.LinkSentence(
        'universal:entity=(token) & mansi:basic_pos=(noun)'
    )
)
"""

#
is_noun = '# & universal:entity=(token) & mansi:basic_pos=(noun) '

rombandeeva.add_element('universal:morpheme', grammar.Temp.NULL, 'number_noun_null_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:number:set_sing')]
    ]
).add_class('number_suffix')

rombandeeva.add_element('universal:morpheme', '^г', 'ɣ_number_suffix').applied(
    *[
        grammar.LinkSentence(is_noun + '& [ universal:end=(а) | universal:end=(е) | universal:end=(я) ]'),
        [grammar.Action('gram:number:set_dual')]
    ]
).add_class('number_suffix')

# твёрдые согласные?

rombandeeva.add_element('universal:morpheme', '^ыг', 'əɣ_number_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:number:set_dual')]
    ]
).add_class('number_suffix')

# мягкие согласные?

rombandeeva.add_element('universal:morpheme', '^яг', 'jaɣ_number_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:number:set_dual')]
    ]
).add_class('number_suffix')

lps_matrix = [
    ['sing', '1', 'ум', 'um'],
    ['sing', '2', 'ын', 'ən'],
    ['sing', '3', 'е', 'e'],
    ['dual', '1', 'ме̄н', 'mēn'],
    ['dual', '3', 'е̄н', 'ēn'],
    ['plur', '1', 'ув', 'uw'],
    ['plur', '3', 'а̄ныл', 'ānəl'],
]

for number, person, suffix, id in lps_matrix:
    rombandeeva.add_element('universal:morpheme', '^' + suffix, id + '_lp_suffix').add_class('lps').applied(
        *[
            grammar.LinkSentence(
                is_noun + '& gram:possessor:number=({0}) & gram:possessor:person=({0})'.format(number, person)
            ),
            [grammar.Action('mansi:make_lp', arguments=[number, person])]
        ]
    )

rombandeeva.add_element('universal:morpheme', '^ы̄н', 'ə̄n_suffix_lps_2sg').add_class('lps').applied(
    *[
        grammar.LinkSentence(
            is_noun + '& gram:possessor:number!=(sing) & gram:possessor:person=(2)'
        ),
        [
            grammar.Action('mansi:make_lp', arguments=['sing', '2'])
        ]
    ]
)
rombandeeva.add_element('universal:morpheme', '^ы̄н', 'ə̄n_suffix_lps_2du').add_class('lps').applied(
    *[
        grammar.LinkSentence(
            is_noun + '& gram:possessor:number!=(sing) & gram:possessor:person=(2)'
        ),
        [
            grammar.Action('mansi:make_lp', arguments=['dual', '2'])
        ]
    ]
)

rombandeeva.add_element('universal:morpheme', '^н', 'n_number_suffix').applied(
    *[
        grammar.LinkSentence(is_noun + '& [ universal:end=(а) | universal:end=(е) | universal:end=(э) ]'),
        [grammar.Action('gram:number:set_plur')]
    ]
).add_class('number_suffix')

# твёрдые согласные?

rombandeeva.add_element('universal:morpheme', '^ан', 'an_number_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:number:set_plur')]
    ]
).add_class('number_suffix')

# мягкие согласные?

rombandeeva.add_element('universal:morpheme', '^ян', 'jan_number_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:number:set_plur')]
    ]
).add_class('number_suffix')

rombandeeva.add_element('universal:morpheme', grammar.Temp.NULL, 'null_suffix_main_case').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_main')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^н', 'n_case_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_lat')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^ын', 'ən_case_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_lat')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^т', 't_case_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_loc')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^ыт', 'ət_case_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_loc')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^ныл', 'nəl_case_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_abl')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^л', 'l_case_suffix').applied(
    *[grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_instr')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^ыл', 'əl_case_suffix').applied(
    *[grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_instr')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^ил', 'əl2_case_suffix').applied(
    *[grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_instr')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^г', 'ɣ_case_suffix').applied(
    *[grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_trans')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^ыг', 'iɣ_case_suffix').applied(
    *[grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_trans')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^иг', 'iɣ2_case_suffix').applied(
    *[grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_trans')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('mansi:VowMorpheme', '^а', 'a_case_suffix_voc').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_voc')]
    ]
).add_class('case_suffix')

# page 70

is_verb = '# & universal:entity=(token) & mansi:basic_pos=(verb) '

## /

## warning: mutation strategy may be applied wrong to these elements <= is_verb is too broad for that

rombandeeva.get_class('infinitive_excl_suff', await=True).added_behaviour('override')

# infinitive!

rombandeeva.add_element('universal:morpheme', '^уӈкве', 'uŋkwe_infinitive_suffix').applied(
    *[
        grammar.LinkSentence(is_verb),
        [grammar.Action('gram:verb:set_infinitive')]
    ]
).add_class('infinitive_excl_suff').add_class('inf_suff')

rombandeeva.add_element('universal:morpheme', '^уӈкв', 'uŋkw_infinitive_suffix_short').applied(
    *[
        grammar.LinkSentence(is_verb),
        [grammar.Action('gram:verb:set_infinitive')]
    ]
).add_class('infinitive_excl_suff').add_class('inf_suff')

rombandeeva.add_element('universal:morpheme', '^юӈкве', 'juŋkwe_infinitive_suffix').applied(
    *[
        grammar.LinkSentence(is_verb),
        [grammar.Action('gram:verb:set_infinitive')]
    ]
).add_class('infinitive_excl_suff').add_class('inf_suff')

rombandeeva.add_element('universal:morpheme', '^юӈкв', 'juŋkw_infinitive_suffix_short').applied(
    *[
        grammar.LinkSentence(is_verb),
        [grammar.Action('gram:verb:set_infinitive')]
    ]
).add_class('infinitive_excl_suff').add_class('inf_suff')

rombandeeva.add_element('universal:morpheme', '^аӈкве', 'aŋkwe_infinitive_suffix').applied(
    *[
        grammar.LinkSentence(is_verb),
        [grammar.Action('gram:verb:set_infinitive')]
    ]
).add_class('infinitive_excl_suff').add_class('inf_suff')

rombandeeva.add_element('universal:morpheme', '^аӈкв', 'aŋkw_infinitive_suffix_short').applied(
    *[
        grammar.LinkSentence(is_verb),
        [grammar.Action('gram:verb:set_infinitive')]
    ]
).add_class('infinitive_excl_suff').add_class('inf_suff')

rombandeeva.add_element('universal:morpheme', '^ӈкве', 'ŋkwe_infinitive_suffix').applied(
    *[
        grammar.LinkSentence(is_verb),
        [grammar.Action('gram:verb:set_infinitive')]
    ]
).add_class('infinitive_excl_suff').add_class('inf_suff')

rombandeeva.add_element('universal:morpheme', '^ӈкв', 'ŋkw_infinitive_suffix_short').applied(
    *[
        grammar.LinkSentence(is_verb),
        [grammar.Action('gram:verb:set_infinitive')]
    ]
).add_class('infinitive_excl_suff').add_class('inf_suff')

# уп, ап, па, пи, п

rombandeeva.add_element('universal:morpheme', '^уп', 'up_wb_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun'),
            grammar.Action('mansi:sem:tool-or-action') # PROP2
        ]
    ]
).add_class('infinitive_excl_suff').add_class('word_building_suffix').add_class('verb_to_noun_suff')

rombandeeva.add_element('universal:morpheme', '^ап', 'ap_wb_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun'),
            grammar.Action('mansi:sem:tool-or-action')
        ]
    ]
).add_class('infinitive_excl_suff').add_class('word_building_suffix').add_class('verb_to_noun_suff')

rombandeeva.add_element('universal:morpheme', '^па', 'pa_wb_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun'),
            grammar.Action('mansi:sem:tool-or-action')
        ]
    ]
).add_class('infinitive_excl_suff').add_class('word_building_suffix').add_class('verb_to_noun_suff')

rombandeeva.add_element('universal:morpheme', '^пи', 'pi_wb_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun'),
            grammar.Action('mansi:sem:tool-or-action')
        ]
    ]
).add_class('infinitive_excl_suff').add_class('word_building_suffix').add_class('verb_to_noun_suff')

rombandeeva.add_element('universal:morpheme', '^п', 'p_wb_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun'),
            grammar.Action('mansi:sem:tool-or-action')
        ]
    ]
).add_class('infinitive_excl_suff').add_class('word_building_suffix').add_class('verb_to_noun_suff')


@rombandeeva.foreach_in_class('verb_to_noun_suff')
def ss_set_mutation_links(element):
    element.provide_mutation_links(
        [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)')]
    )


rombandeeva.add_element('universal:morpheme', '^т', 't_wb_from_noun_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:adj_to_noun'),
            grammar.Action('mansi:sem:obj-size')  # SBST.Q
        ]
    ]
).add_class('adj_ending_excl').add_class('word_building_suffix').add_class('adj_to_noun_suff')

rombandeeva.add_element('universal:morpheme', '^ит', 'it_wb_from_noun_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:adj_to_noun'),
            grammar.Action('mansi:sem:obj-size')
        ]
    ]
).add_class('adj_ending_excl').add_class('word_building_suffix').add_class('adj_to_noun_suff')

rombandeeva.add_element('universal:morpheme', '^та', 'ta_wb_from_noun_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:adj_to_noun'),
            grammar.Action('mansi:sem:obj-size')
        ]
    ]
).add_class('adj_ending_excl').add_class('word_building_suffix').add_class('adj_to_noun_suff')


@rombandeeva.foreach_in_class('adj_to_noun_suff')
def atn_set_mutation_links(element):
    element.provide_mutation_links(
        [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)')]
    )


# page 73, mutation scheme is complicated

rombandeeva.get_class('adj_ending_excl', await=True).added_behaviour('override')
# Need some universal:char_regex AS adj_ending_excl there??

rombandeeva.add_element('mansi:morphemeYU', '^т', 't_wb_from_verb_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun:size')
        ]
    ]
).add_class('verb_to_noun').add_class('yu.verb_ending_excl').add_class('verb_to_noun_suff')

rombandeeva.add_element('mansi:morphemeYU', '^ит', 'it_wb_from_verb_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun:size')
        ]
    ]
).add_class('verb_to_noun').add_class('yu.verb_ending_excl').add_class('verb_to_noun_suff')

rombandeeva.add_element('mansi:morphemeYU', '^та', 'ta_wb_from_verb_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun:size')
        ]
    ]
).add_class('verb_to_noun').add_class('yu.verb_ending_excl').add_class('verb_to_noun_suff')

### EDIT

rombandeeva.add_element('mansi:VowMorpheme', '^си', 'ɕi_coll_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:sem:coll') # COLL
        ]
    ]
)

rombandeeva.add_element('universal:morpheme', '^х', 'x_vn_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun')
        ]
    ]
).add_class('verb_to_noun').add_class('yu.verb_ending_excl').add_class('verb_to_noun_suff')

rombandeeva.add_element('universal:morpheme', '^ах', 'ax_vn_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun') # SBST
        ]
    ]
).add_class('verb_to_noun').add_class('yu.verb_ending_excl').add_class('verb_to_noun_suff')

rombandeeva.add_element('universal:morpheme', '^ум', 'um_suffix_sbst').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun') # SBST
        ]
    ]
).add_class('verb_to_noun').add_class('yu.verb_ending_excl').add_class('verb_to_noun_suff')

rombandeeva.add_element('universal:morpheme', '^м', 'm_suffix_sbst').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun')
        ]
    ]
).add_class('verb_to_noun').add_class('yu.verb_ending_excl').add_class('verb_to_noun_suff')
###


@rombandeeva.foreach_in_class('verb_to_noun_suff')
def vtn_set_mutation_links(element):
    element.provide_mutation_links(
        [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)')]
    )

## mansi:morphemeYU ^ункве < universal:morpheme ^ункве

rombandeeva.get_class('yu.verb_ending_excl', await=True).added_behaviour('override mutate>MUTATION')

rombandeeva.add_element('universal:char_regex', 'ololo', 'random2728').applied(
    grammar.LinkSentence('something'),
    [
        grammar.Action('MUTATION')
    ]
)

# LOTS OF WORD BUILDING SUFFIXES
# ... pages 72-75
#

# page 77

rombandeeva.add_element('universal:morpheme', '^нув', 'nuw_cmpr_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:adj:comparative')  # CMPR
    ]
)

rombandeeva.add_element('universal:morpheme', '^нуве', 'nuwe_cmpr_pred_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:adj:comparative'),
        grammar.Action('mansi:set_pred') # PRED
    ]
)

rombandeeva.add_element('universal:morpheme', '^кве', 'kwe_suffix_adj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_dimin')  # DIM
    ]
)

rombandeeva.add_element('universal:collocation', '''
    <[gram:case=(nom)]> *1 <[gram:case=(abl)]> *1 <[mansi:basic_pos=(adj) & gram:case=(nom)]>
''', 'analytic_comp').applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('gram:adj:comparative')
    ]
)


rombandeeva.add_element('universal:collocation', '''
    <[universal:content=(сяр) | universal:content=(сака)]> *1 <[mansi:basic_pos=(adj) & gram:case=(nom)]>
''', 'analytic_superlative').applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('gram:adj:superlative')
    ]
)

rombandeeva.add_element('universal:morpheme', '^ӈ', 'ŋ_attr_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_attr') # ATTR
    ]
).provide_mutation_links(
    [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(noun)')]
)

rombandeeva.add_element('universal:morpheme', '^ыӈ', 'əŋ_attr_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_attr')
    ]
).provide_mutation_links(
    [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(noun)')]
)

rombandeeva.add_element('universal:morpheme', '^иӈ', 'əŋ2_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_attr')
    ]
).provide_mutation_links(
    [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(noun)')]
)

# *** tal_suffix REF

rombandeeva.add_element('universal:morpheme', '^и', 'i_attr_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:noun_to_adj'),
        grammar.Action('sem:adj_to_noun_corresp')
    ]
)

rombandeeva.add_element('universal:morpheme', '^ы', 'i2_attr_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:noun_to_adj'),
        grammar.Action('sem:adj_to_noun_corresp')
    ]
)

# PARTICIPLE -> ADJ, not actually VERB -> ADJ

rombandeeva.add_element('mansi:morphemeYU', '^м', 'm_ptcp_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_participle')  # PTCP ; $INGORE_SEGMENTATION if token is found in dictionaries
    ]
).add_class('yu.verb_ending_excl').provide_mutation_links(
    [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)')]
)

rombandeeva.add_element('mansi:morphemeYU', '^ум', 'um_ptcp_suffix_participle').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_participle')
    ]
).add_class('yu.verb_ending_excl').provide_mutation_links(
    [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)')]
)

rombandeeva.add_element('mansi:morphemeYU', '^ам', 'am_ptcp_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_participle')
    ]
).add_class('yu.verb_ending_excl').provide_mutation_links(
    [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)')]
)

# page 83

#rombandeeva.add_element('universal:morpheme', 'ий', 'ij_rus_suffix').applied(
#    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
#    [
#        grammar.Action(grammar.Temp.NULL),
#        grammar.Action('mansi:russian_loan_word') # $IGNORE_SEGMENTATION
#    ]
#)

#rombandeeva.add_element('universal:morpheme', 'ый', 'ij2_rus_suffix').applied(
#    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
#    [
#        grammar.Action(grammar.Temp.NULL),
#        grammar.Action('mansi:russian_loan_word')
#    ]
#)

rombandeeva.add_element('universal:collocation', '''
    <[mansi:basic_pos=(noun) | mansi:basic_pos=(numeral)]> *1 <[mansi:basic_pos=(noun) & mansi:HAS_DerP=()]>
''', 'phrase_adj').applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('mansi:phrase_adj')
    ]
)

rombandeeva.add_element('universal:experimental:reduplication', 'яныг', 'janəɣ_redupl').applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('sem:magnification_colloc')
    ]
)

# ??? -ит -> -ит | -ыт ; page 87

rombandeeva.add_element('universal:morpheme', '^ит', 'it_ord_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(numeral)'),
    [
        grammar.Action('gram:set_ord')  # ORD
    ]
)

rombandeeva.add_element('universal:morpheme', '^ыт', 'it2_ord_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(numeral)'),
    [
        grammar.Action('gram:set_ord')
    ]
)

rombandeeva.add_element('universal:morpheme', '^иттыг', 'ittəɣ_mult_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(numeral)'),
    [
        grammar.Action('gram:set_mult') # MULT
    ]
)

rombandeeva.add_element('universal:morpheme', '^ынтыг', 'əntəɣ_mult_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(numeral)'),
    [
        grammar.Action('gram:set_mult')
    ]
)

rombandeeva.add_element('universal:collocation', '''
    <[mansi:basic_pos=(numeral) & [gram:numeral_cat=(cardinal) | gram:numeral_cat=(ordinal)]]>
    *1 <[universal:content=(сёс)]>
''', 'repet_numeral_colloc').applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('gram:numeral:co_to_repet_colloc')
    ]
)

# page 91 !!

rombandeeva.add_element('universal:morpheme', '^кем', 'kem_appr_suffix').applied(
    grammar.LinkSentence('''# & universal:entity=(token) & mansi:basic_pos=(numeral)
    & gram:numeral_cat=(cardinal)'''),
    [
        grammar.Action('gram:numeral:cardinal_to_round')
    ]
).add_class('kem_abstraction')

rombandeeva.get_class('kem_abstraction', await=True).added_behaviour('''
    prepend <universal:morpheme> ( (^ах) | (^ман) ) -> (0.5|0.5)
''')

rombandeeva.add_element('universal:collocation', '''
    <[mansi:basic_pos=(numeral)]> *1 <[universal:content=(суп) | universal:content=(па̄л)]>
''', 'num_partial_colloc').applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('mansi:numeral:partial_colloc')
    ]
)

# extract morphemes from tokens here

personal_pronouns = {
    '1SG': {
        'nom': 'ам',
        'acc': 'а̄нум',
        'dat': 'а̄нумн',
        'abl': 'а̄нумныл',
        'instr': 'а̄нумтыл',
    },
    '2SG': {
        'nom': 'наӈ',
        'acc': 'наӈын',
        'dat': 'наӈынн',
        'abl': 'наӈынныл',
        'instr': 'наӈынтыл',
    },
    '3SG': {
        'nom': 'тав',
        'acc': 'таве',
        'dat': 'таве̄н',
        'abl': 'таве̄ныл',
        'instr': 'таветыл',
    },
    '1DU': {
        'nom': 'ме̄н',
        'acc': 'ме̄нме̄н',
        'dat': 'ме̄нме̄нн',
        'abl': 'ме̄нме̄нныл',
        'instr': 'ме̄нме̄нтыл',
    },
    '2DU': {
        'nom': 'нэ̄н',
        'acc': 'нэ̄нан',
        'dat': 'нэ̄нанн',
        'abl': 'нэ̄нанныл',
        'instr': 'нэ̄нантыл',
    },
    '3DU': {
        'nom': 'тэ̄н',
        'acc': 'тэ̄нтэ̄н',
        'dat': 'тэ̄нтэ̄нн',
        'abl': 'тэ̄нтэ̄нныл',
        'instr': 'тэ̄нтэ̄нтыл',
    },
    '1PL': {
        'nom': 'ма̄н',
        'acc': 'ма̄нав',
        'dat': 'ма̄навн',
        'abl': 'ма̄навныл',
        'instr': 'ма̄навтыл'
    },
    '2PL': {
        'nom': 'на̄н',
        'acc': 'на̄нан',
        'dat': 'нананн',
        'abl': 'на̄нанныл',
        'instr': 'на̄нантыл'
    },
    '3PL': {
        'nom': 'та̄н',
        'acc': 'та̄наныл',
        'dat': 'та̄нанылн',
        'abl': 'та̄нанылныл',
        'instr': 'та̄нанылтыл'
    }
}

"""
for person_number in personal_pronouns:
    for case in personal_pronouns[person_number]:
        rombandeeva.add_element(
            'universal:token', personal_pronouns[person_number][case], 'pers_pron_{}.{}'.format(person_number, case)
        ).applied(
            grammar.LinkSentence('# & universal:entity=(input)'),
            [
                grammar.Action('mansi:pronoun:personal:' + person_number),
                grammar.Action('gram:case:set_' + case)
            ]
        )
"""

rombandeeva.add_element('universal:morpheme', '^ки', 'ki_emph_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(pronoun)'),
    [
        grammar.Action('mansi:pronoun:lich_ukaz') # EMPH
    ]
).add_class('lich_ukaz')

rombandeeva.add_element('universal:morpheme', '^кке', 'kke_sol_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(pronoun)'),
    [
        grammar.Action('mansi:pronoun:set_sol')  # SOL
    ]
).add_class('kke_suff')

rombandeeva.get_system('universal:morpheme').subclasses_order(
   '? <>> .kke_suff > .p_lps',
   parent_filter=grammar.LinkSentence(
      'universal:entity=(token) & mansi:basic_pos=(pronoun)',
      rombandeeva
   )
)

rombandeeva.add_element('universal:morpheme', '^на̄', 'nā_pron_refl_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(pronoun)'),
    [
        grammar.Action('gram:set_refl')  # REFL
    ]
).add_class('nā_pron_refl_suffix')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '.lich_ukaz > .nā_pron_refl_suffix> .p_lps',
    parent_filter=grammar.LinkSentence(
      'universal:entity=(token) & mansi:basic_pos=(pronoun)',
      rombandeeva
   )
)

lps_matrix_2 = [
    ['sing', '1', '^м'],
    ['sing', '3', '^тэ'],
    ['dual', '1', '^ме̄н'],
    ['dual', '3', '^тэ̄н'],
    ['plur', '1', '^в'],
    ['plur', '3', '^ныл']
]

p_lps_filter = '# & universal:entity=(token) & mansi:basic_pos=(pronoun)'
for number, person, suffix in lps_matrix_2:
    rombandeeva.add_element(
        'universal:morpheme',
        suffix,
        '2a_{}_{}_suff_lps'.format(number, person)
    ).applied(
        grammar.LinkSentence(p_lps_filter),
        [
            grammar.Action('mansi:make_lp', arguments=[number, person])
        ]
    ).add_class('p_lps')

rombandeeva.add_element(
    'universal:morpheme',
    '^н',
    '2a_sing_2_suff_lps'
).applied(
    grammar.LinkSentence(p_lps_filter),
    [
        grammar.Action('mansi:make_lp', arguments=['sing', '2'])
    ]
).add_class('p_lps')

rombandeeva.add_element(
    'universal:morpheme',
    '^н',
    '2a_plur_2_suff_lps'
).applied(
    grammar.LinkSentence(p_lps_filter),
    [
        grammar.Action('mansi:make_lp', arguments=['plur', '2'])
    ]
).add_class('p_lps')

# page 98-99!

interrog_pronoun = [
    ['хотъют', 'хотъютыг', 'хотъютыт', 'xotjut'],
    ['хо̄ӈха', 'хо̄ӈхаг', 'хо̄ӈхат', 'xōŋxa'],
    ['ма̄ныр', 'ма̄нарыг', 'ма̄нарыт', 'mānər']
]

"""
for sing, dual, plur, id_word in interrog_pronoun:
    rombandeeva.add_element('universal:token', sing, '{}_sing'.format(id_word)).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('gram:number:set_sing')
        ]
    ).add_class('interrog_pronoun')
    rombandeeva.add_element('universal:token', dual, '{}_dual'.format(id_word)).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('gram:number:set_dual')
        ]
    ).add_class('interrog_pronoun')
    rombandeeva.add_element('universal:token', plur, '{}_plur'.format(id_word)).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('gram:number:set_plur')
        ]
    ).add_class('interrog_pronoun')
"""

#rombandeeva.get_class('interrog_pronoun').intrusion(
#    class_list=['case_suffixes'],
#    bw_list=grammar.BWList(exclude_mutations=['gram:case:set_loc'])
#)

demonstr_pronoun_matrix = [
    [['ты', 'та'], ['тыиг', 'таиг'], ['тыит', 'таит']],
    [['тыи', 'таи'], ['тыиг', 'таиг'], ['тыит', 'таит']],
    [['тыин', 'таин'], ['тыигн', 'таигн'], ['тыитн', 'таитн']],
    [['тыиныл', 'таиныл'], ['тыигныл', 'таигныл'], ['тыитныл', 'таитныл']],
    [['тыил', 'таил'], ['тыигыл', 'таигыл'], ['тыитыл', 'таитыл']],
    [['тыиг', 'таиг'], [], []]
]

cases = ['nom', 'acc', 'dat', 'abl', 'instr', 'trans']
num = ['sing', 'dual', 'plur']
"""
for j, group in enumerate(demonstr_pronoun_matrix):
    for e, number in enumerate(group):
        if not number:
            continue
        rombandeeva.add_element(
            'universal:token', number[0], 'pd.ty_{}_{}'.format(j, e)
        ).applied(
            grammar.LinkSentence('# & universal:entity=(input)'),
            [
                grammar.Action('gram:case:set_{}'.format(cases[j])),
                grammar.Action('gram:number:set_{}'.format(num[e])),
                grammar.Action('mansi:pronoun:demonstrative')
            ]
        )
        rombandeeva.add_element(
            'universal:token', number[1], 'pd.ta_{}_{}'.format(j, e)
        ).applied(
            grammar.LinkSentence('# & universal:entity=(input)'),
            [
                grammar.Action('gram:case:set_{}'.format(cases[j])),
                grammar.Action('gram:number:set_{}'.format(num[e])),
                grammar.Action('mansi:pronoun:demonstrative')
            ]
        )
"""

det_pronoun_matrix = [
    ['tamle', 'тамле'],
    ['kāsəŋ', 'ка̄сыӈ'],
    ['pussən', 'пуссын'],
    ['tōwa', 'то̄ва'],
    ['tasāwit', 'таса̄вит']
]

"""
for id_word, mansi_word in det_pronoun_matrix:
    rombandeeva.add_element(
        'universal:token:start',
        mansi_word,
        id_word
    ).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('mansi:set_basic_pos:pronoun'),
            grammar.Action('mansi:pronoun:determinative')
        ]
    )
"""

hotpa = ['хо̄тпа', 'хо̄тпаг', 'хо̄тпат']
matyr = ['матыр', 'матарыг', 'матарыт']

"""
for j in range(3):
    for s in ('xōtpa', 'matər'):
        rombandeeva.add_element(
            'universal:token', eval(s)[j], 'pi_{}_{}'.format(s, num[j])
        ).applied(
            grammar.LinkSentence('# & universal:entity=(input)'),
            [
                grammar.Action('gram:number:set_{}'.format(num[j]))
            ]
        )
"""

matyr_hotpa_matrix = [
    ['nom', 'хо̄тпа', 'матыр'],
    ['dat', 'хо̄тпан', 'матарн'],
    ['abl', 'хо̄тпаныл', 'матарныл'],
    ['instr', 'хо̄тпал', 'матарыл'],
    ['trans', 'хо̄тпаг', 'матарыг']
]

"""
for case, h_paradigm, m_paradigm in matər_xōtpa_matrix:
    rombandeeva.add_element(
        'universal:token', x_paradigm, 'xōtpa_{}'.format(case)
    ).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('gram:case:set_{}'.format(case))
        ]
    )
    rombandeeva.add_element(
        'universal:token', m_paradigm, 'matər_{}'.format(case)
    ).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('gram:case:set_{}'.format(case))
        ]
    )

# negative pronouns нэ̄мхо̄тпа and нэ̄матыр
for case, x_paradigm, m_paradigm in matər_xōtpa_matrix:
    rombandeeva.add_element(
        'universal:token', 'нэ̄м' + x_paradigm, 'NEG_xōtpa_{}'.format(case)
    ).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('gram:case:set_{}'.format(case))
        ]
    )
    rombandeeva.add_element(
        'universal:token', 'нэ̄' + m_paradigm, 'NEG_matər_{}'.format(case)
    ).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('gram:case:set_{}'.format(case))
        ]
    )
"""

# pronouns need further description

# page 107, VERB
# `not a derivative` parameter
rombandeeva.add_element('universal:morpheme', '^ахт', 'axt_refl_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_refl')  # REFL
    ]
).add_class('refl_suffs')

rombandeeva.add_element('universal:morpheme', '^хат', 'xat_refl_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_refl')  # REFL
    ]
).add_class('refl_suffs')

rombandeeva.add_element('mansi:morphemeYU', '^ыгл', 'əɣl_tr_suffix').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:intransitive=()'
    ),
    [
        grammar.Action('gram:make_transitive')  # TR
    ]
).add_class('trans_suffs')

rombandeeva.add_element('mansi:morphemeYU', '^гл', 'ɣl_tr_suffix').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:intransitive=()'
    ),
    [
        grammar.Action('gram:make_transitive')  # TR
    ]
).add_class('trans_suffs')

rombandeeva.add_element('universal:morpheme', grammar.Temp.NULL, 'null_for_trans').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb)'
    ),
    [
        grammar.Action('gram:make_intransitive')  # DETR
    ]
).add_class('trans_suffs')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '''? < .lt_suff >> .inf_suff''',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:basic_pos=(verb)')
)
# reflexive не могут иметь при себе прямого дополнения

# page 112, побудительные глаголы - повторение предыдущего

# page 113, типы спряжения глагола

rombandeeva.add_element('universal:morpheme', '^л', 'l_obj_suffix').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb) & [gram:person=(1) | gram:person=(2)]'
    ),
    [
        grammar.Action('mansi:set_obj_conj')
    ]
).add_class('conj_set')

rombandeeva.add_element('universal:morpheme', '^тэ', 'te_obj_suffix').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:person=(3)'
    ),
    [
        grammar.Action('mansi:conj:set_obj')
    ]
).add_class('conj_set')

rombandeeva.add_element('universal:morpheme', '^т', 't_obj_suffix').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:person=(3)'
    ),
    [
        grammar.Action('mansi:conj:set_obj')
    ]
).add_class('conj_set')

rombandeeva.add_element('universal:morpheme', '^ве', 'we_pass_suffix').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:person=(3)'
    ),
    [
        grammar.Action('mansi:conj:set_subj_pass')
    ]
).add_class('conj_set')

rombandeeva.add_element('universal:morpheme', grammar.Temp.NULL, 'conj_null').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:conj:set_objectless')
    ]
).add_class('conj_set')
#

present_s_consonant_suffs = [('jēɣ', 'е̄г'), ('i', 'и'), ('je', 'е'), ('jē', 'е̄')]
for code, suff in present_s_consonant_suffs:
    rombandeeva.add_element(
        'universal:morpheme',
        '^' + suff,
        '{}_present_suff'.format(code)
    ).applied(
        grammar.LinkSentence(
            '''# & universal:entity=(token)
            & mansi:basic_pos=(verb)
            & gram:tense!=()
            '''
        ),
        [
            grammar.Action('gram:tense:set_present')
        ]
    )


present_h_consonant_suffs = [('eɣ', 'эг'), ('ēɣ', 'э̄г'), ('i', 'ы'), ('e', 'э'), ('ē', 'э̄')]
for code, suff in present_h_consonant_suffs:
    rombandeeva.add_element(
        'universal:morpheme',
        '^' + suff,
        '{}_present_suff'.format(code)
    ).applied(
        grammar.LinkSentence(
            '''# & universal:entity=(token)
            & mansi:basic_pos=(verb)
            & mansi:conj=(objectless)
            & gram:tense!=()'''
        ),
        [
            grammar.Action('gram:tense:set_present')
        ]
    )
rombandeeva.get_system('universal:morpheme').subclasses_order(
    '? << .inf_suff |',
    parent_filter=grammar.LinkSentence(
        'universal:entity=(token) & mansi:basic_pos=(verb)'
    ),
    strict=True
)

rombandeeva.add_element('universal:morpheme', '^ыс', 'əs_past_suffix').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
            & mansi:basic_pos=(verb)
            & gram:tense!=()'''
    ),
    [
        grammar.Action('gram:tense:set_past')
    ]
).add_class('past_suffixes')

rombandeeva.add_element('universal:morpheme', '^ас', 'as_past_suffix').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
            & mansi:basic_pos=(verb)
            & gram:tense!=()'''
    ),
    [
        grammar.Action('gram:tense:set_past')
    ]
).add_class('past_suffixes')

# page 115

rombandeeva.add_element('universal:morpheme', '^с', 's_past_suffix').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
            & mansi:basic_pos=(verb)
            & gram:tense!=()'''
    ),
    [
        grammar.Action('gram:tense:set_past')
    ]
).add_class('past_suffixes')

rombandeeva.add_element('universal:morpheme', '^м', 'm_ev_suffix').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & [ mansi:conj=(objectless) | mansi:conj=(obj) ]
        & gram:tense!=()'''
    ),
    [
        grammar.Action('gram:mood:set_latentive'),
        grammar.Action('gram:tense:set_past')
    ]
)

rombandeeva.add_element('universal:morpheme', '^ум', 'um_ev_suffix').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & [ mansi:conj=(objectless) | mansi:conj=(obj) ]
        & gram:tense!=()'''
    ),
    [
        grammar.Action('gram:mood:set_latentive'),
        grammar.Action('gram:tense:set_past')
    ]
)

rombandeeva.add_element('universal:morpheme', '^ам', 'am_ev_suffix').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & [ mansi:conj=(objectless) | mansi:conj=(obj) ]
        & gram:tense!=()'''
    ),
    [
        grammar.Action('gram:mood:set_latentive'),
        grammar.Action('gram:tense:set_past')
    ]
)

rombandeeva.add_element('mansi:morpheme_soft', '^има', 'ima_ev_pass_suffix').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & gram:transitive=()
        & mansi:conj=(subj_pass)'''
    ),
    [
        grammar.Action('gram:mood:set_latentive')
    ]
)

rombandeeva.add_element('mansi:morpheme_soft', '^ыма', 'ima_2_ev_pass_suffix').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & gram:transitive=()
        & mansi:conj=(subj_pass)'''
    ),
    [
        grammar.Action('gram:mood:set_latentive')
    ]
)

# page 116
# INDICATIVE

rombandeeva.add_element('universal:morpheme', '^ум', 'um_1sg_ind_subj').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^н', 'n_2sg_ind_subj').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['2']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^ын', 'ən_2sg_ind_subj').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['2']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element(
    'universal:morpheme',
    grammar.Temp.NULL,
    'null_3sing_ind_objless'
).applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(objectless)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^ме̄н', 'mēn_1du_ind_subj').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^ы̄н', 'ə̄n_2du_ind_subj').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['2']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^ы̄н', 'ə̄n_2pl_ind_subj').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['2']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^ыг', 'əɣ_3du_ind_subj').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^г', 'ɣ_3du_ind_subj').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^ув', 'uw_1pl_ind_subj').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^в', 'w_1pl_ind_subj').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^э̄в', 'ēw_1pl_ind_subj').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:set_number:plur')
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^ыт', 'ət_3pl_ind_subj').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:set_number:plur'),
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '.past_suffixes > .objectless_conj_suffixes',
    parent_filter=grammar.LinkSentence(
        'universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(objectless)'
    )
)

rombandeeva.add_element('universal:collocation', '''
    <[mansi:conj=(objectless)] :contains[.objectless_conj_suffixes]> *1
    тах''', 'analytic_future').applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('gram:tense:set_future')
    ]
)

rombandeeva.add_element(
    'universal:collocation',
    '<[gram:verb:infinitive=()]> *1 <[mansi:lemma=(патуӈкве)]>',
    'future_patuŋkwe'
).applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('gram:tense:set_future')
    ]
)

# page 121.add_class('verb_conj_personal')

rombandeeva.add_element('mansi:morphemeYU', '^и', 'i_suffix_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj) & gram:tense!=()'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('obj_conj_tense')

rombandeeva.add_element('universal:morpheme', '^л', 'l_suffix_obj_sg').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:object_number:set_sing')
    ]
).add_class('obj_conj_object_number').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:morphemeYU', '^аг', 'aɣ_suffix_obj_du').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:object_number:set_dual')
    ]
).add_class('obj_conj_object_number').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:morphemeYU', '^ан', 'an_suffix_obj_pl').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:object_number:set_plur')
    ]
).add_class('obj_conj_object_number').add_class('verb_conj_personal')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '.obj_conj_tense > .obj_conj_object_number',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)')
)

#rombandeeva.get_system('universal:morpheme').subclasses_order(
#    '#i_suffix_present > .obj_conj_object_number > .l_friendly',
#    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)')
#)

#rombandeeva.get_system('universal:morpheme').subclasses_order(
#    '#i_suffix_present > .l_non_friendly',
#    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)')
#)

rombandeeva.add_element('mansi:VowMorpheme', '^ум', 'um_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('l_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^ын', 'ən_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['2']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('l_friendly').add_class('verb_conj_personal')


rombandeeva.add_element('universal:morpheme', '^тэ', 'te_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('l_non_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^ме̄н', 'mēn_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('l_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^ы̄н', 'ə̄n_obj_conj_du').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['2']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('l_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^ы̄н', 'ə̄n_obj_conj_pl').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['2']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('l_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^тэ̄н', 'tēn_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('l_non_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^ув', 'uw_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('l_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:morphemeYU', '^а̄ныл', 'jānəl_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('verb_conj_personal')

# IN PLUR ONLY:
rombandeeva.add_element('universal:morpheme', '^ныл', 'nəl_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('verb_conj_personal')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '#an_suffix_obj_plur > #nəl_obj_conj',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(obj)'),
    strict=True
)

# page 124

rombandeeva.add_element('universal:collocation', '''
    <[mansi:conj=(obj)]> *1
    тах''', 'analytic_future_for_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('gram:tense:set_future')
    ]
)

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '#we_pass_suffix > .subj_pass_suffixes |',
    parent_filter=grammar.LinkSentence(
        'universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(subj_pass)'
    )
)

rombandeeva.add_element('mansi:VowMorpheme', '^м', 'm_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

for numb in ('sing', 'dual', 'plur'):
    rombandeeva.add_element('mansi:VowMorpheme', '^н', 'n_suffix_subj_pass_' + numb).applied(
        grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(subj_pass)'),
        [
            grammar.Action('mansi:verb:set_person', arguments=['2']),
            grammar.Action('gram:number:set_' + numb)
        ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', grammar.Temp.NULL, 'null_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^ме̄н', 'mēn_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^г', 'ɣ_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^в', 'w_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^т', 't_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '.past_suffixes > .subj_pass_suffixes',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:basic_pos=(verb) & mansi:conj=(subj_pass)')
)

rombandeeva.add_element('universal:collocation', '''
    <[mansi:conj=(subj_pass)]> *1
    тах''', 'analytic_future_for_subj_pass_conj').applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('gram:tense:set_future')
    ]
)

# page 126

rombandeeva.add_element('universal:morpheme', '^э', 'e_suffix_imperative_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:tense!=()'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('imperative_present_2sg')

rombandeeva.add_element('universal:morpheme', '^е', 'je_suffix_imperative_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:tense!=()'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('imperative_present_2sg')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '| .imperative_present_2sg  >> .obj_conj_object_number > #n_suffix_imperative |',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:basic_pos=(verb)'),
    select_into={
        'id': 'imperative_group_2sg',
        'classes': ['imperative_group', 'mood_changing'],
        'actions': [
            grammar.Action('gram:mood:set_imperative'),
            grammar.Action('mansi:verb:set_person', arguments=['2']),
            grammar.Action('gram:number:set_sing')
        ]
    },
    strict=True
)

rombandeeva.add_element('mansi:VowMorpheme', '^н', 'n_suffix_imperative').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:mood:set_imperative')
    ]
)

rombandeeva.add_element('universal:morpheme', '^э̄', 'ē_suffix_imperative_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:tense!=()'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('imperative_present_2du_pl')

rombandeeva.add_element('universal:morpheme', '^е̄', 'jē_suffix_imperative_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:tense!=()'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('imperative_present_2du_pl')

# NEEDS IMPROVEMENT TO SUPPORT MUTATION STRATEGY

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '| .imperative_present_2du_pl >> .obj_conj_object_number > #n_suffix_imperative |',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:basic_pos=(verb)'),
    select_into={
        'id': 'imperative_group_2du_pl',
        'classes': ['imperative_group', 'mood_changing'],
        'actions': [
            grammar.Action('gram:mood:set_imperative'),
            grammar.Action('mansi:verb:set_person', arguments=['2']),
            grammar.Action('gram:number:set_dual', branching=True),
            grammar.Action('gram:number:set_plur', branching=True)
        ]
    },
    strict=True
)

rombandeeva.add_element('universal:morpheme', grammar.Temp.NULL, 'null_for_mood_as_ind').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:mood:set_indicative')
    ]
).add_class('mood_changing')


# page 127

rombandeeva.add_element('universal:collocation', 'вос *1 <[gram:mood=(indicative)>', 'imperative_3pers').applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('gram:mood:set_imperative'),
        grammar.Action('mansi:verb:set_person', arguments=['3'])
    ]
)

rombandeeva.add_element(
    'universal:collocation',
    'вос *1 <[mansi:conj=(subj_pass)]>',
    'analyt_imper_for_subj_pass_conj'
).applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('gram:mood:set_imperative')
    ]
)

# page 128

rombandeeva.add_element('mansi:VowMorpheme', '^$[ы]нув', 'ənuw_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token)'),
    [
        grammar.Action('gram:mood:set_conjunctive')
    ]
).add_class('nuv_suffixes')

rombandeeva.add_element('mansi:VowMorpheme', '^$[а]нув', 'anuw_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token)'),
    [
        grammar.Action('gram:mood:set_conjunctive')
    ]
).add_class('nuv_suffixes')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '.nuv_suffixes >> .obj_conj_object_number >+ .verb_conj_personal'
)

for numb in ('sing', 'plur'):
    rombandeeva.add_element('universal:morpheme', '^э', 'e_conjunctive_obj_' + numb).applied(
        grammar.LinkSentence('# & universal:entity=(token) & gram:mood=(conjunctive)'),
        [
            grammar.Action('mansi:verb:set_person', arguments=['3']),
            grammar.Action('gram:number:set_' + numb)
        ]
).add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^е', 'je_conjunctive_obj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & gram:mood=(conjunctive)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('verb_conj_personal')

### verb_conj_personal EXTENSION
vcp_ext_matrix = [
    ['sing', '1', 'ум', 'um'],
    ['sing', '2', 'ын', 'ən'],
    ['sing', '3', 'е', 'e'],
    ['dual', '1', 'ме̄н', 'mēn'],
    ['dual', '3', 'е̄н', 'ēn'],
    ['plur', '1', 'ув', 'uw'],
    ['plur', '3', 'а̄ныл', 'ānəl']
]
for number, person, suffix, id_name in vcp_ext_matrix:
    rombandeeva.add_element(
        'mansi:VowMorpheme',
        '^' + suffix,
        '{}_vcp_ext'.format(id_name)
    ).applied(
        grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
        [
            grammar.Action('mansi:verb:set_person', arguments=[person]),
            grammar.Action('gram:number:set_{}'.format(number))
        ]
    ).add_class('verb_conj_personal')
###

# page 130, optative

rombandeeva.add_element(
    'universal:collocation',
    '<[mansi:basic_pos=(verb)]> *1 ке',
    'analytic_optative'
).applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('gram:mood:set_optative')
    ]
)

# latentive
# the elements above providing latentive -- what's that???

rombandeeva.add_element('universal:morpheme', '^н', 'n_for_ev_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:mood:set_latentive')
    ]
).add_class('latentive_suffs_present').add_class('latentive_suffs')

rombandeeva.add_element('universal:morpheme', '^ын', 'ən_for_ev_present').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb)'
    ),
    [
        grammar.Action('gram:mood:set_latentive')
    ]
).add_class('latentive_suffs_present').add_class('latentive_suffs')

rombandeeva.add_element('universal:morpheme', '^ан', 'an_for_ev_present').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb)'
    ),
    [
        grammar.Action('gram:mood:set_latentive')
    ]
).add_class('latentive_suffs_present').add_class('latentive_suffs')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '| .latentive_suffs >> .tense_suffs_latentive >> .obj_conj_object_number >+ .verb_conj_personal',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:basic_pos=(verb)')
)

rombandeeva.add_element('universal:morpheme', '^е', 'je_ev_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & gram:mood=(latentive) & gram:tense!=()'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('tense_suffs_latentive')

rombandeeva.add_element('universal:morpheme', '^е̄', 'jē_ev_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & gram:mood=(latentive) & gram:tense!=()'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('tense_suffs_latentive')

rombandeeva.add_element('universal:morpheme', '^э', 'e_ev_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & gram:mood=(latentive) & gram:tense!=()'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('tense_suffs_latentive')

rombandeeva.add_element('universal:morpheme', '^э̄', 'ē_ev_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & gram:mood=(latentive) & gram:tense!=()'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('tense_suffs_latentive')

# page 133, try if this works for the tables on p. 132-133

rombandeeva.add_element('universal:morpheme', '^м', 'm_suffix_past_ev').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:tense!=()'),
    [
        grammar.Action('gram:tense:set_past'),
        grammar.Action('gram:mood:set_latentive')
    ]
).add_class('latentive_suffs_past').add_class('latentive_suffs')

rombandeeva.add_element('universal:morpheme', '^ум', 'um_suffix_past_ev').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & gram:tense!=()
        '''
    ),
    [
        grammar.Action('gram:tense:set_past'),
        grammar.Action('gram:mood:set_latentive')
    ]
).add_class('latentive_suffs_past').add_class('latentive_suffs')

rombandeeva.add_element('universal:morpheme', '^ам', 'am_suffix_past_ev').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & gram:tense!=()
        '''
    ),
    [
        grammar.Action('gram:tense:set_past')
    ]
).add_class('latentive_suffs_past').add_class('latentive_suffs')

# i am not sure we need syl_count there
rombandeeva.add_element('universal:morpheme', '^ӯм', 'ūm_suffix_past_ev').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & gram:tense!=()
        '''
    ),
    [
        grammar.Action('gram:tense:set_past'),
        grammar.Action('gram:mood:set_latentive')
    ]
).add_class('latentive_suffs_past').add_class('latentive_suffs')

rombandeeva.add_element('mansi:VowMorpheme', '^има', 'ima_ev_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:mood:set_latentive'),
        grammar.Action('mansi:conj:set_subj_pass')
    ]
).add_class('latentive_suff_subj_pass')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '| .latentive_suff_subj_pass > .verb_conj_personal |',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:basic_pos=(verb)')
)

# page 136

smlf_suffs = ['ап', 'ат', 'ас', 'ай', 'ал', 'алт', 'ыгп', 'ыгт', 'лыгт', 'увл', 'м', 'умт', 'амл', 'мат', 'май', 'ылмат']
smlf_suffs += ['ал', 'л', 'иньт', 'с']

for e, suff in enumerate(smlf_suffs):
    rombandeeva.add_element('universal:morpheme', '^' + suff, 'smlf_suff_' + str(e)).applied(
        grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
        [
            grammar.Action('gram:set_semelfactive') # SMLF
        ]
    ).add_class('word_formation')

rombandeeva.add_element('universal:morpheme', '^умт', 'umt_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_inchoative') # INCH
    ]
).add_class('word_formation')

rombandeeva.add_element('universal:morpheme', '^мыгт', 'məɣt_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_inchoative') # INCH
    ]
).add_class('word_formation')

dur_suffs = ['а̄нт', 'ант', 'гал', 'л', 'ас', 'асьл', 'ал', 'а̄л', 'с', 'ыгл', 'тл']

for e, suff in enumerate(dur_suffs):
    rombandeeva.add_element('universal:morpheme', '^' + suff, 'dur_suff_' + str(e)).applied(
        grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
        [
            grammar.Action('gram:set_durative')  # DUR
        ]
    ).add_class('word_formation')


iter_suffs = ['а̄л', 'ыгл', 'гала̄л', 'ыгла̄л', 'а̄лыгл', 'ата̄л', 'лант', 'гал']

for e, suff in enumerate(iter_suffs):
    rombandeeva.add_element('universal:morpheme', '^' + suff, 'iter_suff_' + str(e)).applied(
        grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
        [
            grammar.Action('gram:set_iterative')  # ITER
        ]
    ).add_class('word_formation')

# page 140

rombandeeva.add_element('universal:morpheme', '^ке', 'ke_suffix_adj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_dimin')  # DIM
    ]
).add_class('word_formation')

rombandeeva.add_element('universal:morpheme', '^те', 't'e_suffix_adj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_dimin')  # DIM
    ]
).add_class('word_formation')

# noun_to_verb

rombandeeva.add_element('universal:morpheme', '^м', 'm_noun_to_verb').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:noun_to_verb'),
        grammar.Action('gram:make_transitive') # TR
    ]
).add_class('noun_to_verb_suff')

rombandeeva.add_element('universal:morpheme', '^л', 'l_noun_to_verb').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:noun_to_verb')
    ]
).add_class('noun_to_verb_suff')

rombandeeva.add_element('universal:morpheme', '^л', 'l_transitive').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:make_transitive')
    ]
)

rombandeeva.add_element('universal:morpheme', '^л', 'l_intransitive').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:make_intransitive')
    ]
)

rombandeeva.add_element('mansi:VowMorpheme', '^ал', 'al_noun_to_verb').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:noun_to_verb'),
        grammar.Action('gram:make_transitive')
    ]
).add_class('noun_to_verb_suff')

rombandeeva.add_element('universal:morpheme', '^т', 't_noun_to_verb').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:noun_to_verb'),
        grammar.Action('gram:make_intransitive')
    ]
).add_class('noun_to_verb_suff')


@rombandeeva.foreach_in_class('noun_to_verb_suff')
def mutation_links_for_noun_to_verb(element):
    element.provide_mutation_links(
        [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(noun)')]
    )

# page 141
# OMG prefixes


rombandeeva.add_element('universal:morpheme', '_^хот', 'xot_prefix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('direct:set_meaning', arguments=['от'])
    ]
)

rombandeeva.add_element('universal:morpheme', '_^лап', 'lap_prefix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('direct:set_meaning', arguments=['за'])
    ]
)

rombandeeva.add_element('universal:morpheme', '_^э̄л', 'ēl_prefix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('direct:set_meaning', arguments=['от'])
    ]
)

rombandeeva.add_element('universal:morpheme', '_^ёл', 'jol_prefix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('direct:set_meaning', arguments=['c'])
    ]
)

rombandeeva.add_element('universal:morpheme', '_^но̄х', 'nox_prefix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('direct:set_meaning', arguments=['вверх'])
    ]
)

rombandeeva.add_element('universal:morpheme', '_^юв', 'juw_prefix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('direct:set_meaning', arguments=['в'])
    ]
)

rombandeeva.add_element('universal:morpheme', '_^кон', 'kon_prefix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('direct:set_meaning', arguments=['наружу'])
    ]
)

# page 142

rombandeeva.add_element(
    'universal:collocation',
    '<[mansi:basic_pos=(noun)]> *1 <[mansi:lemma=(патуӈкве)]>',
    'compound_verb'
).applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('mansi:basic_pos:set_verb')
    ]
)

#rombandeeva.add_element('mansi:VowMorpheme', '^йт', 'jt_suffix_rus').applied(
#   grammar.LinkSentence('# & universal:entity=(token)'),
#    [
#        grammar.Action('mansi:basic_pos:set_verb'),
#        grammar.Action('mansi:russian_loan_word')
#    ]
#)

# page 143

rombandeeva.add_element('universal:morpheme', '^м', 'm_ptcp').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_participle'),  # PTCP
        grammar.Action('gram:set_resultative')  # RES
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^ум', 'um_ptcp').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_participle'),  # PTCP
        grammar.Action('gram:set_resultative')  # RES
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^ам', 'am_ptcp').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_participle'),  # PTCP
        grammar.Action('gram:set_resultative')  # RES
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^им', 'im_ptcp').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_converb')  # CVB
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^н', 'n_ptcp').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_participle'),  # PTCP
        grammar.Action('gram:set_present')  # PRS
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^нэ', 'nе_ptcp').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_participle'),  # PTCP
        grammar.Action('gram:set_present')  # PRS
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^нэ̄', 'nē_ptcp').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_participle'),  # PTCP
        grammar.Action('gram:set_present')  # PRS
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^ын', 'ən_ptcp').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_participle'),  # PTCP
        grammar.Action('gram:set_present')  # PRS
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^ан', 'an_ptcp').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_participle'),  # PTCP
        grammar.Action('gram:set_present')  # PRS
    ]
).add_class('participle_suffix')

# TRANSGRESSIVE

rombandeeva.add_element('universal:morpheme', '^им', 'im_cvb').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
        & [ mansi:basic_pos=(verb) | mansi:basic_pos=(participle) ]
        '''
    ),
    [
        grammar.Action('mansi:make_transgressive')
    ]
)

rombandeeva.add_element('universal:morpheme', '^ым', 'im_2_cvb').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
        & [ mansi:basic_pos=(verb) | mansi:basic_pos=(participle) ]
        '''
    ),
    [
        grammar.Action('mansi:make_transgressive')
    ]
)

rombandeeva.add_element('universal:morpheme', '^м', 'm_cvb').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
        & [ mansi:basic_pos=(verb) | mansi:basic_pos=(participle) ]
        '''
    ),
    [
        grammar.Action('mansi:make_transgressive')
    ]
)

rombandeeva.add_element('universal:morpheme', '^т', 't_cvb').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
        & [ mansi:basic_pos=(verb) | mansi:basic_pos=(participle) ]
        '''
    ),
    [
        grammar.Action('mansi:make_transgressive')
    ]
)

# page 149

rombandeeva.add_element(
    'universal:collocation',
    '''<[[mansi:basic_pos=(pronoun) | mansi:basic_pos=(adj) | mansi:basic_pos=(numeral) | mansi:basic_pos=(adv)] ]>
    *1 <[mansi:lemma=(сирыл)]>''',
    'syntactic_adverb'
).applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('mansi:basic_pos:set_adv')
    ]
)

# page 151

rombandeeva.add_element(
    'universal:collocation',
    '<[mansi:basic_pos=(adv)]> :ignore[*1+] <[gram:case=(abl)]>',
    'syntactic_adverb_comparative'
).applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('mansi:basic_pos:set_adv'),
        grammar.Action('gram:set_comparative')
    ]
)

rombandeeva.add_element('universal:morpheme', '^нув', 'nuv_suffix_adv').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adv)'),
    [
        grammar.Action('gram:adv:comparative')
    ]
)

rombandeeva.add_element('universal:morpheme', '^нуве', 'nuve_suffix_adv').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adv)'),
    [
        grammar.Action('gram:adv:comparative')
    ]
)

rombandeeva.add_element(
    'universal:collocation',
    '<[[mansi:lemma=(сяр)|mansi:lemma=(сака)]]> *1 <[mansi:basic_pos=(adv)]>',
    'syntactic_adv_superlative'
).applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('mansi:basic_pos:set_adv'),
        grammar.Action('gram:set_superlative')
    ]
)

# page 153

postpos_mutable = [
    ('кӣвыр', 'ki*vyr'),
    ('хал', 'hal'),
    ('ва̄та', 'va*ta'),
    ('ёлы-па̄л', 'yoly_pa*l'), # collocation as variant
    ('нуми-па̄л', 'numi_pa*l') # collocation as variant
]

"""
for pp_word, pp_id in postpos_mutable:
    rombandeeva.add_element('universal:token', pp_word, pp_id).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('mansi:basic_pos:set_postpos')
        ]
    ).add_class('postpos_mutable')
"""

#rombandeeva.get_class('postpos_mutable', await=True).intrusion(
#    class_list=['case_suffixes', 'verb_conj_personal']
#)

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '.case_suffixes > .verb_conj_personal',
    parent_filter=grammar.LinkSentence('universal:class=(postpos_mutable)')
)

"""
rombandeeva.add_element('universal:token', 'па̄л', 'pa*l_postpos_in_colloc').applied(
    grammar.LinkSentence('# & universal:entity=(collocation)'),
    [
        grammar.Action('mansi:basic_pos:set_postpos')
    ]
).add_class('postpos_mutable')
"""

postpos_unmutable = [
    ['мус', ('до',)],
    ['ёт', ('с',)],
    ['ма̄гыс', ('для', 'за')],
    ['палт', ('к', 'у')],
    ['тармыл', ('на',)],
    ['паттыиг', ('вместо', 'взамен')],
    ['уртыиг', ('вместо', 'взамен')],
    ['пе̄нтсыл', ('вместо', 'взамен')],
    ['ӯлтта', ('через',)],
    ['нупыл', ('в направлении',)],
    ['хосыт', ('по',)],
    ['ляльт', ('против',)],
    ['торыг', ('перед',)],
    ['урыл', ('о', 'про')],
    ['о̄вылтытыт', ('о', 'про')],
    ['коны-пал', ('кроме',)],
    ['сыс', ('во время',)],
    ['э̄ртын', ('когда',)],
    ['э̄рт', ('когда',)],
    ['хольт', ('как',)],
    ['та̄ра', ('мимо',)]
]

pp_i = 0
"""
for lemma, meanings in postpos_unmutable:
    pp_actions = [grammar.Action('mansi:basic_pos:set_postpos')]
    if type(meanings) == str:
        pp_actions.append(grammar.Action('mansi:translation:set_new', arguments=[meanings]))
    else:
        for meaning in meanings:
            pp_actions.append(grammar.Action('mansi:translation:set_new', arguments=[meaning], branching=True))
    rombandeeva.add_element('universal:token', lemma, '{}_postpos_lemma'.format(pp_i)).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        pp_actions
    )
    pp_i += 1
"""


def luima_seripos_formatting(s):
    s = s.replace('­', '')
    s = s.replace('¬', '')
    return s


def stem_token(ic, elem):
    stem_results = ic.onseg_hook_bank.stemmer.get_stem_for(elem.get_content())

    if stem_results:
        for n, stem_group in enumerate(stem_results):
            nel = ic.clone_within_cluster(elem, n) if n else elem
            nel.set_parameter('mansi:basic_pos', stem_group.entry.get_pos())
            translation = stem_group.entry.get_translation()
            if translation:
                nel.set_parameter('mansi:translation', translation)
            nel.set_parameter('mansi:full_lemma', stem_group.entry.full_lemma)
            ic.ic_log.add_log(
                "STEMS_EXTRACTED",
                element_id=nel.get_ic_id(),
                cluster_id=nel.get_parent_ic_id(),
                positions=list(range(stem_group.index)),
                group=None
            )
    else:
        ic.ic_log.add_log(
            "STEMS_EXTRACTED",
            element_id=elem.get_ic_id(),
            cluster_id=elem.get_parent_ic_id(),
            positions=list(range(len(elem.get_content()))),
            group=None
        )
        elem.set_parameter('mansi:basic_pos', 'unknown')

    return ic


class OutputFileChecker:
    def __init__(self):
        self.luima_seripos_json_files = [
            re.sub(r'\.json$', '', file) for file in os.listdir('luima_seripos/db_json')
        ]
        self.release_ready_files = [
            re.sub(r'.+\/|_\d+\.json$', '', file) for file in open("json_output/release1_ready.txt").read().splitlines()
        ]
        self.need_files = [
            file + ".json" for file in self.luima_seripos_json_files if file not in self.release_ready_files
        ]

    def get_files_on_threads(self, n):
        return self.chunk_list(self.need_files, n)

    @staticmethod
    def say_ready(file_name):
        with open("json_output/release1_ready.txt", "a") as rlr:
            rlr.write("\n" + file_name)
            rlr.close()

    @staticmethod
    def chunk_list(seq, num):
        avg = len(seq) / float(num)
        out = []
        last = 0.0

        while last < len(seq):
            out.append(seq[int(last):int(last + avg)])
            last += avg

        return out


#threads_count = 5
#output_file_checker = OutputFileChecker()
#thread_files = output_file_checker.get_files_on_threads(threads_count)


def ae_thread(num):
    my_files = thread_files[num]
    for luima_file_path in my_files:
        print('Working of file:', luima_file_path)
        luima_file = json.loads(open('luima_seripos/db_json/' + luima_file_path).read())
        for n, text_block in enumerate(luima_file["content"]["correct"]):
            text = text_block
            text = luima_seripos_formatting(text)
            text_id = "%s_%d" % (luima_file_path.replace(".json", ""), n)
            meta = {
                "filename": text_id,
                "author": "luima_seripos",
                "researcher": "-",
                "title": text_id,
                "genre": "newspaper",
                "place": "-",
                "dialect": "standard",
                "year_from": 2012,
                "year_to": 2018
            }
            input_container = grammar.InputContainer(text, prevent_auto=True)
            input_container.onseg_hook_bank.stemmer = trie_stemmer.stemmer

            input_container.config.param_rewrite = True
            # input_container.config.gm_cycle_limit = 100
            # input_container.config.broad_exception_mode = True
            #input_container.config.show_index = True
            # input_container.config.submessages.cycle_limit_exceeded = True
            input_container.add_onseg_hook('universal:token', stem_token)
            input_container.start_auto_segmentation()
            # input_container.onseg_hook_bank.stemmer.write_cache()
            input_container.connect_mc(rombandeeva)
            input_container.run_mc_analysis()

            # print([(x.get_system_name(), x.get_content()) for x in input_container.elements])
            mns_template = output_templates.tsakorpus_document.Template(rombandeeva)
            tsa_output = mns_template.run(input_container, meta=meta)
            output_file_checker.say_ready('json_output/release1/{}.json'.format(text_id))
            with open('json_output/release1/{}.json'.format(text_id), 'w') as to:
                to.write(tsa_output)
                to.close()


#print(WordEntry)
#processes = dict()
#for n in range(threads_count):
#    processes[n] = threading.Thread(target=ae_thread, args=(n,))
#    processes[n].start()
#for n in range(threads_count):
#    processes[n].join()
    #processes[n].join()

# page 159: ?

### RUN seq:correction:mansi* mutation
### create mansi:morphemeYU
