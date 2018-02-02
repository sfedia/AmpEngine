#!/usr/bin/python3
import re
import inspect
import structures_collection as collection
import resource_handler as resources
import convertation_handler as converter
import log_handler as logs
import itertools
import random
import string


class InputContainer:
    def __init__(self, content, metadata=None):
        self.metadata = {}
        if metadata:
            self.metadata = metadata
        self.elements = []
        self.INPUT = 'universal:input'
        self.ic_log = logs.log_object.New()
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
            except collection.auto_segmentation.SegmentTemplateNotFound:
                continue

    def remove_childs_of(self, parent_id):
        for element in self.elements:
            if element.get_parent_ic_id() == parent_id:
                self.elements.remove(element)

    def get_by_ic_id(self, ic_id):
        for element in self.elements:
            if element.get_ic_id() == ic_id:
                return element
        return None

    def get_by_system_name(self, system_name):
        returned = []
        for element in self.elements:
            if element.get_ic_id() == system_name:
                returned.append(element)

        return returned

    def segment_element(self, element, child_system, c_outlines):
        parent_ic = element.get_ic_id()
        ices = []
        for outline_object in c_outlines:
            ice = InputContainerElement(
                child_system, outline_object.get_attachment(), char_outline=outline_object, parent=parent_ic
            )
            ices.append(ice.get_ic_id())
            self.add_element(ice)
        return ices

    def add_element(self, element):
        self.elements.append(element)

    def get_all(self):
        return self.elements

    def backward_parse(self, input_container_element, scanned_system):
        pass

    def make_apply(self, main_container_element_id, main_container, scanned_system):
        main_container_element = main_container.get_by_id(main_container_element_id)
        get_applied = main_container_element.get_applied()
        link_sentences = get_applied['links']
        actions = get_applied['actions']
        rows = self.get_by_system_name(scanned_system)
        for row in rows:
            for link_sentence in link_sentences:
                if link_sentence.check(row):
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
                            collection.static.Handler.get_func(action.get_path())(
                                extracted_ic_id, args, action.branching_allowed()
                            )
                        else:
                            collection.static.Handler.get_func(action.get_path())(
                                extracted_ic_id,
                                branching=action.branching_allowed()
                            )
                    break


class InputContainerElement:
    def __init__(self, system_name, content, input_container, char_outline=None, params=dict(), parent=None, group=None, fork_id=None):
        self.system_name = system_name
        self.content = content
        self.params = params
        self.char_outline = char_outline
        for param, func in collection.auto_parameter_extraction.Handler.get_param_extractors(self.system_name):
            self.params[param] = func(content)
        self.ic_id = ''.join(random.choice('abcdef' + string.digits) for _ in range(20))
        self.parent_ic_id = parent
        self.group = group
        self.fork_id = fork_id
        if fork_id and not input_container.get_by_ic_id(fork_id):
            raise UnknownForkID()

    def set_parameter(self, param_name, param_value):
        self.params[param_name] = param_value

    def get_parameter(self, param_name):
        if param_name not in self.params:
            raise ParameterNotFound()
        return self.params[param_name]

    def get_ic_id(self):
        return self.ic_id

    def get_parent_ic_id(self):
        return self.parent_ic_id

    def get_system_name(self):
        return self.system_name

    def get_content(self):
        return self.content

    def get_char_outline(self):
        return self.char_outline

    def get_group(self):
        """
        :return: (Int; >0 because None should not confuse group number) number of group the element belongs to
        """
        return self.group

    def get_fork_id(self):
        return self.fork_id


