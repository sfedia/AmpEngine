#!/usr/bin/python3
import re
import inspect
import structures_collection as collection
import resource_handler as resources
import convertation_handler as converter
import log_handler as logs
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
            raise UndefinedSystem()
        for child_system in collection.dependency.systems[system_name]:
            try:
                for element in self.get_by_system_name(system_name):
                    self.segment_element(
                        element,
                        child_system,
                        collection.auto_segmentation.Handler().segment(system_name, child_system)
                    )
                self.segment_into_childs(child_system)
            except collection.auto_segmentation.NoSuchSegmentTemplate:
                continue

    def remove_childs_of(self, parent_id):
        for element in self.elements:
            if element.get_parent_ic_id() == parent_id:
                self.elements.remove(element)

    def get_by_ic_id(self, ic_id):
        returned = []
        for element in self.elements:
            if element.get_ic_id() == ic_id:
                returned.append(element)

        return returned

    def get_by_system_name(self, system_name):
        returned = []
        for element in self.elements:
            if element.get_ic_id() == system_name:
                returned.append(element)

        return returned

    def segment_element(self, element, child_system, child_list):
        parent_ic = element.get_ic_id()
        ices = []
        for child in child_list:
            ice = InputContainerElement(child_system, child, parent=parent_ic)
            ices.append(ice.get_ic_id())
            self.add_element(ice)
        return ices

    def add_element(self, element):
        self.elements.append(element)

    def get_all(self):
        return self.elements

    def make_apply(self, main_container_element_id, main_container, scanned_system):
        main_container_element = main_container.get_by_id(main_container_element_id)
        link_sentence = main_container_element.apply_for[0]
        actions = main_container_element.apply_for[1]
        rows = self.get_by_system_name(scanned_system)
        for row in rows:
            if LinkSentence(link_sentence, main_container, self, scanned_system).check(row):
                # get ic_id
                if not collection.auto_segmentation.Handler.can_segment(scanned_system, main_container_element.get_type()):
                    extracted_ic_id = collection.layer_extraction.Handler.extract(
                        scanned_system, main_container_element.get_type()
                    )(row, main_container_element.get_content())
                else:
                    # ???
                    # a request to logger can be done
                    for x in self.get_by_system_name(scanned_system):
                        if x.get_content() == main_container_element.get_content():
                            extracted_ic_id = x.get_ic_id()
                            break
                for action in actions:
                    args = action.get_arguments()
                    if args:
                        collection.static.Handler.get_func(action.get_path())(extracted_ic_id, args)
                    else:
                        collection.static.Handler.get_func(action.get_path())(extracted_ic_id)


class InputContainerElement:
    def __init__(self, system_name, content, params=dict(), parent=None):
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

    def get_parent_ic_id(self):
        return self.parent_ic_id

    def get_system_name(self):
        return self.system_name

    def get_content(self):
        return self.content


class Container:
    def __init__(self):
        self.rows = []
        self.entities = []


    def add_entity(self, entity_object):
        if entity_object not in self.entities:
            self.entities.append(entity_object)

    def get_all(self):
        return self.rows

    def get_by_id(self, element_id):
        for row in self.rows:
            if row.id == element_id:
                return row
        return False

    def get_by_class_name(self, class_name):
        elements = []
        for row in self.rows:
            if class_name in row.get_class_names():
                elements.append(row)

        return elements

    def get_by_type(self, element_type):
        elements = []
        for row in self.rows:
            if element_type == row.get_type():
                elements.append(row)

        return elements

    def get_elems_providing_param(self, param, element, input_container, scanned_system):
        aprp = []
        for row in self.rows:
            if not row.apply_for:
                continue
            af_link = row.apply_for[0]
            af_funcs = row.apply_for[1]
            if not af_funcs:
                continue
            for func in af_funcs:
                check_results = LinkSentence(af_link, self, input_container, scanned_system).check(element)
                if param in collection.static.Handler.get_func_params(func) and check_results:
                    aprp.append(row.get_id())
        return aprp

    def add_element(self, element_type, element_content, element_id):
        if self.get_by_id(element_id):
            raise IdIsNotUnique()
        element = ContainerElement(element_type, element_content, element_id, self)
        self.rows.append(element)
        return self.get_by_id(element_id)


