#!/usr/bin/python3
import grammar
import mansi_stemmer
import structures_collection as coll

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

rombandeeva.add_element('universal:morpheme', '^та!л', 'tal_suffix').applied(
    *[
        grammar.LinkSentence('# & universal:entity=(token) & mansi:simple_pos=(adj)'),
        [grammar.Action('sem:make_opposite')]  # CAR
    ]
)
#
rombandeeva.add_element('universal:morpheme', '^т', 't_suffix').add_class('caus_suffixes') # CAUS
rombandeeva.add_element('mansi:VowMorpheme', '^лт', 'lt_suffix').add_class('caus_suffixes') # CAUS
rombandeeva.add_element('universal:morpheme', '^пт', 'pt_suffix').add_class('caus_suffixes')
rombandeeva.add_element('universal:morpheme', '^лтт', 'ltt_suffix').add_class('caus_suffixes')
rombandeeva.add_element('universal:morpheme', '^тт', 'tt_suffix').add_class('caus_suffixes')
for element in rombandeeva.get_by_class_name('caus_suffixes'):
    # or just element.applied ??
    rombandeeva.get_by_id(element.get_id()).applied(
        *[
            grammar.LinkSentence('# & universal:entity=(token) & mansi:simple_pos=(verb) & sem:causative!=()'),
            [
                grammar.Action('sem:make_causative')
            ]
        ]
    )

rombandeeva.add_element('universal:morpheme', '^л', 'l_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:simple_pos=(verb) & gram:intransitive=()'),
    [
        grammar.Action('gram:make_transitive')
    ]
).add_class('trans_suffixes')

