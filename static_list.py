@new_func('sem:make_opposite', params_affected=['sem:is_opposite'])
# args -> []
def sem_make_opposite(element, arguments=[], branching=[]):
    element.set_parameter('sem:is_opposite', True)
    return element


@new_func('sem:make_causative', params_affected=['sem:causative'])
# args -> []
def sem_make_causative(element, arguments=[], branching=[]):
    element.set_parameter('sem:causative', True)
    return element


@new_func('gram:make_transitive', params_affected=['gram:transitive'])
# args -> []
def gram_make_transitive(element, arguments=[], branching=[]):
    element.set_parameter('gram:transitive', True)
    return element


@new_func('gram:number:set_sing', params_affected=['gram:number'])
# args -> []
def gram_number_set_sing(element, arguments=[], branching=[]):
    element.set_parameter('gram:number', 'sing')
    return element


@new_func('gram:number:set_dual', params_affected=['gram:number'])
# args -> []
def gram_number_set_dual(element, arguments=[], branching=[]):
    element.set_parameter('gram:number', 'dual')
    return element


@new_func('mansi:make_lp', params_affected=[])
# args -> [sing, 1]
def mansi_make_lp(element, arguments=[], branching=[]):
    element.set_parameter('gram:possessor:number', arguments[0])
    element.set_parameter('gram:possessor:person', arguments[1])
    return element


@new_func('gram:number:set_plur', params_affected=['gram:number'])
# args -> []
def gram_number_set_plur(element, arguments=[], branching=[]):
    element.set_parameter('gram:number', 'plur')
    return element


@new_func('gram:case:set_main', params_affected=['gram:case'])
# args -> []
def gram_case_set_main(element, arguments=[], branching=[]):
    element.set_parameter('gram:case', 'main')
    return element


@new_func('gram:case:set_lat', params_affected=['gram:case'])
# args -> []
def gram_case_set_lat(element, arguments=[], branching=[]):
    element.set_parameter('gram:case', 'lat')
    return element


@new_func('gram:case:set_loc', params_affected=['gram:case'])
# args -> []
def gram_case_set_loc(element, arguments=[], branching=[]):
    element.set_parameter('gram:case', 'loc')
    return element


@new_func('gram:case:set_abl', params_affected=['gram:case'])
# args -> []
def gram_case_set_abl(element, arguments=[], branching=[]):
    element.set_parameter('gram:case', 'abl')
    return element


@new_func('gram:case:set_instr', params_affected=['gram:case'])
# args -> []
def gram_case_set_instr(element, arguments=[], branching=[]):
    element.set_parameter('gram:case', 'instr')
    return element


@new_func('gram:case:set_trans', params_affected=['gram:case'])
# args -> []
def gram_case_set_trans(element, arguments=[], branching=[]):
    element.set_parameter('gram:case', 'trans')
    return element


@new_func('gram:case:set_voc', params_affected=['gram:case'])
# args -> []
def gram_case_set_voc(element, arguments=[], branching=[]):
    element.set_parameter('gram:case', 'voc')
    return element


@new_func('gram:verb:set_infinitive', params_affected=['gram:verb:infinitive'])
# args -> []
def gram_verb_set_infinitive(element, arguments=[], branching=[]):
    element.set_parameter('gram:verb:infinitive', True)
    return element


@new_func('mansi:verb_to_noun', params_affected=['mansi:from_verb'])
# args -> []
def mansi_verb_to_noun(element, arguments=[], branching=[]):
    element.set_parameter('mansi:from_verb', True)
    return element


@new_func('mansi:sem:tool-or-action', params_affected=['sem:prop2'])
# args -> []
def mansi_sem_tool_or_action(element, arguments=[], branching=[]):
    element.set_parameter('sem:prop2', True)
    return element


@new_func('mansi:adj_to_noun', params_affected=[])
# args -> []
def mansi_adj_to_noun(element, arguments=[], branching=[]):
    return element


