#!/usr/bin/python3


class Handler:
    def __init__(self):
        pass

    def segment(self, from_, to_):
        return True


# every function should return List

@segmentation('universal:input', 'universal:token')
def input_to_tokens(content, metadata=None):
    return content.split()