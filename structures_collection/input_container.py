#!/usr/bin/python3


class CharOutline:
    def __init__(self, char_indices, attachment=None):
        self.simple_sequence = True
        self.index_groups = [list()]
        self.atcm = attachment
        for e, index in enumerate(char_indices):
            if type(index) != int:
                raise ValueError('Int expected, but {} found'.format(type(index)))
            if e > 0:
                if char_indices[e - 1] > char_indices[e]:
                    raise ValueError('Sorted list expected')
                if self.simple_sequence and char_indices[e] - char_indices[e - 1] > 1:
                    self.simple_sequence = False
                if char_indices[e] == char_indices[e - 1]:
                    raise ValueError('Char indices list should not contain duplicates')
                if char_indices[e] - char_indices[e - 1] > 1:
                    self.index_groups.append([char_indices[e]])
                else:
                    self.index_groups[-1].append(char_indices[e])
            else:
                self.index_groups[-1].append(char_indices[e])
        if not self.index_groups[0]:
            raise CharOutlineIsEmpty()

    def start(self):
        return self.index_groups[0][0]

    def end(self):
        return self.index_groups[-1][-1]

    def attachment(self, att_string):
        self.atcm = att_string

    def get_attachment(self):
        return self.atcm


class CharOutlineIsEmpty(Exception):
    pass