@new_func('mansi:sem:obj-size', params_affected=[])
# args -> []
def mansi_sem_obj_size(element, arguments=[], branching=[]):
    return element


@new_func('mansi:verb_to_noun:size', params_affected=[])
# args -> []
def mansi_verb_to_noun_size(element, arguments=[], branching=[]):
    return element


@new_func('mansi:sem:coll', params_affected=[])
# args -> []
def mansi_sem_coll(element, arguments=[], branching=[]):
    return element


@new_func('gram:adj:comparative', params_affected=['gram:degree_of_comparison'])
# args -> []
def gram_adj_comparative(element, arguments=[], branching=[]):
    element.set_parameter('gram:degree_of_comparison', 'comparative')
    return element


@new_func('mansi:set_pred', params_affected=[])
# args -> []
def mansi_set_pred(element, arguments=[], branching=[]):
    element.set_parameter('gram:pred', True)
    return element


@new_func('gram:set_dimin', params_affected=[])
# args -> []
def gram_set_dimin(element, arguments=[], branching=[]):
    return element


@new_func('gram:adj:superlative', params_affected=['gram:degree_of_comparison'])
# args -> []
def gram_adj_superlative(element, arguments=[], branching=[]):
    element.set_parameter('gram:degree_of_comparison', 'superlative')
    return element


@new_func('gram:set_attr', params_affected=[])
# args -> []
def gram_set_attr(element, arguments=[], branching=[]):
    return element


@new_func('gram:noun_to_adj', params_affected=['mansi:from_noun'])
# args -> []
def gram_noun_to_adj(element, arguments=[], branching=[]):
    element.set_parameter('mansi:from_noun', True)
    return element


@new_func('sem:adj_to_noun_corresp', params_affected=['mansi:from_noune'])
# args -> []
def sem_adj_to_noun_corresp(element, arguments=[], branching=[]):
    element.set_parameter('mansi:from_noun', True)
    return element


@new_func('gram:set_participle', params_affected=['mansi:basic_pos'])
# args -> []
def gram_set_participle(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'participle')
    return element


@new_func('mansi:russian_loan_word', params_affected=['mansi:is_russian'])
# args -> []
def mansi_russian_loan_word(element, arguments=[], branching=[]):
    element.set_parameter('mansi:is_russian', True)
    return element


@new_func('mansi:phrase_adj', params_affected=['mansi:basic_pos'])
# args -> []
def mansi_phrase_adj(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'adj')
    return element


@new_func('sem:magnification_colloc', params_affected=[])
# args -> []
def sem_magnification_colloc(element, arguments=[], branching=[]):
    return element


@new_func('gram:set_ord', params_affected=['gram:numeral_cat'])
# args -> []
def gram_set_ord(element, arguments=[], branching=[]):
    element.set_parameter('gram:numeral_cat', 'ordinal')
    return element


@new_func('gram:set_mult', params_affected=['gram:numeral_cat'])
# args -> []
def gram_set_mult(element, arguments=[], branching=[]):
    element.set_parameter('gram:numeral_cat', 'mult')
    return element


@new_func('gram:numeral:co_to_repet_colloc', params_affected=['gram:numeral_cat'])
# args -> []
def gram_numeral_co_to_repet_colloc(element, arguments=[], branching=[]):
    element.set_parameter('gram:numeral_cat', 'repetitive')
    return element


@new_func('gram:numeral:cardinal_to_round', params_affected=[])
# args -> []
def gram_numeral_cardinal_to_round(element, arguments=[], branching=[]):
    return element


@new_func('mansi:numeral:partial_colloc', params_affected=[])
# args -> []
def mansi_numeral_partial_colloc(element, arguments=[], branching=[]):
    return element


@new_func('mansi:pronoun:personal:1SG', params_affected=['mansi:basic_pos', 'mansi:pronoun:person', 'mansi:pronoun:number'])
# args -> []
def mansi_pronoun_personal_1sg(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'pronoun')
    element.set_parameter('mansi:pronoun:person', '1')
    element.set_parameter('mansi:pronoun:number', 'sing')
    return element


