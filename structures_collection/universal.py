#!/usr/bin/python3


class universal:
    # inherit for 2 subelements?
    def __init__(self, obj):
        self.object = obj

    def done(self):
        return self.object

    class mark:
        def plural(self, *args):
            universal.object.set_parameter('number', 'plural')