rombandeeva.get_system('universal:morpheme').subclasses_order(
   '? < .number_suffix <<>> .lps >> .case_suffix >> ?',
   # the next argument is optional
   parent_filter=grammar.LinkSentence(
      'universal:entity=(token) & mansi:simple_pos=(noun)',
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
        'universal:entity=(token) & mansi:simple_pos=(verb)',
        rombandeeva
    )
)

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '? << :root >> ? >> .word_building_suffix >> .case_suffix >> ?',
    parent_filter=grammar.LinkSentence(
        'universal:entity=(token) & mansi:simple_pos=(noun)'
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

rombandeeva.add_element('universal:morpheme', '^г', 'g_suffix').applied(
    *[
        grammar.LinkSentence(is_noun + '& [ universal:end=(а) | universal:end=(е) | universal:end=(я) ]'),
        [grammar.Action('gram:number:set_dual')]
    ]
).add_class('number_suffix')

# твёрдые согласные?

rombandeeva.add_element('universal:morpheme', '^ыг', 'yg_suffix').applied(
    *[
        grammar.LinkSentence(is_noun + '& universal:reg_match=(%MANSI_CONS_END%){pre=(ыг)}'),
        [grammar.Action('gram:number:set_dual')]
    ]
).add_class('number_suffix')

# мягкие согласные?

rombandeeva.add_element('universal:morpheme', '^яг', 'yag_suffix').applied(
    *[
        grammar.LinkSentence(is_noun + '& [ universal:reg_match=(%MANSI_CONS_END%){pre=(яг)} | universal:end=(и)]'),
        [grammar.Action('gram:number:set_dual')]
    ]
).add_class('number_suffix')

lps_matrix = [
    ['sing', '1', 'ум', 'um'],
    ['sing', '2', 'ын', 'yn'],
    ['sing', '3', 'е', 'e'],
    ['dual', '1', 'ме!н', 'men'],
    ['dual', '3', 'е!н', 'en'],
    ['plur', '1', 'ув', 'uv'],
    ['plur', '3', 'а!ныл', 'anyl'],
]

for number, person, suffix, id in lps_matrix:
    rombandeeva.add_element('universal:morpheme', '^' + suffix, id + '_suffix').add_class('lps').applied(
        *[
            grammar.LinkSentence(
                is_noun + '& gram:possessor:number=({0}) & gram:possessor:person=({0})'.format(number, person)
            ),
            [grammar.Action('mansi:make_lp', arguments=[number, person])]
        ]
    )

rombandeeva.add_element('universal:morpheme', '^ы!н', 'yn_suffix_lps').add_class('lps').applied(
    *[
        grammar.LinkSentence(
            is_noun + '& gram:possessor:number!=(sing) & gram:possessor:person=(2)'
        ),
        [
            grammar.Action('mansi:make_lp', arguments=['sing', '2'], branching=True),
            grammar.Action('mansi:make_lp', arguments=['dual', '2'], branching=True),
        ]
    ]
)

rombandeeva.add_element('universal:morpheme', '^н', 'n_suffix').applied(
    *[
        grammar.LinkSentence(is_noun + '& [ universal:end=(а) | universal:end=(е) | universal:end=(э) ]'),
        [grammar.Action('gram:number:set_plur')]
    ]
).add_class('number_suffix')

# твёрдые согласные?

rombandeeva.add_element('universal:morpheme', '^ан', 'an_suffix').applied(
    *[
        grammar.LinkSentence(is_noun + '& universal:reg_match=(%MANSI_CONS_END%){pre=(ан)}'),
        [grammar.Action('gram:number:set_plur')]
    ]
).add_class('number_suffix')

# мягкие согласные?

rombandeeva.add_element('universal:morpheme', '^ян', 'yan_suffix').applied(
    *[
        grammar.LinkSentence(is_noun + '& [ universal:reg_match=(%MANSI_CONS_END%){pre=(ян)} | universal:end=(и)]'),
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
        grammar.LinkSentence(is_noun + '& universal:reg_match=([ГЛАСНЫЙ | ГЛАСНЫЙ СОГЛАСНЫЙ]$){pre=(н)}'),
        [grammar.Action('gram:case:set_lat')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^ын', 'yn_case_suffix').applied(
    *[
        grammar.LinkSentence(is_noun + '& universal:reg_match=(%MANSI_CONS2_END%){pre=(ын)}'),
        [grammar.Action('gram:case:set_lat')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^т', 't_case_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_loc')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^ыт', 'yt_case_suffix').applied(
    *[
        grammar.LinkSentence(is_noun + '& universal:reg_match=(%MANSI_CONS2_END%){pre=(ыт)}'),
        [grammar.Action('gram:case:set_loc')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^ныл', 'nyl_case_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [grammar.Action('gram:case:set_abl')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^л', 'l_case_suffix').applied(
    *[grammar.LinkSentence(is_noun + '& universal:reg_match=(%MANSI_VOW_END%){pre=(л)}'),
        [grammar.Action('gram:case:set_instr')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^ыл', 'yl_case_suffix').applied(
    *[grammar.LinkSentence(is_noun + '& universal:reg_match=(%MANSI_CONS_END%){pre=(ыл)}'),
        [grammar.Action('gram:case:set_instr')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^ил', 'il_case_suffix').applied(
    *[grammar.LinkSentence(is_noun + '& universal:reg_match=(%MANSI_CONS_END%){pre=(ил)}'),
        [grammar.Action('gram:case:set_instr')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^г', 'g_case_suffix').applied(
    *[grammar.LinkSentence(is_noun + '& [ universal:end=(а) | universal:end=(е) | universal:end=(э) ]'),
        [grammar.Action('gram:case:set_trans')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^ыг', 'yg_case_suffix').applied(
    *[grammar.LinkSentence(is_noun + '& universal:reg_match=(%MANSI_CONS_END%){pre=(ыг)}'),
        [grammar.Action('gram:case:set_trans')]
    ]
).add_class('case_suffix')

rombandeeva.add_element('universal:morpheme', '^иг', 'ig_case_suffix').applied(
    *[grammar.LinkSentence(is_noun + '& [universal:reg_match=(%MANSI_CONS_END%){pre=(иг)} | universal:end=(и)]'),
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

rombandeeva.add_element('universal:morpheme', '^ун!кве', 'u+_infinitive_suffix').applied(
    *[
        grammar.LinkSentence(
            is_verb + '& universal:reg_match=(%MANSI_CONS_END%){pre=(ун!кве)} & universal:syl_count:odd=(){pre=(ун!кве)}'
        ),
        [grammar.Action('gram:verb:set_infinitive')]
    ]
).add_class('infinitive_excl_suff').add_class('inf_suff')

rombandeeva.add_element('universal:morpheme', '^юн!кве', 'yu+_infinitive_suffix').applied(
    *[
        grammar.LinkSentence(
            is_verb + '& universal:reg_match=(%MANSI_CONS_END%){pre=(ун!кве)} & universal:syl_count:odd=(){pre=(ун!кве)}'
        ),
        [grammar.Action('gram:verb:set_infinitive')]
    ]
).add_class('infinitive_excl_suff').add_class('inf_suff')

rombandeeva.add_element('universal:morpheme', '^ан!кве', 'a+_infinitive_suffix').applied(
    *[
        grammar.LinkSentence(
            is_verb + '& universal:reg_match=(%MANSI_CONS_END%){pre=(ун!кве)} & universal:syl_count:even=(){pre=(ун!кве)}'
        ),
        [grammar.Action('gram:verb:set_infinitive')]
    ]
).add_class('infinitive_excl_suff').add_class('inf_suff')

rombandeeva.add_element('universal:morpheme', '^н!кве', 'null+_infinitive_suffix').applied(
    *[
        grammar.LinkSentence(is_verb + '& universal:reg_match=(%MANSI_VOW_END%){pre=(н!кве)} & universal:syl_count=(1)'),
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

rombandeeva.add_element('mansi:VowMorpheme', '^си', 'si_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:sem:coll') # COLL
        ]
    ]
)

rombandeeva.add_element('universal:morpheme', '^х', 'h_suffix').applied(
    *[
        grammar.LinkSentence(is_noun),
        [
            grammar.Action('mansi:verb_to_noun')
        ]
    ]
).add_class('verb_to_noun').add_class('yu.verb_ending_excl').add_class('verb_to_noun_suff')

rombandeeva.add_element('universal:morpheme', '^ах', 'ah_suffix').applied(
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

rombandeeva.add_element('universal:morpheme', '^нув', 'nuv_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:adj:comparative')  # CMPR
    ]
)

rombandeeva.add_element('universal:morpheme', '^нуве', 'nuve_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:adj:comparative'),
        grammar.Action('mansi:set_pred') # PRED
    ]
)

rombandeeva.add_element('universal:morpheme', '^кве', 'kve_suffix_adj').applied(
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

rombandeeva.add_element('universal:morpheme', '^н!', 'ng_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_attr') # ATTR
    ]
).provide_mutation_links(
    [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(noun)')]
)

rombandeeva.add_element('universal:morpheme', '^ын!', 'yng_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_attr')
    ]
).provide_mutation_links(
    [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(noun)')]
)

rombandeeva.add_element('universal:morpheme', '^ин!', 'ing_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_attr')
    ]
).provide_mutation_links(
    [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(noun)')]
)

# *** tal_suffix REF

rombandeeva.add_element('universal:morpheme', '^и', 'i_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:noun_to_adj'),
        grammar.Action('sem:adj_to_noun_corresp')
    ]
)

rombandeeva.add_element('universal:morpheme', '^ы', 'y_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:noun_to_adj'),
        grammar.Action('sem:adj_to_noun_corresp')
    ]
)

# PARTICIPLE -> ADJ, not actually VERB -> ADJ

rombandeeva.add_element('mansi:morphemeYU', '^м', 'm_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_participle')  # PTCP ; $INGORE_SEGMENTATION if token is found in dictionaries
    ]
).add_class('yu.verb_ending_excl').provide_mutation_links(
    [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)')]
)

rombandeeva.add_element('mansi:morphemeYU', '^ум', 'um_suffix_participle').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_participle')
    ]
).add_class('yu.verb_ending_excl').provide_mutation_links(
    [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)')]
)

rombandeeva.add_element('mansi:morphemeYU', '^ам', 'am_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action('gram:set_participle')
    ]
).add_class('yu.verb_ending_excl').provide_mutation_links(
    [grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)')]
)

# page 83

rombandeeva.add_element('universal:morpheme', 'ий', 'ij_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action(grammar.Temp.NULL),
        grammar.Action('mansi:russian_loan_word') # $IGNORE_SEGMENTATION
    ]
)

rombandeeva.add_element('universal:morpheme', 'ый', 'yj_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(adj)'),
    [
        grammar.Action(grammar.Temp.NULL),
        grammar.Action('mansi:russian_loan_word')
    ]
)

rombandeeva.add_element('universal:collocation', '''
    <[mansi:basic_pos=(noun) | mansi:basic_pos=(numeral)]> *1 <[mansi:basic_pos=(noun) & mansi:HAS_DerP=()]>
''', 'phrase_adj').applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('mansi:phrase_adj')
    ]
)