@new_func('gram:case:set_nom', params_affected=['gram:case'])
# args -> []
def gram_case_set_nom(element, arguments=[], branching=[]):
    element.set_parameter('gram:case', 'nom')
    return element


@new_func('gram:case:set_acc', params_affected=['gram:case'])
# args -> []
def gram_case_set_acc(element, arguments=[], branching=[]):
    element.set_parameter('gram:case', 'acc')
    return element


@new_func('gram:case:set_dat', params_affected=['gram:case'])
# args -> []
def gram_case_set_dat(element, arguments=[], branching=[]):
    element.set_parameter('gram:case', 'dat')
    return element


@new_func('mansi:pronoun:personal:2SG', params_affected=['mansi:basic_pos', 'mansi:pronoun:person', 'mansi:pronoun:number'])
# args -> []
def mansi_pronoun_personal_2sg(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'pronoun')
    element.set_parameter('mansi:pronoun:person', '2')
    element.set_parameter('mansi:pronoun:number', 'sing')
    return element


@new_func('mansi:pronoun:personal:3SG', params_affected=['mansi:basic_pos', 'mansi:pronoun:person', 'mansi:pronoun:number'])
# args -> []
def mansi_pronoun_personal_3sg(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'pronoun')
    element.set_parameter('mansi:pronoun:person', '3')
    element.set_parameter('mansi:pronoun:number', 'sing')
    return element


@new_func('mansi:pronoun:personal:1DU', params_affected=['mansi:basic_pos', 'mansi:pronoun:person', 'mansi:pronoun:number'])
# args -> []
def mansi_pronoun_personal_1du(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'pronoun')
    element.set_parameter('mansi:pronoun:person', '1')
    element.set_parameter('mansi:pronoun:number', 'dual')
    return element


@new_func('mansi:pronoun:personal:2DU', params_affected=['mansi:basic_pos', 'mansi:pronoun:person', 'mansi:pronoun:number'])
# args -> []
def mansi_pronoun_personal_2du(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'pronoun')
    element.set_parameter('mansi:pronoun:person', '2')
    element.set_parameter('mansi:pronoun:number', 'dual')
    return element


@new_func('mansi:pronoun:personal:3DU', params_affected=['mansi:basic_pos', 'mansi:pronoun:person', 'mansi:pronoun:number'])
# args -> []
def mansi_pronoun_personal_3du(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'pronoun')
    element.set_parameter('mansi:pronoun:person', '3')
    element.set_parameter('mansi:pronoun:number', 'dual')
    return element


@new_func('mansi:pronoun:personal:1PL', params_affected=['mansi:basic_pos', 'mansi:pronoun:person', 'mansi:pronoun:number'])
# args -> []
def mansi_pronoun_personal_1pl(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'pronoun')
    element.set_parameter('mansi:pronoun:person', '1')
    element.set_parameter('mansi:pronoun:number', 'plur')
    return element


@new_func('mansi:pronoun:personal:2PL', params_affected=['mansi:basic_pos', 'mansi:pronoun:person', 'mansi:pronoun:number'])
# args -> []
def mansi_pronoun_personal_2pl(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'pronoun')
    element.set_parameter('mansi:pronoun:person', '2')
    element.set_parameter('mansi:pronoun:number', 'plur')
    return element


@new_func('mansi:pronoun:personal:3PL', params_affected=['mansi:basic_pos', 'mansi:pronoun:person', 'mansi:pronoun:number'])
# args -> []
def mansi_pronoun_personal_3pl(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'pronoun')
    element.set_parameter('mansi:pronoun:person', '3')
    element.set_parameter('mansi:pronoun:number', 'plur')
    return element


