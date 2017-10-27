## Two (or more) ways to solve the char replacement problem
### 1. !override behaviour and pair-in-class usage
```python
rombandeeva.add_element('universal:char_regex', '([ГЛАСНЫЙ])с([ГЛАСНЫЙ])', 'XsX_sequence').applied(
    [
        grammar.LinkSentence('#'),
        []
    ]    
).add_class('XsX_pair')

rombandeeva.add_element('universal:char_regex:responsive', 'c\g<2>', 'XsX_sequence').applied(
    [
        grammar.LinkSentence('#'),
        [grammar.Action('seq:correction:mansi:XsX')]
    ]    
).add_class('XsX_pair')

rombandeeva.get_class('XsX_pair').added_behaviour('!override')
```
This, however, needs a `seq:correction:mansi:*` mutation (`*` for multiple cases; `XsX` for the single case) to be run.
### 2. 'replace' behaviour
Not a conceptual way because the final system may not be defined
