#!/usr/bin/python3
import re
import inspect
import structures_collection as collection
import resource_handler as resources
import convertation_handler as converter


class Container:
    def __init__(self):
        pass

    rows = []

    def get_all(self):
        return self.rows

    def get_by_id(self, element_id):
        for row in self.rows:
            if row.id == element_id:
                return row
        return False

    def get_actions_declaring(self, parameter, element, from_list = ()):
        afs = []
        if len(from_list) == 0:
            for row in self.rows:
                if len(row.apply_for) == 0:
                    continue
                for af in row.apply_for:
                    if len(af.actions) == 0:
                        for action in af.actions:
                            # allow resources ?
                            check_results = LinkSentence(af.link, self).check(element)
                            if parameter in action.edit_affected_parameters and check_results:
                                afs.append((row.get_id(), af))
        return afs

    def add_element(self, element_type, element_content, element_id):
        if self.get_by_id(element_id):
            raise IdIsNotUnique()
        element = ContainerElement(element_type, element_content, element_id)
        self.rows.append(element)

    def make_apply(self, link_action_pair, element_id):
        coll_handler = CollectionHandler()
        for row in self.rows:
            if LinkSentence(link_action_pair.link, self).check(row):
                # is it possible to make a variable?
                self.get_by_id(row.get_id()).add_applied(element_id)

                if len(link_action_pair.actions) > 0:
                    for action in link_action_pair.actions:
                        coll_handler.run_function(action.path, action.arguments)


class CollectionHandler:

    def __init__(self):
        pass

    def if_exists(self, path):
        if not re.search(r'^[\w_:]+$', path):
            raise WrongCollectionPath()

        s_path = path.split(':')

        if len(s_path) < 2:
            raise WrongCollectionPath()

        if not hasattr(collection, s_path[0]):
            raise NoSuchSystem()

        system = getattr(collection, s_path[0])()
        if not hasattr(system, s_path[1]):
            raise NoSuchSubsystem()
        else:
            subsystem = getattr(system, s_path[1])

        for step in s_path[2:]:
            if not hasattr(subsystem, step):
                raise NoSuchSubsystem()
            subsystem = getattr(subsystem, step)

        return subsystem

    def run_function(self, path, args = ()):
        function = self.if_exists(path)
        try:
            return function(args)
        except:
            raise WrongFunctionUse()

    def get_static(self, path):
        static = self.if_exists(path)
        if inspect.isclass(static):
            return static
        else:
            raise TypeIsNotStatic()


class ContainerElement:
    def __init__(self, element_type, element_content, element_id):
        self.type = element_type
        self.content = element_content
        self.id = element_id
        self.class_names = []
        self.apply_for = []
        self.applied_ids = []
        self.parameters = {}

    def apply(self, link_act_pair):
        self.apply_for += link_act_pair

    def add_applied(self, applied_id):
        self.applied_ids.append(applied_id)

    def add_class(self, class_name):
        if not class_name in self.class_names:
            self.class_names.append(class_name)

    def edit_parameter(self, key, value = True):
        self.parameters[key] = value

    def set_parameter(self, key, value = True):
        if not key in self.parameters:
            self.edit_parameter(key, value)
        else:
            raise ParameterExistsAlready()

    def get_parameter(self, key):
        if key in self.parameters:
            return self.parameters[key]
        else:
            raise NoSuchParameter()

    def get_id(self):
        return self.id


class LinkSentence:

    def __init__(self, link_string, container, from_list = (), allow_resources = True):
        self.link = link_string
        self.container = container
        if len(from_list) == 0:
            self.checked_list = container.get_all()
        else:
            self.checked_list = from_list
        self.allow_resources = allow_resources

    def check_element(self, element, param_pair, block_converter=False):
        try:
            is_good = element.get_parameter(param_pair.key) == param_pair.value
        except NoSuchParameter:
            good_afs = self.container.get_actions_declaring(param_pair.key, element)
            if len(good_afs) > 0:
                self.container.make_apply(good_afs[0][1], good_afs[0][0])
                is_good = element.get_parameter(param_pair.key) == param_pair.value
            elif self.allow_resources:
                parameter = resources.get_parameter(param_pair.key, element)
                if parameter:
                    is_good = parameter == param_pair.value
                elif not block_converter:
                    conv_variants = converter.convert_param_pair(param_pair.key, param_pair.value)
                    if len(conv_variants) == 0:
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
        def __init__(self, key, value=True):
            self.key = key
            self.value = value
            self.prop = 'ParameterPair'

    def parse_sector(self, sector, element):
        sector = sector.strip()
        sector_rx = r'([\w:]+)(\*?=)\(([^\)]*)\)|\s*([&\|])\s*|(\[[^\]]*\])'

        class GroupEq:
            comparison = 3
            sector_op = 1

        parsed_sector = re.findall(sector_rx, sector)

        parsed_list = []

        for seq in parsed_sector:
            f_seq = list(set(seq))
            if len(f_seq) == GroupEq.comparison:
                if f_seq == '=':
                    parameter_pair = self.ParameterPair(f_seq[0], f_seq[2])
                elif f_seq == '*=':
                    parameter_pair = self.ParameterPair(f_seq[0], element.get_parameter(f_seq[2]))
                else:
                    raise WrongLinkSentence()
                parsed_list.append(parameter_pair)
            elif len(f_seq) == GroupEq.sector_op:
                fs_extracted = f_seq[0].strip()
                if fs_extracted[0] == '[':
                    parsed_list.append(self.parse_sector(fs_extracted[1:-1].strip(), element))
                elif fs_extracted in ['&', '|']:
                    parsed_list.append(fs_extracted)
                else:
                    raise WrongLinkSentence()
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

        common_operator = '&' if '&' in complete_list else '|' if '|' in complete_list else False

        if not common_operator and (len(link_slice) > 1 or len(link_slice) == 0):
            raise WrongLinkSentence()

        if not common_operator:
            return link_slice[0]
        elif common_operator == '&':
            return not False in link_slice
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
		return self.path

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