class ContainerEntity:
    def __init__(self, level, identifier):
        self.level = level
        self.identifier = identifier

    def get_level(self):
        return self.level

    def get_identifier(self):
        return self.identifier


class ContainerElement:
    def __init__(self, element_type, element_content, element_id, container):
        self.type = element_type
        self.content = element_content
        self.container = container
        self.id = element_id
        self.class_names = []
        self.apply_for = []
        self.applied_ids = []
        self.parameters = {}

    def applied(self, link_sentence, actions):
        self.apply_for = [link_sentence, actions]
        return self

    def add_applied(self, applied_id):
        self.applied_ids.append(applied_id)
        return self

    def add_class(self, class_name):
        if class_name not in self.class_names:
            self.class_names.append(class_name)
            self.container.add_entity(ContainerEntity('class', class_name))
            return self

    def edit_parameter(self, key, value=True):
        self.parameters[key] = value
        return self

    def set_parameter(self, key, value=True):
        if key not in self.parameters:
            self.edit_parameter(key, value)
        else:
            raise ParameterExistsAlready()
        return self

    def get_parameter(self, key):
        if key in self.parameters:
            return self.parameters[key]
        raise NoSuchParameter()

    def get_id(self):
        return self.id

    def get_class_names(self):
        return self.class_names

    def get_type(self):
        return self.type

    def get_content(self):
        return self.content
    
    def set_child_type(self, child_type):
        if ':' in child_type:
            raise WrongChildType()
        self.type += ':' + child_type


