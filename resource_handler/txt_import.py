#!/usr/bin/python3


class HandlerStart:
    def __init__(self):
        self.links = {}
        self.params_provided = {}

    def get_link(self, link_name):
        if link_name in self.links:
            return self.links[link_name]
        else:
            raise LinkNotFound()

    def add_link(self, link_name, value):
        self.links[link_name] = value


# every function should return List


Handler = HandlerStart()


def new_link(link_name):

    def link_decorator(link):
        Handler.add_link(link_name, link)

        def wrapped(function_arg1):
            return link(function_arg1)

        return wrapped

    return link_decorator


class LinkNotFound(Exception):
    pass
