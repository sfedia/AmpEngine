#!/usr/bin/python3

marked_classes = {}


def mark_as(identifiers):
    def wrapper(cl):
        def wrapped(*args):
            marked_classes[tuple(identifiers)] = cl
        return wrapped
    return wrapper


@mark_as(['*'])
class main:
    pass
    # ...
