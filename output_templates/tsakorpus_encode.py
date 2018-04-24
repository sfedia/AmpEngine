#!/usr/bin/python3

import output_templates.lgr_action as lgr


class Encode:
    def __init__(self):
        self.tsakorpus_notation = {
            "1": "pers",
            "2": "pers",
            "3": "pers",
            "A": "pos",
            "POST": "pos",
            "PART": "pos",
            "INTRJ": "pos",
            "ADV": "pos",
            "ADJ": "pos",
            "ART": "pos",
            "CONJ": "pos",
            "CNJ": "pos",
            "N": "pos",
            "NUM": "pos",
            "PREP": "pos",
            "PRO": "pos",
            "V": "pos",
            "SBST": "pos",
            "rel_n": "nType",
            "topn": "nType",
            "famn": "nType",
            "persn": "nType",
            "patrn": "nType",
            "PN": "nType",
            "abl": "case",
            "nom": "case",
            "lat": "case",
            "ins": "case",
            "loc": "case",
            "acc": "case",
            "trans": "case",
            "prs": "tense",
            "pst": "tense",
            "evid": "mood",
            "ind": "mood",
            "fut": "tense",
            "pl": "number",
            "du": "number",
            "sg": "number",
            "ptcp": "v_form",
            "cvb": "v_form",
            "pres": "ptcp_form",
            "res": "ptcp_form",
            "neg": "ptcp_form",
            "simult": "cnv_form",
            "imp": "v_form",
            "inf": "v_form",
            "subj_pass": "v_conj",
            "iter": "v_deriv",
            "tr": "v_deriv",
            "detr": "v_deriv",
            "caus": "v_deriv",
            "smlf": "v_deriv",
            "attr": "attr",
            "dim": "n_deriv",
            "pej": "n_deriv",
            "1sg": "poss",
            "2sg": "poss",
            "3sg": "poss",
            "1du": "poss",
            "2du": "poss",
            "3du": "poss",
            "1pl": "poss",
            "2pl": "poss",
            "3pl": "poss",
            "comp": "comp",
            "ord": "num_deriv",
            "coll": "num_deriv",
            "distr": "num_deriv",
            "cond": "mood",
            "o": "object",
            "q": "quality",
            "rus": "add",
            "rus_sfx": "add",
            "missp": "add",
            "empty": "add",
            "unknown": "add"
        }

    def tsa_encode(self, action):
        lgr_abbr = lgr.lgr_values[action.get_path()](action)
        return self.multiple_lgr2tsa(lgr_abbr)

    def tsa_encode_value(self, action_path):
        lgr_abbr = lgr.lgr_values[action_path](None)
        return self.multiple_lgr2tsa(lgr_abbr)

    def check_lgr(self):
        for lgr_abbr in lgr.lgr_values:
            print(lgr_abbr, '=>', self.tsa_encode_value(lgr_abbr))

    def lgr2tsa(self, lgr_abbr):
        lgr_abbr = self.prepare_abbr(lgr_abbr)
        if lgr_abbr in self.tsakorpus_notation:
            return lgr_abbr, self.tsakorpus_notation[lgr_abbr]
        elif lgr_abbr.upper() in self.tsakorpus_notation:
            return lgr_abbr.upper(), self.tsakorpus_notation[lgr_abbr.upper()]
        elif lgr_abbr.lower() in self.tsakorpus_notation:
            return lgr_abbr.lower(), self.tsakorpus_notation[lgr_abbr.lower()]
        else:
            raise TsakorpusEquivalentNotFound(lgr_abbr)

    def multiple_lgr2tsa(self, lgr_abbr):
        lgr_abbr = self.prepare_abbr(lgr_abbr)
        return [self.lgr2tsa(x) for x in lgr_abbr.split(".")]

    @staticmethod
    def prepare_abbr(lgr_abbr):
        if lgr_abbr is None:
            lgr_abbr = "unknown"
        return lgr_abbr


class TsakorpusEquivalentNotFound(Exception):
    pass
