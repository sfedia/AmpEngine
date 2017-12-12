import re


def ParameterPair(a, b):
    return {'key':a, 'value':b}

class WrongLinkSentence(Exception):
    pass

def parse_sector(sector, element):
    global WrongLinkSentence
    sector = sector.strip()
    sector_rx = r'([\w:]+)((\*?=|\?))\(([^\)]*)\)|\s*([&\|])\s*|(\[.*\])'

    class GroupEq:
        comparison = 3
        sector_op = 1

    parsed_list = []
    RE_SHARP = r"^#\s*"
    if re.search(RE_SHARP, sector):
        parsed_list.append("__SHARP__")
        sector = re.sub(RE_SHARP, '', sector)

    parsed_sector = re.findall(sector_rx, sector)


    for seq in parsed_sector:
        f_seq = [x for x in seq if x != '']
        for op in ('=', '*='):
            if op in f_seq:
                f_seq.remove(op)
        print(f_seq)
        if f_seq == ['#']:
            parsed_list.append('SHARPЪ')
        elif len(f_seq) == GroupEq.comparison:
            if f_seq[1] == '=':
                parameter_pair = ParameterPair(f_seq[0], f_seq[2])
            elif f_seq[1] == '*=':
                parameter_pair = ParameterPair(f_seq[0], element.get_parameter(f_seq[2]))
            else:
                raise WrongLinkSentence()
            parsed_list.append(parameter_pair)
        elif len(f_seq) == GroupEq.sector_op:
            fs_extracted = f_seq[0].strip()
            if fs_extracted[0] == '[':
                parsed_list.append(parse_sector(fs_extracted[1:-1].strip(), element))
            elif fs_extracted in ['&', '|']:
                parsed_list.append(fs_extracted)
            else:
                raise WrongLinkSentence()
        else:
            raise WrongLinkSentence()

    return parsed_list


print(parse_sector('# & universal:entity=(word) | [ a:bb=(b) | [ b:aa=(c) & c:ee=(d) ] ]', []))


