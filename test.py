import grammar

container = grammar.Container()

container.add_element('universal:affix:suffix', 'н', 'n_suffix')

container.get_by_id('n_suffix').set_parameter('one_character')

print(container.get_by_id('n_suffix').parameters)