rombandeeva.add_element('universal:experimental:reduplication', 'яныг', 'yanyg_redupl').applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('sem:magnification_colloc')
    ]
)

# ??? -ит -> -ит | -ыт ; page 87

rombandeeva.add_element('universal:morpheme', '^ит', 'it_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(numeral)'),
    [
        grammar.Action('gram:set_ord')  # ORD
    ]
)

rombandeeva.add_element('universal:morpheme', '^ыт', 'yt_suffix_for_nums').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(numeral)'),
    [
        grammar.Action('gram:set_ord')
    ]
)

rombandeeva.add_element('universal:morpheme', '^иттыг', 'ittyg_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(numeral)'),
    [
        grammar.Action('gram:set_mult') # MULT
    ]
)

rombandeeva.add_element('universal:morpheme', '^ынтыг', 'yntyg_suffix').applied(
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

rombandeeva.add_element('universal:morpheme', '^кем', 'kem_suffix').applied(
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
    <[mansi:basic_pos=(numeral)]> *1 <[universal:content=(суп) | universal:content=(па!л)]>
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
        'acc': 'а!нум',
        'dat': 'а!нумн',
        'abl': 'а!нумныл',
        'instr': 'а!нумтыл',
    },
    '2SG': {
        'nom': 'нан!',
        'acc': 'нан!ын',
        'dat': 'нан!ынн',
        'abl': 'нан!ынныл',
        'instr': 'нан!ынтыл',
    },
    '3SG': {
        'nom': 'тав',
        'acc': 'таве',
        'dat': 'таве!н',
        'abl': 'таве!ныл',
        'instr': 'таветыл',
    },
    '1DU': {
        'nom': 'ме!н',
        'acc': 'ме!нме!н',
        'dat': 'ме!нме!нн',
        'abl': 'ме!нме!нныл',
        'instr': 'ме!нме!нтыл',
    },
    '2DU': {
        'nom': 'нэ!н',
        'acc': 'нэ!нан',
        'dat': 'нэ!нанн',
        'abl': 'нэ!нанныл',
        'instr': 'нэ!нантыл',
    },
    '3DU': {
        'nom': 'тэ!н',
        'acc': 'тэ!нтэ!н',
        'dat': 'тэ!нтэ!нн',
        'abl': 'тэ!нтэ!нныл',
        'instr': 'тэ!нтэ!нтыл',
    },
    '1PL': {
        'nom': 'ма!н',
        'acc': 'ма!нав',
        'dat': 'ма!навн',
        'abl': 'ма!навныл',
        'instr': 'ма!навтыл'
    },
    '2PL': {
        'nom': 'на!н',
        'acc': 'на!нан',
        'dat': 'нананн',
        'abl': 'на!нанныл',
        'instr': 'на!нантыл'
    },
    '3PL': {
        'nom': 'та!н',
        'acc': 'та!наныл',
        'dat': 'та!нанылн',
        'abl': 'та!нанылныл',
        'instr': 'та!нанылтыл'
    }
}

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

rombandeeva.add_element('universal:morpheme', '^ки', 'ki_pronoun_suff').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:pronoun:is_personal=()'),
    [
        grammar.Action('mansi:pronoun:lich_ukaz') # EMPH
    ]
).add_class('lich_ukaz')

rombandeeva.add_element('universal:morpheme', '^кке', 'kke_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:pronoun:is_personal=()'),
    [
        grammar.Action('mansi:pronoun:set_sol')  # SOL
    ]
).add_class('kke_suff')

rombandeeva.get_system('universal:morpheme').subclasses_order(
   '? <>> .kke_suff > .p_lps',
   parent_filter=grammar.LinkSentence(
      'universal:entity=(token) & mansi:simple_pos=(pronoun) & mansi:pronoun:is_personal=()',
      rombandeeva
   )
)

rombandeeva.add_element('universal:morpheme', '^на!', 'na_pr_suffix').applied(
    grammar.LinkSentence('# & mansi:simple_pos=(pronoun) & mansi:pronoun:is_personal=()'),
    [
        grammar.Action('gram:set_refl')  # REFL
    ]
).add_class('na_suff')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '? > .lich_ukaz > .na_suff > .p_lps',
    parent_filter=grammar.LinkSentence(
      'universal:entity=(token) & mansi:simple_pos=(pronoun) & mansi:pronoun:is_personal=()',
      rombandeeva
   ),
   strict=True
)

lps_matrix_2 = [
    ['sing', '1', '^м'],
    ['sing', '3', '^тэ'],
    ['dual', '1', '^ме!н'],
    ['dual', '3', '^тэ!н'],
    ['plur', '1', '^в'],
    ['plur', '3', '^ныл']
]

p_lps_filter = '# & universal:entity=(token) & mansi:basic_pos=(pronoun) & mansi:pronoun:is_personal=()'
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
    '2a_sing/plur_2_suff_lps'
).applied(
    grammar.LinkSentence(p_lps_filter),
    [
        grammar.Action('mansi:make_lp', arguments=['sing', '2'], branching=True),
        grammar.Action('mansi:make_lp', arguments=['plur', '2'], branching=True)
    ]
).add_class('p_lps')

# page 98-99!