class Container:
    def __init__(self):
        self.rows = []
        self.entities = []
        self.cont_log = logs.log_object.New()
        for system in collection.dependency.systems:
            self.add_entity(ContainerEntity('system', system, self))

    def add_entity(self, entity_object):
        if entity_object not in self.entities:
            self.entities.append(entity_object)

    def get_class(self, identifier):
        for entity in self.entities:
            if entity.get_level() == 'class' and entity.get_identifier == identifier:
                return entity
        raise ClassEntityNotFound()

    def get_system(self, identifier):
        for entity in self.entities:
            if entity.get_level() == 'system' and entity.get_identifier == identifier:
                return entity
        raise SystemEntityNotFound()

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

    def foreach_in_class(self, class_name):
        def fic_decor(class_func):
            for row in self.rows:
                if class_name in row.get_class_names():
                    class_func(row)

            def wrapped(fa1, fa2):
                return class_func(fa1, fa2)

            return wrapped

        return fic_decor

    def get_by_type(self, element_type):
        elements = []
        for row in self.rows:
            if element_type == row.get_type():
                elements.append(row)

        return elements

    def iter_content_filter(self, filter_func, sort_by_length=False, sort_desc=False, system_filter=None):
        elements = []
        content_table = dict()
        i = 0

        for row in self.rows:
            if filter_func(row.get_content()) and (row.get_type() == system_filter if system_filter else True):
                elements.append(row)
                if sort_by_length:
                    if row.get_content() not in content_table:
                        content_table[row.get_content()] = []
                    content_table[row.get_content()].append(i)
                i += 1

        if sort_by_length:
            sorted_elements = []
            content_list = list(content_table.keys())
            content_list.sort(key=len, reverse=sort_desc)
            for s in content_list:
                for element_index in content_table[s]:
                    sorted_elements.append(elements[element_index])
            return sorted_elements
        return elements

    def get_elems_providing_param(self, param, input_container_element, scanned_system):
        aprp = []
        for row in self.rows:
            get_applied = row.get_applied()
            if not get_applied['links']:
                continue
            link_sentences = get_applied['links']
            actions = get_applied['actions']
            if not actions:
                continue
            for action in actions:
                for link_sentence in link_sentences:
                    check_results = link_sentence.check(input_container_element)
                    if param in collection.static.Handler.get_func_params(action) and check_results:
                        aprp.append(row.get_id())
                        break
        return aprp

    def add_element(self, element_type, element_content, element_id):
        if self.get_by_id(element_id):
            raise IdIsNotUnique()
        element = ContainerElement(element_type, element_content, element_id, self)
        self.rows.append(element)
        return self.get_by_id(element_id)

    def intrusion(self, link_sentence, whitelist=None):
        if whitelist is None:
            raise IntrusionIsEmpty()
        supported_types = ['classes']
        for type_ in whitelist:
            if whitelist not in supported_types:
                raise IntrusionUnsupportedType()
            if type_ == 'classes':
                self.get_class(whitelist[type_]).subelems_intrusion(link_sentence)


class ContainerEntity:
    def __init__(self, level, identifier, container):
        self.level = level
        self.identifier = identifier
        self.subcl_orders = []
        self.added_bhvr = 'standard'
        self.subelems_intrusion = []
        self.container = container

    def get_level(self):
        return self.level

    def get_identifier(self):
        return self.identifier

    def added_behaviour(self, pattern):
        if self.level != 'class':
            raise AddedBehaviourNotSupported()
        self.added_bhvr = pattern

    def subclasses_order(self, order_string, parent_filter=None, select_into=None, strict=False):
        if self.level != 'system':
            raise SubclassesOrderNotSupported()
        self.subcl_orders.append({
            'order': order_string,
            'parent_filter': parent_filter,
            'select_into': select_into,
            'strict': strict
        })

    def subelements_intrusion(self, link_sentence):
        self.subelems_intrusion.append(link_sentence)

    def get_subcl_orders(self):
        return self.subcl_orders

    def get_subclasses_affecting_ids(self, id_names):
        found_orders = []
        for id_name in id_names:
            for order in self.subcl_orders:
                affected_ids = order.get_affected_ids()
                if id_name in affected_ids:
                    found_orders.append(order)
                else:
                    affected_classes = order.get_affected_classes()
                    for id_class in self.container.get_by_id(id_name).get_class_names():
                        if id_class in affected_classes:
                            found_orders.append(order)
                            break
        return found_orders

    def inspect_added_behaviour(self):
        return self.added_bhvr

    def get_subelems_intrusion(self):
        return self.subelems_intrusion