@new_func('mansi:pronoun:lich_ukaz', params_affected=[])
# args -> []
def mansi_pronoun_lich_ukaz(element, arguments=[], branching=[]):
    return element


@new_func('mansi:pronoun:set_sol', params_affected=[])
# args -> []
def mansi_pronoun_set_sol(element, arguments=[], branching=[]):
    return element


@new_func('gram:set_refl', params_affected=[])
# args -> []
def gram_set_refl(element, arguments=[], branching=[]):
    return element


@new_func('mansi:pronoun:demonstrative', params_affected=[])
# args -> []
def mansi_pronoun_demonstrative(element, arguments=[], branching=[]):
    return element


@new_func('mansi:set_basic_pos:pronoun', params_affected=['mansi:basic_pos'])
# args -> []
def mansi_set_basic_pos_pronoun(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'pronoun')
    return element


@new_func('mansi:pronoun:determinative', params_affected=[])
# args -> []
def mansi_pronoun_determinative(element, arguments=[], branching=[]):
    return element


@new_func('gram:make_reflexive', params_affected=[])
# args -> []
def gram_make_reflexive(element, arguments=[], branching=[]):
    return element


@new_func('gram:make_intransitive', params_affected=['gram:intransitive'])
# args -> []
def gram_make_intransitive(element, arguments=[], branching=[]):
    element.set_parameter('gram:intransitive', True)
    return element


@new_func('mansi:set_obj_conj', params_affected=['mansi:conj'])
# args -> []
def mansi_set_obj_conj(element, arguments=[], branching=[]):
    element.set_parameter('mansi:conj', 'obj')
    return element


@new_func('mansi:conj:set_obj', params_affected=['mansi:conj'])
# args -> []
def mansi_conj_set_obj(element, arguments=[], branching=[]):
    element.set_parameter('mansi:conj', 'obj')
    return element


@new_func('mansi:conj:set_subj_pass', params_affected=['mansi:conj'])
# args -> []
def mansi_conj_set_subj_pass(element, arguments=[], branching=[]):
    element.set_parameter('mansi:conj', 'subj_pass')
    return element


@new_func('mansi:conj:set_objectless', params_affected=['mansi:conj'])
# args -> []
def mansi_conj_set_objectless(element, arguments=[], branching=[]):
    element.set_parameter('mansi:conj', 'objectless')
    return element


@new_func('gram:tense:set_present', params_affected=[])
# args -> []
def gram_tense_set_present(element, arguments=[], branching=[]):
    return element


@new_func('gram:tense:set_past', params_affected=[])
# args -> []
def gram_tense_set_past(element, arguments=[], branching=[]):
    return element


@new_func('gram:mood:set_latentive', params_affected=['gram:mood'])
# args -> []
def gram_mood_set_latentive(element, arguments=[], branching=[]):
    element.set_parameter('gram:mood', 'latentive')
    return element


@new_func('mansi:tense:set_past', params_affected=[])
# args -> []
def mansi_tense_set_past(element, arguments=[], branching=[]):
    return element


@new_func('mansi:verb:set_person', params_affected=[])
# args -> [1]
def mansi_verb_set_person(element, arguments=[], branching=[]):
    element.set_parameter('gram:person', arguments[0])
    return element


@new_func('gram:set_number:plur', params_affected=[])
# args -> []
def gram_set_number_plur(element, arguments=[], branching=[]):
    element.set_parameter('gram:number', 'plur')
    return element


@new_func('gram:tense:set_future', params_affected=[])
# args -> []
def gram_tense_set_future(element, arguments=[], branching=[]):
    return element


@new_func('mansi:object_number:set_sing', params_affected=[])
# args -> []
def mansi_object_number_set_sing(element, arguments=[], branching=[]):
    return element


@new_func('mansi:object_number:set_dual', params_affected=[])
# args -> []
def mansi_object_number_set_dual(element, arguments=[], branching=[]):
    return element


@new_func('mansi:object_number:set_plur', params_affected=[])
# args -> []
def mansi_object_number_set_plur(element, arguments=[], branching=[]):
    return element