interrog_pronoun = [
    ['хотъют', 'хотъютыг', 'хотъютыт', 'hotyut'],
    ['хо!н!ха', 'хо!н!хаг', 'хо!н!хат', 'honha'],
    ['ма!ныр', 'ма!нарыг', 'ма!нарыт', 'manyr']
]

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

det_pronoun_matrix = [
    ['tamle', 'тамле'],
    ['kasyn', 'ка!сын!'],
    ['pussyn', 'пуссын'],
    ['tova', 'то!ва'],
    ['tasavit', 'таса!вит']
]
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

hotpa = ['хо!тпа', 'хо!тпаг', 'хо!тпат']
matyr = ['матыр', 'матарыг', 'матарыт']

for j in range(3):
    for s in ('hotpa', 'matyr'):
        rombandeeva.add_element(
            'universal:token', eval(s)[j], 'pi_{}_{}'.format(s, num[j])
        ).applied(
            grammar.LinkSentence('# & universal:entity=(input)'),
            [
                grammar.Action('gram:number:set_{}'.format(num[j]))
            ]
        )

matyr_hotpa_matrix = [
    ['nom', 'хо!тпа', 'матыр'],
    ['dat', 'хо!тпан', 'матарн'],
    ['abl', 'хо!тпаныл', 'матарныл'],
    ['instr', 'хо!тпал', 'матарыл'],
    ['trans', 'хо!тпаг', 'матарыг']
]

for case, h_paradigm, m_paradigm in matyr_hotpa_matrix:
    rombandeeva.add_element(
        'universal:token', h_paradigm, 'hotpa_{}'.format(case)
    ).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('gram:case:set_{}'.format(case))
        ]
    )
    rombandeeva.add_element(
        'universal:token', m_paradigm, 'matyr_{}'.format(case)
    ).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('gram:case:set_{}'.format(case))
        ]
    )

# negative pronouns нэ!мхо!тпа and нэ!матыр
for case, h_paradigm, m_paradigm in matyr_hotpa_matrix:
    rombandeeva.add_element(
        'universal:token', 'нэ!м' + h_paradigm, 'NEG_hotpa_{}'.format(case)
    ).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('gram:case:set_{}'.format(case))
        ]
    )
    rombandeeva.add_element(
        'universal:token', 'нэ!' + m_paradigm, 'NEG_matyr_{}'.format(case)
    ).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('gram:case:set_{}'.format(case))
        ]
    )

# pronouns need further description

# page 107, VERB
# `not a derivative` parameter
rombandeeva.add_element('universal:morpheme', '^ахт', 'aht_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:base_length=(1)'),
    [
        grammar.Action('gram:make_reflexive')  # REFL
    ]
).add_class('trans_suffs')

rombandeeva.add_element('universal:morpheme', '^хат', 'hat_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:base_length=(1)'),
    [
        grammar.Action('gram:make_reflexive')  # REFL
    ]
).add_class('trans_suffs')

rombandeeva.add_element('mansi:morphemeYU', '^ыгл', 'ygl_suffix').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:intransitive=()'
    ),
    [
        grammar.Action('gram:make_transitive')  # TR
    ]
).add_class('trans_suffs')

rombandeeva.add_element('mansi:morphemeYU', '^гл', 'gl_suffix').applied(
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

rombandeeva.add_element('universal:morpheme', '^л', 'l_oc_suffix').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb) & [gram:person=(1) | gram:person=(2)]'
    ),
    [
        grammar.Action('mansi:set_obj_conj')
    ]
).add_class('conj_set')

rombandeeva.add_element('universal:morpheme', '^тэ', 'te_oc_suffix').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:person=(3)'
    ),
    [
        grammar.Action('mansi:conj:set_obj')
    ]
).add_class('conj_set')

rombandeeva.add_element('universal:morpheme', '^т', 't_oc_suffix').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb) & gram:person=(3)'
    ),
    [
        grammar.Action('mansi:conj:set_obj')
    ]
).add_class('conj_set')

rombandeeva.add_element('universal:morpheme', '^ве', 've_spc_suffix').applied(
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

present_s_consonant_suffs = [('ye!g', 'е!г'), ('i', 'и'), ('ye', 'е'), ('ye!', 'е!')]
for code, suff in present_s_consonant_suffs:
    rombandeeva.add_element(
        'universal:morpheme',
        '^' + suff,
        '{}_present_suff'.format(code)
    ).applied(
        grammar.LinkSentence(
            '''# & universal:entity=(token)
            & mansi:basic_pos=(verb)
            & universal:reg_match=(%MANSI_CONS_END%){pre=(''' + suff + ''')}
            '''
        ),
        [
            grammar.Action('gram:tense:set_present')
        ]
    )

present_h_consonant_suffs = [('eg', 'эг'), ('e!g', 'э!г'), ('y', 'ы'), ('e', 'э'), ('e!', 'э!')]
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
            & universal:reg_match=(%MANSI_CONS_END%){pre=(''' + suff + ''')}'''
        ),
        [
            grammar.Action('gram:tense:set_present')
        ]
    )

rombandeeva.add_element('universal:morpheme', '^ыс', 'ys_past_suffix').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
            & mansi:basic_pos=(verb)
            & universal:syl_count=(1)
            & universal:reg_match(%MANSI_CONS_1,2_END%){pre=(ыс)}'''
    ),
    [
        grammar.Action('gram:tense:set_past')
    ]
).add_class('past_suffixes')

rombandeeva.add_element('universal:morpheme', '^ас', 'as_past_suffix').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
            & mansi:basic_pos=(verb)
            & universal:syl_count>(1)
            & universal:reg_match=(%MANSI_CONS_1,2_END%){pre=(ас)}'''
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
            & universal:syl_count>(1)
            & universal:reg_match(%MANSI_VOW_END%){pre=(с)}'''
    ),
    [
        grammar.Action('gram:tense:set_past')
    ]
).add_class('past_suffixes')

