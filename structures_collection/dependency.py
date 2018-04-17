#!/usr/bin/python3

systems = {
    'universal:input': [
        'universal:sentence'
    ],
    'universal:sentence': [
        'universal:token'
    ],
    'universal:token': [
        'universal:morpheme'
    ],
    'universal:morpheme': []
}


def check_transitivity(a_system, b_system):
    global systems
    if a_system not in systems:
        return False
    return b_system in systems[a_system]
