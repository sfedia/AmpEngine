#!/usr/bin/python3

systems = {
    'universal:input': [
        'universal:token',
        'universal:collocation'
    ],
    'universal:collocation': [
        'universal:token'
    ],
    'universal:token': [
        'universal:morpheme',
        'mansi:morphemeYU',
        'mansi:VowMorpheme',
        'universal:char',
        'universal:char_regex'
    ],
    'universal:morpheme': [
        'universal:char',
        'universal:char_regex'
    ],
    'mansi:VowMorpheme': ['universal:morpheme'],
    'mansi:morphemeYU': ['universal:morpheme'],
    'universal:char': [],
    'universal:char_regex': ['universal:char']
}