rombandeeva.add_element('universal:morpheme', '^м', 'm_unob_suffix').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & [ mansi:conj=(objectless) | mansi:conj=(obj) ]
        & mansi:syl_count=(1)
        & universal:reg_match=(%MANSI_CONS_END%){pre=(м)}'''
    ),
    [
        grammar.Action('gram:mood:set_latentive'),
        grammar.Action('mansi:tense:set_past')
    ]
)

rombandeeva.add_element('universal:morpheme', '^ум', 'um_unob_suffix').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & [ mansi:conj=(objectless) | mansi:conj=(obj) ]
        & mansi:syl_count=(1)
        & universal:reg_match=(%MANSI_CONS_END%){pre=(ум)}
        & universal:reg_match!=([лн]$){pre=(ум)}'''
    ),
    [
        grammar.Action('gram:mood:set_latentive'),
        grammar.Action('mansi:tense:set_past')
    ]
)

rombandeeva.add_element('universal:morpheme', '^ам', 'am_unob_suffix').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & [ mansi:conj=(objectless) | mansi:conj=(obj) ]
        & mansi:syl_count>=(1)
        & universal:reg_match=([лн]$){pre=(ам)}'''
    ),
    [
        grammar.Action('gram:mood:set_latentive'),
        grammar.Action('mansi:tense:set_past')
    ]
)

rombandeeva.add_element('mansi:morpheme_soft', '^има', 'ima_unob_suffix').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & gram:transitive=()
        & mansi:syl_count>=(1)
        & universal:reg_match=([лнст]'$){pre=(има)}
        & mansi:conj=(subj_pass)'''
    ),
    [
        grammar.Action('gram:mood:set_latentive')
    ]
)