class LinkSentence:
    def __init__(self, link_string, container, input_container, scanned_system, from_list=(), allow_resources=True):
        self.link = link_string
        self.container = container
        self.input_container = input_container
        if not from_list:
            self.checked_list = self.input_container.get_by_system_name(scanned_system)
        else:
            self.checked_list = from_list
        self.allow_resources = allow_resources
        self.scanned_system = scanned_system

    def check_element(self, element, param_pair, block_converter=False):
        if param_pair.sharp:
            return collection.sharp_function.Handler.get_sharp(self.scanned_system, element.get_type())(
                element,
                self.container,
                self.input_container
            )
        try:
            if not param_pair.is_bool_check():
                is_good = param_pair.compare(element.get_parameter(param_pair.key))
            else:
                is_good = True if element.get_parameter(param_pair.key) else False
        except NoSuchParameter:
            #good_afs = collection.static.Handler.params_affected(param_pair.key)
            #good_afs = self.container.get_actions_declaring(param_pair.key, element)
            good_aprp = self.container.get_elems_providing_param(
                param_pair.key,
                element,
                self.input_container,
                self.scanned_system
            )
            if good_aprp:
                self.container.make_apply(good_aprp[0], self.container, self.scanned_system)
                if not param_pair.is_bool_check():
                    is_good = param_pair.compare(element.get_parameter(param_pair.key))
                else:
                    is_good = True if element.get_parameter(param_pair.key) else False
            elif self.allow_resources:
                parameter = resources.request_functions.Handler.get_parameter(param_pair.key, element)
                if parameter:
                    if not param_pair.is_bool_check():
                        is_good = param_pair.compare(element.get_parameter(param_pair.key))
                    else:
                        is_good = True if element.get_parameter(param_pair.key) else False
                elif not block_converter:
                    # is not ready yet
                    conv_variants = []
                    try:
                        conv_variants = converter.convert_param_pair(param_pair.key, param_pair.value)
                    except converter.CannotConvertSystemTypes:
                        pass
                    if not conv_variants:
                        raise CannotGetParameter()
                    else:
                        for variant in conv_variants:
                            try:
                                return self.check_element(element, variant, block_converter=True)
                            except CannotGetParameter:
                                pass
                        raise CannotGetParameter()
                else:
                    raise CannotGetParameter()
            else:
                raise CannotGetParameter()

        return is_good

    class ParameterPair:
        def __init__(self, key, value='', sharp=False, operator="=", bool_check=False):
            self.key = key
            self.bool_check = bool_check
            if value == '':
                self.bool_check = True
            self.value = value
            self.prop = 'ParameterPair'
            self.operator = operator
            if sharp:
                self.prop = 'Sharp'

        def compare(self, value):
            self.operator = self.operator.replace('*', '')
            if self.operator == "=":
                return self.value == value
            elif self.operator == "!=":
                return self.value != value
            elif self.operator == "<":
                return int(self.value) < int(value)
            elif self.operator == "<=":
                return int(self.value) <= int(value)
            elif self.operator == ">":
                return int(self.value) > int(value)
            elif self.operator == ">=":
                return int(self.value) >= int(value)
            else:
                raise WrongLinkSentence()

        def is_bool_check(self):
            return self.bool_check

    def parse_sector(self, sector, element):
        sector = sector.strip()
        sector_rx = r'([\w:]+)(\*?([<>!=\?]+))\(([^\)]*)\)(\{[^\}]+\})?|\s*([&\|])\s*|(\[\s*(.*?)\s*\])'
        parsed_list = []
        RE_SHARP = r"^#\s*"
        if re.search(RE_SHARP, sector):
            parsed_list.append(self.ParameterPair('#', sharp=True))
            sector = re.sub(RE_SHARP, '', sector)

        parsed_sector = re.finditer(sector_rx, sector)
        for seq in parsed_sector:
            # AND/OR operators
            if re.search(r'[&\|]', seq.group(0)):
                parsed_list.append(seq.group(1))
            # bracket group
            elif re.search(r'^\[.*\]$', seq.group(0)):
                parsed_list.append(self.parse_sector(seq.group(1), element))
            # parameter checking
            elif re.search(r'[<>!=\?]\s*\(', seq.group(0)):
                par_name = seq.group(1)
                operator = seq.group(2)
                value = seq.group(4)
                if '*' not in operator:
                    parameter_pair = self.ParameterPair(par_name, value, operator=operator)
                else:
                    parameter_pair = self.ParameterPair(par_name, element.get_parameter(value), operator=operator)
                parsed_list.append(parameter_pair)
            else:
                raise WrongLinkSentence()

        parsed_sector = re.findall(sector_rx, sector)
        return parsed_list

    def is_good(self, link_slice, element):
        len_link_slice = len(link_slice)
        complete_list = []

        for i in range(len_link_slice):
            if link_slice[i] in ('&', '|'):
                complete_list.append(link_slice[i])
            elif type(link_slice[i]) == list:
                complete_list.append(self.check_element(element, link_slice[i]))
            else:
                complete_list.append(self.is_good(link_slice[i], element))

        if '&' in complete_list and '|' in complete_list:
            raise WrongLinkSentence()

        common_operator = '&' if '&' in complete_list else '|' if '|' in complete_list else False

        if not common_operator and (not link_slice or len(link_slice) > 1):
            raise WrongLinkSentence()

        if not common_operator:
            return link_slice[0]
        elif common_operator == '&':
            return False not in link_slice
        elif common_operator == '|':
            return True in link_slice
        else:
            raise WrongLinkSentence()

    def check(self, element):
        parsed_list = self.parse_sector(self.link, element)
        return self.is_good(parsed_list, element)


class Action:
    def __init__(self, path, arguments=False):
        self.path = path
        self.arguments = arguments if arguments else []

    def get_path(self):
        return self.path

    def get_arguments(self):
        return self.arguments

    def get_args(self):
        return self.get_arguments()


class IdIsNotUnique(Exception):
    pass


class ParameterExistsAlready(Exception):
    pass


class NoSuchParameter(Exception):
    pass


class WrongCollectionPath(Exception):
    pass


class NoSuchSystem(Exception):
    pass


class NoSuchSubsystem(Exception):
    pass


class WrongFunctionUse(Exception):
    pass


class CannotGetParameter(Exception):
    pass


class WrongLinkSentence(Exception):
    pass


class TypeIsNotStatic(Exception):
    pass


class WrongChildType(Exception):
    pass


class UndefinedSystem(Exception):
    pass
