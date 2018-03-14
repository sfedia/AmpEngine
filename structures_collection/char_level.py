#!/usr/bin/python3


class CharOutline:
    def __init__(self, ci_groups, attachment=None, metadata=None):
        self.__groups = ci_groups
        self.__attachment = attachment
        self.__metadata = metadata

    def add_attachment(self, attachment, override=False):
        if not self.__attachment:
            self.__attachment = attachment
        elif not override:
            raise AttachmentAlreadySet()

    def add_group(self, group):
        self.__groups.append(group)

    def shift_group(self, group_index, shift_int, start_int, rev=False):
        self.__groups[group_index].shift_indices(shift_int, start_int, rev)

    def get_groups(self):
        return self.__groups

    def get_metadata(self):
        return self.__metadata

    def get_attachment(self):
        return self.__attachment


class CharIndexGroup:
    def __init__(self, indices, is_range=False, range_strict=False, is_virtual=False):
        self.is_virtual = is_virtual
        if is_range and is_virtual:
            raise MalformedCharOutline('index group cannot be both range and virtual group')
        self.indices = []
        self.unallocated = False
        if is_range and len(self.indices) != 2:
            raise MalformedCharOutline('range list should include two integers')
        elif is_range:
            self.indices += list(range(indices[0], indices[1] + int(range_strict)))
        elif is_virtual:
            if indices != UNALLOCATED and not 0 < len(indices) <= 2:
                raise MalformedCharOutline('virtual margin can be unallocated or a list of 1 or 2 integers')
            elif indices != UNALLOCATED:
                self.indices = indices
            else:
                # so margin is UNALLOCATED
                self.unallocated = True
        else:
            self.indices = indices

    def get_indices(self):
        return self.indices if not self.unallocated else UNALLOCATED

    def shift_indices(self, shift_int, start_int, rev=False):
        for j, n in enumerate(self.indices):
            if (not rev and n >= start_int) or (rev and n <= start_int):
                self.indices[j] += shift_int


UNALLOCATED = -1.5


class CharOutlineIsEmpty(Exception):
    pass


class MalformedCharOutline(Exception):
    pass


class AttachmentAlreadySet(Exception):
    pass