rombandeeva.add_element('mansi:morpheme_soft', '^ыма', 'yma_unob_suffix').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & gram:transitive=()
        & mansi:syl_count>=(1)
        & universal:reg_match=([лнст]$){pre=(ыма)}
        & mansi:conj=(subj_pass)'''
    ),
    [
        grammar.Action('gram:mood:set_latentive')
    ]
)

# page 116
# INDICATIVE

rombandeeva.add_element('universal:morpheme', '^ум', 'um_1sing_ind_objless').applied(
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

rombandeeva.add_element('universal:morpheme', '^н', 'n_2sing_ind_objless').applied(
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

rombandeeva.add_element('universal:morpheme', '^ын', 'yn_2sing_ind_objless').applied(
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

rombandeeva.add_element('universal:morpheme', '^ме!н', 'men_1dual_ind_objless').applied(
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

rombandeeva.add_element('universal:morpheme', '^ы!н', 'yn_2_dual/plur_ind_objless').applied(
    grammar.LinkSentence(
        '''#
        & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:conj=(objectless)'''
    ),
    [
        grammar.Action('mansi:verb:set_person', arguments=['2']),
        grammar.Action('gram:number:set_dual', branching=True),
        grammar.Action('gram:number:set_plur', branching=True)
    ]
).add_class('objectless_conj_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^ыг', 'yg_3dual_ind_objless').applied(
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

rombandeeva.add_element('universal:morpheme', '^г', 'g_3dual_ind_objless').applied(
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

rombandeeva.add_element('universal:morpheme', '^ув', 'uv_1plur_ind_objless').applied(
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

rombandeeva.add_element('universal:morpheme', '^в', 'v_1plur_ind_objless').applied(
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

rombandeeva.add_element('universal:morpheme', '^э!в', 'ev_1plur_ind_objless').applied(
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

rombandeeva.add_element('universal:morpheme', '^ыт', 'yt_3plur_ind_objless').applied(
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
    '<[gram:verb:infinitive=()]> *1 <[mansi:lemma=(патун!кве)]>',
    'future_patunkwe'
).applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('gram:tense:set_future')
    ]
)

# page 121.add_class('verb_conj_personal')

rombandeeva.add_element('mansi:morphemeYU', '^и', 'i_suffix_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(obj)'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('obj_conj_tense')

rombandeeva.add_element('universal:morpheme', '^л', 'l_suffix_object_sing').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:object_number:set_sing')
    ]
).add_class('obj_conj_object_number').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:morphemeYU', '^аг', 'ag_suffix_object_dual').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:object_number:set_dual')
    ]
).add_class('obj_conj_object_number').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:morphemeYU', '^ан', 'an_suffix_object_plur').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:object_number:set_plur')
    ]
).add_class('obj_conj_object_number').add_class('verb_conj_personal')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '.obj_conj_tense > .obj_conj_object_number',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:conj=(obj)')
)

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '#i_suffix_present > .obj_conj_object_number > .l_friendly',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:conj=(obj)')
)

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '#i_suffix_present > .l_non_friendly',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:conj=(obj)')
)

rombandeeva.add_element('mansi:VowMorpheme', '^ум', 'um_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('l_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^ын', 'yn_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['2']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('l_friendly').add_class('verb_conj_personal')


rombandeeva.add_element('universal:morpheme', '^тэ', 'te_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('l_non_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^ме!н', 'men_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('l_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^ы!н', 'yyn_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['2']),
        grammar.Action('gram:number:set_dual', branching=True),
        grammar.Action('gram:number:set_plur', branching=True)
    ]
).add_class('l_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^тэ!н', 'teen_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('l_non_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^ув', 'uv_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('l_friendly').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:morphemeYU', '^а!ныл', 'jaanyl_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('verb_conj_personal')

# IN PLUR ONLY:
rombandeeva.add_element('universal:morpheme', '^ныл', 'nyl_obj_conj').applied(
    grammar.LinkSentence('# & universal:entity=(tooken) & mansi:conj=(obj)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('verb_conj_personal')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '#an_suffix_obj_plur > #nyl_obj_conj',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:conj=(obj)'),
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
    '#ve_spc_suffix > .subj_pass_suffixes |',
    parent_filter=grammar.LinkSentence(
        'universal:entity=(token) & mansi:conj=(subj_pass)'
    )
)

rombandeeva.add_element('mansi:VowMorpheme', '^м', 'm_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^н', 'n_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['2']),
        grammar.Action('gram:number:set_sing', branching=True),
        grammar.Action('gram:number:set_dual', branching=True),
        grammar.Action('gram:number:set_plur', branching=True)
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', grammar.Temp.NULL, 'null_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_sing')
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^ме!н', 'men_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^г', 'g_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^в', 'v_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['1']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.add_element('mansi:VowMorpheme', '^т', 't_suffix_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:conj=(subj_pass)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_plur')
    ]
).add_class('subj_pass_suffixes').add_class('verb_conj_personal')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '.past_suffixes > .subj_pass_suffixes',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:conj=(subj_pass)')
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
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('imperative_present_2sg')

rombandeeva.add_element('universal:morpheme', '^е', 'ye_suffix_imperative_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('imperative_present_2sg')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '| .BASE > .imperative_present_2sg  >> .obj_conj_object_number > #n_suffix_imperative |',
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

rombandeeva.add_element('universal:morpheme', '^э!', 'ee_suffix_imperative_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('imperative_present_2du_pl')

rombandeeva.add_element('universal:morpheme', '^е!', 'yee_suffix_imperative_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('imperative_present_2du_pl')

# NEEDS IMPROVEMENT TO SUPPORT MUTATION STRATEGY

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '| .BASE > .imperative_present_2du_pl >> .obj_conj_object_number > #n_suffix_imperative |',
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

rombandeeva.add_element('mansi:VowMorpheme', '^$[ы]нув', 'ynuv_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & [mansi:syl_count=(1) | mansi:syl_count=(3)]'),
    [
        grammar.Action('gram:mood:set_conjunctive')
    ]
).add_class('nuv_suffixes')

rombandeeva.add_element('mansi:VowMorpheme', '^$[а]нув', 'anuv_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & [mansi:syl_count=(2)]'),
    [
        grammar.Action('gram:mood:set_conjunctive')
    ]
).add_class('nuv_suffixes')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '.nuv_suffixes >> .obj_conj_object_number >+ .verb_conj_personal'
)

rombandeeva.add_element('universal:morpheme', '^э', 'e_conjunctive_obj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & gram:mood=(conjunctive)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_sing', branching=True),
        grammar.Action('gram:number:set_plur', branching=True)
    ]
).add_class('verb_conj_personal')

rombandeeva.add_element('universal:morpheme', '^е', 'ye_conjunctive_obj').applied(
    grammar.LinkSentence('# & universal:entity=(token) & gram:mood=(conjunctive)'),
    [
        grammar.Action('mansi:verb:set_person', arguments=['3']),
        grammar.Action('gram:number:set_dual')
    ]
).add_class('verb_conj_personal')

### verb_conj_personal EXTENSION
vcp_ext_matrix = [
    ['sing', '1', 'ум', 'um'],
    ['sing', '2', 'ын', 'yn'],
    ['sing', '3', 'е', 'e'],
    ['dual', '1', 'ме!н', 'men'],
    ['dual', '3', 'е!н', 'en'],
    ['plur', '1', 'ув', 'uv'],
    ['plur', '3', 'а!ныл', 'anyl']
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

rombandeeva.add_element('universal:morpheme', '^н', 'n_for_latentive_praes').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & mansi:syl_count=(1)'),
    [
        grammar.Action('gram:mood:set_latentive')
    ]
).add_class('latentive_suffs_present').add_class('latentive_suffs')

rombandeeva.add_element('universal:morpheme', '^ын', 'yn_for_latentive_praes').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb) & universal:reg_match=(%MANSI_CONS_TWO_MORE_END%)'
    ),
    [
        grammar.Action('gram:mood:set_latentive')
    ]
).add_class('latentive_suffs_present').add_class('latentive_suffs')

rombandeeva.add_element('universal:morpheme', '^ан', 'an_for_latentive_praes').applied(
    grammar.LinkSentence(
        '# & universal:entity=(token) & mansi:basic_pos=(verb) & universal:reg_match=(%MANSI_CONS_TWO_MORE_END%)'
    ),
    [
        grammar.Action('gram:mood:set_latentive')
    ]
).add_class('latentive_suffs_present').add_class('latentive_suffs')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '| .BASE > .latentive_suffs >> .tense_suffs_latentive >> .obj_conj_object_number >+ .verb_conj_personal',
    parent_filter=grammar.LinkSentence('universal:entity=(token) & mansi:basic_pos=(verb)')
)

rombandeeva.add_element('universal:morpheme', '^е', 'ye_latentive_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & gram:mood=(latentive)'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('tense_suffs_latentive')

rombandeeva.add_element('universal:morpheme', '^е!', 'yee_latentive_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & gram:mood=(latentive)'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('tense_suffs_latentive')

rombandeeva.add_element('universal:morpheme', '^э', 'e_latentive_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & gram:mood=(latentive)'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('tense_suffs_latentive')

rombandeeva.add_element('universal:morpheme', '^э!', 'ee_latentive_present').applied(
    grammar.LinkSentence('# & universal:entity=(token) & gram:mood=(latentive)'),
    [
        grammar.Action('gram:tense:set_present')
    ]
).add_class('tense_suffs_latentive')

# page 133, try if this works for the tables on p. 132-133

rombandeeva.add_element('universal:morpheme', '^м', 'm_suffix_past_latentive').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb) & universal:reg_match=(%MANSI_VOW%){post=()}'),
    [
        grammar.Action('gram:tense:set_past'),
        grammar.Action('gram:mood:set_latentive')
    ]
).add_class('latentive_suffs_past').add_class('latentive_suffs')

rombandeeva.add_element('universal:morpheme', '^ум', 'um_suffix_past_latentive').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & universal:reg_match=(%MANSI_CONS%){pre=(ум)}
        & universal:reg_match!=([лн]){pre=(ум)}
        & universal:reg_match=(%MANSI_CONS+I%){post=()}
        '''
    ),
    [
        grammar.Action('gram:tense:set_past'),
        grammar.Action('gram:mood:set_latentive')
    ]
).add_class('latentive_suffs_past').add_class('latentive_suffs')

