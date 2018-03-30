#!/usr/bin/python3


class Clear:
    @staticmethod
    def remove_spec_chars(system_name, content):
        if system_name == 'universal:morpheme':
            if content.startswith('^'):
                return content[1:]
            return content
        return content
