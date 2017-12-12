#!/usr/bin/python3
import structures_collection as collection
import random
import string


class InputContainer:
    def __init__(self, content, metadata=None):
        self.metadata = {}
        if metadata is not None:
            self.metadata = metadata
        self.elements = []
        self.INPUT = 'universal:input'
        self.add_element(InputContainerElement(self.INPUT, content))
        self.segment_into_childs(self.INPUT)

    def segment_into_childs(self, system_name):
        if system_name not in collection.dependency.systems:
            return
        for child_system in collection.dependency.systems[system_name]:
            for element in self.get_by_system_name(system_name):
                try:
                    self.segment_element(
                        element,
                        child_system,
                        collection.auto_segmentation.Handler.segment(system_name, child_system)(element.get_content())
                    )
                except collection.auto_segmentation.NoSuchSegmentTemplate:
                    pass
            self.segment_into_childs(child_system)

    def get_by_ic_id(self, ic_id):
        returned = []
        for element in self.elements:
            if element.get_ic_id() == ic_id:
                returned.append(element)

        return returned

    def get_by_system_name(self, system_name):
        returned = []
        for element in self.elements:
            if element.get_system_name() == system_name:
                returned.append(element)

        return returned

    def segment_element(self, element, child_system, child_list):
        parent_ic = element.get_ic_id()
        for child in child_list:
            self.add_element(InputContainerElement(child_system, child, parent=parent_ic))

    def add_element(self, element):
        self.elements.append(element)


class InputContainerElement:
    def __init__(self, system_name, content, params={}, parent=None):
        self.system_name = system_name
        self.content = content
        self.params = params
        for param, func in collection.auto_parameter_extraction.Handler.get_param_extractors(self.system_name):
            self.params[param] = func(content)
        self.ic_id = ''.join(random.choice('abcdef' + string.digits) for _ in range(20))
        self.parent_ic_id = parent

    def set_parameter(self, param_name, param_value):
        self.params[param_name] = param_value

    def get_parameter(self, param_name):
        return self.params[param_name]

    def get_ic_id(self):
        return self.ic_id

    def get_system_name(self):
        return self.system_name

    def get_content(self):
        return self.content


input = InputContainer('the quick brown fox jumps over the lazy dog')

print(input.get_by_system_name('universal:input'))
print(input.get_by_system_name('universal:token'))