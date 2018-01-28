#!/usr/bin/python3


class CharOutline:
    def __init__(self, char_indices, is_range=False, range_strict=False, attachment=None):
        self.index_groups = [list()]
        self.is_range = is_range
        self.__attachment = attachment
        self.error_se = 'CharOutline: .start()/end() is only avaliable for ranges'

        if self.is_range and len(char_indices) != 2:
            raise ValueError('CharOutline: indices range should contain two integers')
        elif self.is_range:
            for n in range(char_indices[0], char_indices[1] + int(range_strict)):
                self.index_groups[0].append(n)
        else:
            self.index_groups[0] = char_indices

        if not self.index_groups[0]:
            raise CharOutlineIsEmpty()

    def start(self):
        if not self.is_range:
            raise ValueError(self.error_se)
        return self.index_groups[0][0]

    def end(self):
        if not self.is_range:
            raise ValueError(self.error_se)
        return self.index_groups[-1][-1]

    def add_attachment(self, attachment_string):
        self.__attachment = attachment_string

    def get_attachment(self):
        return self.__attachment


class CharOutlineIsEmpty(Exception):
    pass
