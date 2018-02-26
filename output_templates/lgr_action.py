#!/usr/bin/python3


def number_shorten(num):
    if num == 'sing':
        return 'SG'
    elif num == 'dual':
        return 'DU'
    elif num == 'plur':
        return 'PL'


lgr_values = {
    'gram:mood:set_indicative': lambda action: 'IND',
    'gram:make_transitive': lambda action: 'TR',
    'gram:set_present': lambda action: 'PRS',
    'mansi:pronoun:personal:3PL': lambda action: '3PL',
    'mansi:noun_to_verb': lambda action: None,
    'mansi:conj:set_objectless': lambda action: None,  # ?
    'gram:numeral:cardinal_to_round': lambda action: None,
    'gram:numeral:co_to_repet_colloc': lambda action: None,
    'gram:case:set_trans': lambda action: 'TRANS',
    'mansi:sem:obj-size': lambda action: 'SBST.Q',
    'mansi:pronoun:personal:2DU': lambda action: '2DU',
    'gram:verb:set_infinitive': lambda action: 'INF',
    'mansi:object_number:set_sing': lambda action: 'SG.O',
    'gram:tense:set_present': lambda action: 'PRS',
    'gram:case:set_acc': lambda action: 'ACC',
    'mansi:set_basic_pos:pronoun': lambda action: 'PN',
    'gram:set_refl': lambda action: 'REFL',
    'mansi:verb_to_noun:size': lambda action: 'SBST.Q',
    'mansi:basic_pos:set_adv': lambda action: 'ADV',
    'mansi:phrase_adj': lambda action: None,  # ?
    'gram:set_comparative': lambda action: 'CMPR',
    'mansi:sem:tool-or-action': lambda action: 'PROP2',
    'gram:set_resultative': lambda action: 'RES',
    'gram:set_converb': lambda action: 'CVB',
    'gram:number:set_plur': lambda action: 'PL',
    'gram:number:set_dual': lambda action: 'DU',
    'gram:set_participle': lambda action: 'PTCP',
    'gram:set_dimin': lambda action: 'DIM',
    'mansi:pronoun:personal:1SG': lambda action: '1SG',
    'mansi:conj:set_obj': lambda action: 'O',
    'mansi:pronoun:personal:3DU': lambda action: '3DU',
    'sem:make_causative': lambda action: 'CAUS',
    'mansi:pronoun:personal:2SG': lambda action: '2SG',
    'mansi:make_lp': lambda action: action.get_arguments()[1] + number_shorten(action.get_arguments()[0]),
    'mansi:basic_pos:set_postpos': lambda action: 'POST',
    'gram:mood:set_latentive': lambda action: 'AUD',
    'mansi:pronoun:lich_ukaz': lambda action: 'EMPH',
    'mansi:pronoun:personal:2PL': lambda action: '2PL',
    'gram:tense:set_future': lambda action: 'FUT',
    'direct:set_meaning': lambda action: None,  # ?
    'gram:case:set_instr': lambda action: 'INSTR',
    'mansi:pronoun:demonstrative': lambda action: 'PN.DEM',
    'mansi:numeral:partial_colloc': lambda action: None,  # ?
    'gram:set_mult': lambda action: 'MULT',
    'mansi:pronoun:set_sol': lambda action: 'SOL',
    'gram:case:set_nom': lambda action: 'NOM',
    'mansi:pronoun:personal:1PL': lambda action: '1PL',
    'mansi:make_transgressive': lambda action: 'PCTP',  # ?
    'mansi:russian_loan_word': lambda action: None,
    'mansi:translation:set_new': lambda action: None,
    'gram:noun_to_adj': lambda action: None,
    'gram:case:set_dat': lambda action: 'DAT',
    'gram:case:set_main': lambda action: 'NOM',
    'gram:set_inchoative': lambda action: 'INCH',
    'gram:set_semelfactive': lambda action: 'SMLF',
    'gram:case:set_voc': lambda action: 'VOC',
    'gram:mood:set_conjunctive': lambda action: 'SBJV',
    'gram:set_ord': lambda action: 'ORD',
    'gram:adj:comparative': lambda action: 'CMPR',
    'mansi:adj_to_noun': lambda action: None,
    'sem:make_opposite': lambda action: 'CAR',
    'gram:set_number:plur': lambda action: 'PL',
    'mansi:basic_pos:set_verb': lambda action: 'V',
    'gram:make_reflexive': lambda action: 'REFL',
    'mansi:object_number:set_plur': lambda action: 'PL.O',
    'mansi:tense:set_past': lambda action: 'PST',
    'gram:mood:set_imperative': lambda action: 'IMP',
    'mansi:verb_to_noun': lambda action: 'SBST',
    'gram:set_iterative': lambda action: 'ITER',
    'gram:case:set_lat': lambda action: 'LAT',
    'gram:adv:comparative': lambda action: 'CMPR',
    'gram:adj:superlative': lambda action: 'SUPL',
    'gram:tense:set_past': lambda action: 'PST',
    'mansi:pronoun:personal:1DU': lambda action: '1DU',
    'mansi:object_number:set_dual': lambda action: 'DU.O',
    'mansi:set_obj_conj': lambda action: 'O',
    'mansi:pronoun:personal:3SG': lambda action: '3SG',
    'gram:case:set_abl': lambda action: 'ABL',
    'mansi:verb:set_person': lambda action: str(action.get_arguments()[0]),
    'gram:set_durative': lambda action: 'DUR',
    'gram:mood:set_optative': lambda action: 'OPT',
    'mansi:make_participle': lambda action: 'PTCP',
    'gram:set_superlative': lambda action: 'SUPL',
    'gram:make_intransitive': lambda action: 'DETR',
    'mansi:pronoun:determinative': lambda action: 'PN.DET',
    'mansi:set_pred': lambda action: 'PRED',
    'sem:magnification_colloc': lambda action: None,  # ?
    'gram:case:set_loc': lambda action: 'LOC',
    'mansi:sem:coll': lambda action: 'COLL',
    'gram:number:set_sing': lambda action: 'SG',
    'mansi:conj:set_subj_pass': lambda action: 'PASS',  # ?
    'sem:adj_to_noun_corresp': lambda action: None,
    'gram:set_attr': lambda action: 'ATTR'
}
