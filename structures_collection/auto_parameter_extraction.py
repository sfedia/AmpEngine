#!/usr/bin/python3


class Handler:
    def __init__(self):
        pass

    def get_param_lambdas(self, system_name):
        # return Arr [param_name, Func for system_name Providing param_name
        pass


@extract_parameter('universal:token', 'universal:length')
def length_of_token(content):
    return len(content)