class SubclassesOrder:
    def __init__(self, order_string, main_container, all_nulls, parent_filter=None, select_into=None, strict=True):
        self.scheme = []
        self.strict = strict
        self.main_container = main_container
        self.parent_filter = parent_filter
        self.nulls = all_nulls
        self.select_into = select_into
        sp_string = order_string.split()
        for substr in sp_string:
            if substr == '?':
                self.scheme.append({
                    'type': 'pointer',
                    'subtype': 'everything'
                })
            elif substr.startswith('.'):
                self.scheme.append({
                    'type': 'pointer',
                    'subtype': 'class',
                    'value': substr[1:]
                })
            elif substr.startswith('#'):
                self.scheme.append({
                    'type': 'pointer',
                    'subtype': 'id',
                    'value': substr[1:]
                })
            elif '<' in substr or '>' in substr:
                lookbehind = ''.join([x for x in substr if x == '<'])
                lookahead = ''.join([x for x in substr if x == '>'])
                if lookbehind:
                    self.scheme.append({
                        'type': 'operator',
                        'subtype': 'lookbehind',
                        'value': 'optional' if len(lookbehind) == 2 else 'required'
                    })
                if lookahead:
                    self.scheme.append({
                        'type': 'operator',
                        'subtype': 'lookahead',
                        'value': 'optional' if len(lookahead) == 2 else 'required'
                    })
            else:
                raise MalformedSubOrder()

    def get_affected_classes(self):
        return [x['value'] for x in self.scheme if x['subtype'] == 'class']

    def get_affected_ids(self):
        return [x['value'] for x in self.scheme if x['subtype'] == 'id']

    def check_sequence(self, sequence, available_nulls):
        """
        :param sequence: List[MC element id]
        :return: Bool -> if the order matches the given sequence
        """
        # self.null_elements

        def get_operator(n):
            if n > 0:
                if self.scheme[n - 1]['type'] == 'operator' and self.scheme[n - 1]['subtype'] == 'lookahead':
                    return self.scheme[n - 1]['value']
            elif n < len(self.scheme) - 1:
                if self.scheme[n + 1]['type'] == 'operator' and self.scheme[n + 1]['subtype'] == 'lookbehind':
                    return self.scheme[n + 1]['value']

        ev_groups = []
        non_ev = []
        check_regex = ''
        for j, el in self.scheme:
            if el['type'] == 'pointer' and el['subtype'] == 'everything':
                if get_operator(j) == 'required':
                    check_regex += '((.+))'
                else:
                    check_regex += '((.*)|)'
                ev_groups.append(j)
            elif el['type'] == 'pointer':
                pointer_regex = '(' + '('
                el_name = r'\*' + (r'\.' if el['subtype'] == 'class' else '#') + el['value'] + r'\*'
                non_ev.append(el_name)
                pointer_regex += el_name
                pointer_regex += ')'
                if get_operator(j) == 'optional':
                    pointer_regex += '|'
                pointer_regex += ')'
                check_regex += pointer_regex
            else:
                continue
        non_ev_str = '|'.join(non_ev)
        el_masks = [
            [*['.' + x for x in self.main_container.get_by_id(el_id).get_class_names()], '#' + el_id]
            for el_id in sequence
        ]
        for mask_product in [''.join(['*' + y + '*' for y in x]) for x in itertools.product(el_masks)]:
            rx_grouping = re.compile(check_regex).match(mask_product)
            if not rx_grouping:
                continue
            if re.search(non_ev_str, rx_grouping.groups()[0]) or re.search(non_ev_str, rx_grouping.groups()[-1]):
                continue
            return True

        return False


class ContainerElement:
    def __init__(self, element_type, element_content, element_id, container):
        self.type = element_type
        self.content = element_content
        self.container = container
        self.id = element_id
        self.class_names = []
        self.apply_for = []
        self.applied_ids = []
        self.mutation_links = []
        self.parameters = {}

    def applied(self, link_sentence, actions):
        self.apply_for = [link_sentence, actions]
        self.apply_for[0].add_inherit_element(self)
        return self

    def add_applied(self, applied_id):
        self.applied_ids.append(applied_id)
        return self

    def add_class(self, class_name):
        if class_name not in self.class_names:
            self.class_names.append(class_name)
            self.container.add_entity(ContainerEntity('class', class_name, self.container))
            return self
        raise RepeatedClassAssignment()

    def edit_parameter(self, key, value=True):
        self.parameters[key] = value
        return self

    def set_parameter(self, key, value=True):
        if key not in self.parameters:
            self.edit_parameter(key, value)
        else:
            raise ParameterAlreadyExists()
        return self

    def get_parameter(self, key, args=[]):
        try:
            extractor = collection.auto_parameter_extraction.Handler.get_param_extractors(self.type, key)
            self.parameters[key] = extractor(self.content, args)
        except collection.auto_parameter_extraction.ExtractorNotFound:
            pass
        if key in self.parameters:
            return self.parameters[key]
        else:
            raise ParameterNotFound()

    def get_id(self):
        return self.id

    def get_class_names(self):
        return self.class_names

    def get_type(self):
        return self.type

    def get_content(self):
        return self.content

    def append_child_type(self, child_type):
        if ':' in child_type:
            raise WrongChildType()
        self.type += ':' + child_type

    def provide_mutation_links(self, links):
        self.mutation_links += links

    def get_mutation_links(self):
        return self.mutation_links

    def get_applied(self):
        applied_object = {
            'links': self.apply_for[0],
            'actions': self.apply_for[1]
        }
        for class_name in self.class_names:
            for link_sentence in self.container.get_class(class_name).get_subelems_intrusion():
                applied_object['links'].append(link_sentence)
        return applied_object