@new_func('gram:mood:set_imperative', params_affected=['gram:mood'])
# args -> []
def gram_mood_set_imperative(element, arguments=[], branching=[]):
    element.set_parameter('gram:mood', 'imperative')
    return element


@new_func('gram:mood:set_indicative', params_affected=['gram:mood'])
# args -> []
def gram_mood_set_indicative(element, arguments=[], branching=[]):
    element.set_parameter('gram:mood', 'indicative')
    return element


@new_func('gram:mood:set_conjunctive', params_affected=['gram:mood'])
# args -> []
def gram_mood_set_conjunctive(element, arguments=[], branching=[]):
    element.set_parameter('gram:mood', 'conjunctive')
    return element


@new_func('gram:mood:set_optative', params_affected=['gram:mood'])
# args -> []
def gram_mood_set_optative(element, arguments=[], branching=[]):
    element.set_parameter('gram:mood', 'conjunctive')
    return element


@new_func('gram:set_semelfactive', params_affected=[])
# args -> []
def gram_set_semelfactive(element, arguments=[], branching=[]):
    return element


@new_func('gram:set_inchoative', params_affected=[])
# args -> []
def gram_set_inchoative(element, arguments=[], branching=[]):
    return element


@new_func('gram:set_durative', params_affected=[])
# args -> []
def gram_set_durative(element, arguments=[], branching=[]):
    return element


@new_func('gram:set_iterative', params_affected=[])
# args -> []
def gram_set_iterative(element, arguments=[], branching=[]):
    return element


@new_func('mansi:noun_to_verb', params_affected=['mansi:from_noun'])
# args -> []
def mansi_noun_to_verb(element, arguments=[], branching=[]):
    element.set_parameter('mansi:from_noun', True)
    return element


@new_func('direct:set_meaning', params_affected=[])
# args -> [от]
def direct_set_meaning(element, arguments=[], branching=[]):
    return element


@new_func('mansi:basic_pos:set_verb', params_affected=['mansi:basic_pos'])
# args -> []
def mansi_basic_pos_set_verb(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'verb')
    return element


@new_func('gram:set_resultative', params_affected=[])
# args -> []
def gram_set_resultative(element, arguments=[], branching=[]):
    return element


@new_func('gram:set_converb', params_affected=['mansi:basic_pos'])
# args -> []
def gram_set_converb(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'converb')
    return element


@new_func('mansi:make_participle', params_affected=['mansi:basic_pos'])
# args -> []
def mansi_make_participle(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'participle')
    return element


@new_func('gram:set_present', params_affected=[])
# args -> []
def gram_set_present(element, arguments=[], branching=[]):
    return element


@new_func('mansi:make_transgressive', params_affected=[])
# args -> []
def mansi_make_transgressive(element, arguments=[], branching=[]):
    return element


@new_func('mansi:basic_pos:set_adv', params_affected=['mansi:basic_pos'])
# args -> []
def mansi_basic_pos_set_adv(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'adv')
    return element


@new_func('gram:set_comparative', params_affected=[])
# args -> []
def gram_set_comparative(element, arguments=[], branching=[]):
    return element


@new_func('gram:adv:comparative', params_affected=[])
# args -> []
def gram_adv_comparative(element, arguments=[], branching=[]):
    return element


@new_func('gram:set_superlative', params_affected=[])
# args -> []
def gram_set_superlative(element, arguments=[], branching=[]):
    return element


@new_func('mansi:basic_pos:set_postpos', params_affected=['mansi:basic_pos'])
# args -> []
def mansi_basic_pos_set_postpos(element, arguments=[], branching=[]):
    element.set_parameter('mansi:basic_pos', 'postpos')
    return element


@new_func('mansi:translation:set_new', params_affected=[])
# args -> [до]
def mansi_translation_set_new(element, arguments=[], branching=[]):
    return element