rombandeeva.add_element('universal:morpheme', '^ам', 'am_suffix_past_latentive').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:syl_count=(1){pre=(ам)}
        '''
    ),
    [
        grammar.Action('gram:tense:set_past')
    ]
).add_class('latentive_suffs_past').add_class('latentive_suffs')

# i am not sure we need syl_count there
rombandeeva.add_element('universal:morpheme', '^у!м', 'uum_suffix_past_latentive').applied(
    grammar.LinkSentence(
        '''# & universal:entity=(token)
        & mansi:basic_pos=(verb)
        & mansi:syl_count=(1){pre=(у!м)}
        & universal:reg_match=(%MANSI_VOW%[лн]){pre=(у!м)}
        '''
    ),
    [
        grammar.Action('gram:tense:set_past'),
        grammar.Action('gram:mood:set_latentive')
    ]
).add_class('latentive_suffs_past').add_class('latentive_suffs')

rombandeeva.add_element('mansi:VowMorpheme', '^има', 'ima_latentive_subj_pass').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:mood:set_latentive'),
        grammar.Action('mansi:conj:set_subj_pass')
    ]
).add_class('latentive_suff_subj_pass')

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '| .BASE > .latentive_suff_subj_pass > .verb_conj_personal |',
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

rombandeeva.add_element('universal:morpheme', '^мыгт', 'mygt_suffix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_inchoative') # INCH
    ]
).add_class('word_formation')

dur_suffs = ['а!нт', 'ант', 'гал', 'л', 'ас', 'асьл', 'ал', 'а!л', 'с', 'ыгл', 'тл']

for e, suff in enumerate(dur_suffs):
    rombandeeva.add_element('universal:morpheme', '^' + suff, 'dur_suff_' + str(e)).applied(
        grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
        [
            grammar.Action('gram:set_durative')  # DUR
        ]
    ).add_class('word_formation')


iter_suffs = ['а!л', 'ыгл', 'гала!л', 'ыгла!л', 'а!лыгл', 'ата!л', 'лант', 'гал']

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

rombandeeva.add_element('universal:morpheme', '^те', 'te_suffix_adj').applied(
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
        grammar.Action('mansi:noun_to_verb'),
        grammar.Action('gram:make_transitive', branching=True),
        grammar.Action('gram:make_intransitive', branching=True)
    ]
).add_class('noun_to_verb_suff')

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


rombandeeva.add_element('universal:morpheme', '_^хот', 'hot_prefix').applied(
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

rombandeeva.add_element('universal:morpheme', '_^э!л', 'eel_prefix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('direct:set_meaning', arguments=['от'])
    ]
)

rombandeeva.add_element('universal:morpheme', '_^ёл', 'yol_prefix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('direct:set_meaning', arguments=['c'])
    ]
)

rombandeeva.add_element('universal:morpheme', '_^но!х', 'noh_prefix').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('direct:set_meaning', arguments=['вверх'])
    ]
)

rombandeeva.add_element('universal:morpheme', '_^юв', 'yuv_prefix').applied(
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
    '<[mansi:basic_pos=(noun)]> *1 <[mansi:lemma=(патун!кве)]>',
    'compound_verb'
).applied(
    grammar.LinkSentence('# & universal:entity=(input)'),
    [
        grammar.Action('mansi:basic_pos:set_verb')
    ]
)

rombandeeva.add_element('mansi:VowMorpheme', '^йт', 'yt_suffix_rus').applied(
    grammar.LinkSentence('# & universal:entity=(token)'),
    [
        grammar.Action('mansi:basic_pos:set_verb'),
        grammar.Action('mansi:russian_loan_word')
    ]
)

# page 143

rombandeeva.add_element('universal:morpheme', '^м', 'm_participle').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_participle'),  # PTCP
        grammar.Action('gram:set_resultative')  # RES
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^ум', 'um_participle').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_participle'),  # PTCP
        grammar.Action('gram:set_resultative')  # RES
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^ам', 'am_participle').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_participle'),  # PTCP
        grammar.Action('gram:set_resultative')  # RES
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^им', 'im_participle').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('gram:set_converb')  # CVB
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^н', 'n_participle').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_participle'),  # PTCP
        grammar.Action('gram:set_present')  # PRS
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^нэ', 'nе_participle').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_participle'),  # PTCP
        grammar.Action('gram:set_present')  # PRS
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^нэ!', 'nee_participle').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_participle'),  # PTCP
        grammar.Action('gram:set_present')  # PRS
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^ын', 'yn_participle').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_participle'),  # PTCP
        grammar.Action('gram:set_present')  # PRS
    ]
).add_class('participle_suffix')

rombandeeva.add_element('universal:morpheme', '^ан', 'an_participle').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_participle'),  # PTCP
        grammar.Action('gram:set_present')  # PRS
    ]
).add_class('participle_suffix')

# TRANSGRESSIVE

rombandeeva.add_element('universal:morpheme', '^им', 'im_transgressive').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_transgressive')
    ]
)

rombandeeva.add_element('universal:morpheme', '^ым', 'ym_transgressive').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_transgressive')
    ]
)

rombandeeva.add_element('universal:morpheme', '^м', 'm_transgressive').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
    [
        grammar.Action('mansi:make_transgressive')
    ]
)

rombandeeva.add_element('universal:morpheme', '^т', 't_transgressive').applied(
    grammar.LinkSentence('# & universal:entity=(token) & mansi:basic_pos=(verb)'),
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
    ('ки!выр', 'ki*vyr'),
    ('хал', 'hal'),
    ('ва!та', 'va*ta'),
    ('ёлы-па!л', 'yoly_pa*l'), # collocation as variant
    ('нуми-па!л', 'numi_pa*l') # collocation as variant
]

for pp_word, pp_id in postpos_mutable:
    rombandeeva.add_element('universal:token', pp_word, pp_id).applied(
        grammar.LinkSentence('# & universal:entity=(input)'),
        [
            grammar.Action('mansi:basic_pos:set_postpos')
        ]
    ).add_class('postpos_mutable')

#rombandeeva.get_class('postpos_mutable', await=True).intrusion(
#    class_list=['case_suffixes', 'verb_conj_personal']
#)

rombandeeva.get_system('universal:morpheme').subclasses_order(
    '.case_suffixes > .verb_conj_personal',
    parent_filter=grammar.LinkSentence('universal:class=(postpos_mutable)')
)

rombandeeva.add_element('universal:token', 'па!л', 'pa*l_postpos_in_colloc').applied(
    grammar.LinkSentence('# & universal:entity=(collocation)'),
    [
        grammar.Action('mansi:basic_pos:set_postpos')
    ]
).add_class('postpos_mutable')

postpos_unmutable = [
    ['мус', ('до')],
    ['ёт', ('с')],
    ['ма!гыс', ('для', 'за')],
    ['палт', ('к', 'у')],
    ['тармыл', ('на')],
    ['паттыиг', ('вместо', 'взамен')],
    ['уртыиг', ('вместо', 'взамен')],
    ['пе!нтсыл', ('вместо', 'взамен')],
    ['у!лтта', ('через')],
    ['нупыл', ('в направлении')],
    ['хосыт', ('по')],
    ['ляльт', ('против')],
    ['торыг', ('перед')],
    ['урыл', ('о', 'про')],
    ['о!вылтытыт', ('о', 'про')],
    ['коны-пал', ('кроме')],
    ['сыс', ('во время')],
    ['э!ртын', ('когда')],
    ['э!рт', ('когда')],
    ['хольт', ('как')],
    ['та!ра', ('мимо')]
]

pp_i = 0
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


text = 'ляххалыт, потрыт интернетыт ловьтэгыт'
input_container = grammar.InputContainer(text, prevent_auto=True)
input_container.onseg_hook_bank.stemmer = mansi_stemmer.stemmer.Stem(save_cache='mansi_stemmer/cache_table.sqlite3')
input_container.onseg_hook_bank.end_del = [
    coll.minor.Clear.remove_spec_chars('universal:morpheme', ct.get_content())
    for ct in rombandeeva.iter_content_filter(lambda x: True, system_filter='universal:morpheme')
    if ct.get_content() != grammar.Temp.NULL
]
input_container.onseg_hook_bank.end_del = list(set(input_container.onseg_hook_bank.end_del))


def stem_token(ic, elem):
    stem_results = ic.onseg_hook_bank.stemmer.find(
        elem.get_content(),
        start_del=[],
        end_del=ic.onseg_hook_bank.end_del,
        end_add=['ӈкве', 'аӈкве', 'юӈкве', 'уӈкве']
    )
    pos_tags = [stem['pos_tags'][0] for stem in stem_results]
    pos_tags = list(set(pos_tags))
    if stem_results:
        for stem in stem_results:
            for substem in stem['stems']:
                ic.ic_log.add_log(
                    "STEMS_EXTRACTED",
                    element_id=elem.get_ic_id(),
                    cluster_id=elem.get_parent_ic_id(),
                    positions=substem[1],
                    group=pos_tags.index(stem['pos_tags'][0]),
                    status='preview'
                )
        for group_index, pos_tag in enumerate(pos_tags):
            ic.ic_log.add_log(
                "POS_EXTRACTED",
                element_id=elem.get_ic_id(),
                cluster_id=elem.get_parent_ic_id(),
                pos_tag=pos_tag,
                group=group_index,
                status='preview'
            )
    else:
        ic.ic_log.add_log(
            "STEMS_EXTRACTED",
            element_id=elem.get_ic_id(),
            cluster_id=elem.get_parent_ic_id(),
            pos_tag="unknown",
            positions=list(range(len(elem.get_content()))),
            group=0,
            status='preview'
        )
        ic.ic_log.add_log(
            "POS_EXTRACTED",
            element_id=elem.get_ic_id(),
            cluster_id=elem.get_parent_ic_id(),
            pos_tag="unknown",
            group=0,
            status='preview'
        )

    if elem.is_last_in_cluster('universal:token'):
        ic.nullint_for_cluster(elem.get_parent_ic_id())
        for elem in ic.get_by_ic_id(elem.get_parent_ic_id()).get_childs():
            stems_ext = ic.ic_log.get_log_sequence(
                "STEMS_EXTRACTED", element_id=elem.get_ic_id(), cluster_id=elem.get_parent_ic_id()
            )
            pos_ext = ic.ic_log.get_log_sequence(
                "POS_EXTRACTED", element_id=elem.get_ic_id(), cluster_id=elem.get_parent_ic_id()
            )
            for gr_index in range(len(pos_tags)):
                if gr_index >= len(pos_ext):
                    cel = ic.clone_within_cluster(elem, gr_index)
                    cel.set_parameter('mansi:basic_pos', pos_ext[0].get_prop('pos_tag'))
                    cel_stem = stems_ext[0]
                    cel_stem.set_prop('element_id', cel.get_ic_id())
                    cel_stem.remove_prop('status')
                    ic.ic_log.add_log_document("STEMS_EXTRACTED", cel_stem)
                else:
                    cel = ic.clone_within_cluster(elem, gr_index)
                    cel.set_parameter('mansi:basic_pos', pos_ext[gr_index].get_prop('pos_tag'))
                    cel_stem = stems_ext[gr_index]
                    cel_stem.set_prop('element_id', cel.get_ic_id())
                    cel_stem.remove_prop('status')
                    ic.ic_log.add_log_document("STEMS_EXTRACTED", cel_stem)

        ic.ic_log.remove_logs_from_sector(
            "STEMS_EXTRACTED", ic.ic_log.get_log_sequence("STEMS_EXTRACTED", status='preview')
        )
        ic.ic_log.remove_logs_from_sector(
            "POS_EXTRACTED", ic.ic_log.get_log_sequence("POS_EXTRACTED", status='preview')
        )


input_container.add_onseg_hook('universal:token', stem_token)
input_container.start_auto_segmentation()
input_container.onseg_hook_bank.stemmer.write_cache()
input_container.connect_mc(rombandeeva)
input_container.run_mc_analysis()

print([(x.get_system_name(), x.get_content()) for x in input_container.elements])


# page 159: ?

### RUN seq:correction:mansi* mutation
### create mansi:morphemeYU