class LinkSentence:
    def __init__(self, link_string, container, input_container, scanned_system, from_list=(), allow_resources=True):
        self.link = link_string
        self.container = container
        self.input_container = input_container
        self.inherit_element = None
        if not from_list:
            self.checked_list = self.input_container.get_by_system_name(scanned_system)
        else:
            self.checked_list = from_list
        self.allow_resources = allow_resources
        self.scanned_system = scanned_system

    def add_inherit_element(self, container_element):
        if self.inherit_element:
            raise InheritElementAlreadyExists()
        self.inherit_element = container_element

    def check_element(self, element, param_pair, block_converter=False):
        if param_pair.sharp:
            return collection.sharp_function.Handler.get_sharp(self.scanned_system, element.get_type())(
                element,
                self.inherit_element,
                self.container,
                self.input_container
            )
        try:
            if not param_pair.is_bool_check():
                is_good = param_pair.compare(element.get_parameter(param_pair.key, param_pair.arguments))
            else:
                is_good = True if element.get_parameter(param_pair.key, param_pair.arguments) else False
        except ParameterNotFound:
            good_aprp = self.container.get_elems_providing_param(
                param_pair.key,
                element,
                self.scanned_system
            )
            if good_aprp:
                self.container.make_apply(good_aprp[0], self.container, self.scanned_system)
                if not param_pair.is_bool_check():
                    is_good = param_pair.compare(element.get_parameter(param_pair.key, param_pair.arguments))
                else:
                    is_good = True if element.get_parameter(param_pair.key, param_pair.arguments) else False
            elif self.allow_resources:
                parameter = resources.request_functions.Handler.get_parameter(param_pair.key, element)
                if parameter:
                    if not param_pair.is_bool_check():
                        is_good = param_pair.compare(element.get_parameter(param_pair.key, param_pair.arguments))
                    else:
                        is_good = True if element.get_parameter(param_pair.key, param_pair.arguments) else False
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
        def __init__(self, key, value='', sharp=False, operator="=", bool_check=False, arguments=[]):
            self.key = key
            self.bool_check = bool_check
            if value == '':
                self.bool_check = True
            self.value = value
            self.prop = 'ParameterPair'
            self.operator = operator
            self.arguments = arguments
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

    @staticmethod
    def parse_args(arg_string):
        argument_rx = r'([\w:]+)=\(([^\)]*)\)'
        arguments_struct = []
        for arg in re.finditer(argument_rx, arg_string):
            arguments_struct.append({
                'name': arg.group(1),
                'value': arg.group(2)
            })
        return arguments_struct

    def parse_sector(self, sector, element):
        sector = sector.strip()
        sector_rx = r'([\w:]+)(\*?([<>!=\?]+))\(([^\)]*)\)(\{[^\}]+\})?|\s*([&\|])\s*|(\[\s*(.*?)\s*\])'
        parsed_list = []
        if re.search(r'^#\s*', sector):
            parsed_list.append(self.ParameterPair('#', sharp=True))
            sector = re.sub(r'^#\s*', '', sector)

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
                arguments = self.parse_args(seq.group(5)) if seq.group(5) else []
                if '*' not in operator:
                    parameter_pair = self.ParameterPair(par_name, value, operator=operator, arguments=arguments)
                else:
                    parameter_pair = self.ParameterPair(
                        par_name, element.get_parameter(value), operator=operator, arguments=arguments
                    )
                parsed_list.append(parameter_pair)
            else:
                raise WrongLinkSentence()

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

        common_operator = '&' if '&' in complete_list else '|' if '|' in complete_list else None

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
    def __init__(self, path, arguments=False, branching=False):
        self.path = path
        self.arguments = arguments if arguments else []
        self.branching = branching

    def get_path(self):
        return self.path

    def get_arguments(self):
        return self.arguments

    def get_args(self):
        return self.get_arguments()

    def branching_allowed(self):
        return self.branching


class Temp:
    NULL = '$__NULL__'


class IdIsNotUnique(Exception):
    pass


class ParameterAlreadyExists(Exception):
    pass


class ParameterNotFound(Exception):
    pass


class WrongCollectionPath(Exception):
    pass


class SystemNotFound(Exception):
    pass


class SubsystemNotFound(Exception):
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


class ClassEntityNotFound(Exception):
    pass


class SystemEntityNotFound(Exception):
    pass


class SubclassesOrderNotSupported(Exception):
    pass


class AddedBehaviourNotSupported(Exception):
    pass


class IntrusionIsEmpty(Exception):
    pass


class IntrusionUnsupportedType(Exception):
    pass


class InheritElementAlreadyExists(Exception):
    pass


class UnknownForkID(Exception):
    pass


class MalformedSubOrder(Exception):
    pass


class RepeatedClassAssignment(Exception):
    pass
