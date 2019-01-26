#!/usr/bin/python3

from collections import Counter, namedtuple
import datrie
import json
import os
import re


class WordEntry:
    def __init__(self, lemma):
        self.lemma = lemma
        self.full_lemma = lemma
        self.reduce_lemma()
        self.pos_options = []
        self.rus_meanings = []
        self.common_pos = None

    def reduce_lemma(self):
        self.lemma = re.sub(r'[ёуеыаоэяию]ӈкве$', '', self.lemma)

    def dynamic_lemma(self, wf):
        if wf.endswith("ь"):
            return self.full_lemma
        return self.lemma

    def get_pos(self, update=False):
        if self.pos_options:
            return Counter(self.pos_options).most_common(1)[0][0]
        else:
            return "unknown"

    def get_translation(self):
        if self.rus_meanings:
            return " ".join(self.rus_meanings[0])
        else:
            return ""


class LuimaSeriposToStandard:
    def __init__(self, luima_string):
        self.luima_string = luima_string
        # -> lower
        self.luima_string = self.luima_string.lower()
        self.standard_string = luima_string
        self.difference = None
        self.luima2standard = {
            "а̄": "а",
            "э̄": "э",
            "ӯ": "у",
            "о̄": "о",
            "я̄": "я",
            "ы̄": "ы",
            "е̄": "е",
            "ӣ": "и",
            "ё̄": "ё",
            "с": "с",
            "ю̄": "ю"
        }
        for (luima, standard) in self.luima2standard.items():
            self.standard_string = self.standard_string.replace(luima, standard)
        self.difference = len(self.luima_string) - len(self.standard_string)

    def luima_cut_index(self, index):
        return index + self.difference


dirname = os.path.dirname(__file__)
stem_base = datrie.Trie.load(os.path.join(dirname, 'dict_entries.trie'))
stem_result = namedtuple("StemResult", ["entry", "index"])


def legal_length(pref, s):
    if len(pref) == 1:
        return False
    return True


def get_stem_for(luima_string):
    s = LuimaSeriposToStandard(luima_string)
    return [
        stem_result(entry, s.luima_cut_index(len(pref)))
        for (pref, entry) in stem_base.prefix_items(s.standard_string)[::-1] if legal_length(pref, s)
    ]


#print(get_stem_for("потыртас")[1].entry.get_pos())