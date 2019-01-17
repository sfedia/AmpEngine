#!/usr/bin/python3
from collections import Counter
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
