import yaml
import parglare
from parglare.actions import collect_sep, collect_sep_optional
import prettyprinter
from prettyprinter import pprint, cpprint
import dataclasses
import json

import sys

from parglare_adapter import to_parglare_grammar
from facts import Fact, Judgement, Variable, Name, ComplexTerm, List
#from expressions import Expression

prettyprinter.install_extras(['dataclasses'])

with open('semantics.bnf.yml', 'rt') as f:
    grammar = yaml.load(f)
    for s in grammar['string_terminals']:
        assert s not in grammar['terminals']
        grammar['terminals'][s] = ('string', s)

def pass_many(indexes):
    def action(_, nodes):
        return [
            nodes[i]
            for i in indexes
        ]
    return action


def pass_single(i):
    def action(_, nodes):
        return nodes[i]
    return action


def to_action(f):
    def wrapped(_, nodes):
        return f(*nodes)
    return wrapped


def const_name_factory(name):
    def action(_1, _2):
        return Name(name)
    return action


def complex_term_factory(name, indexes):
    def action(_, nodes):
        return ComplexTerm(name, [
            nodes[i]
            for i in indexes
        ])
    return action

expression_factory = complex_term_factory
binop_factory = lambda _, x: ComplexTerm(x[2], [x[0], x[4]])


def fact_factory(name, indexes, result_indexes):
    def action(_, nodes):
        return Fact(name, [
            nodes[i]
            for i in indexes
        ], [
            nodes[i]
            for i in result_indexes
        ])
    return action


def const(v):
    def action(_, _2):
        return v
    return action


def builtin(_, x):
    def _concat(x):
        if isinstance(x, str):
            return x
        else:
            return ''.join([_concat(e) for e in x])
    return Name(_concat(x))


actions = {
    'start': pass_single(0),
    'judgements': collect_sep,
    'judgement': [
        to_action(lambda premises, _1, _11, _2, _3, conclusion, _4: Judgement(premises, conclusion)),
        to_action(lambda _2, _3, conclusion, _4: Judgement([], conclusion)),
    ],
    'facts': collect_sep,
    'fact': [
        fact_factory('expression_shifted', [2, 4, 6, 8], [13]),
        fact_factory('context_shifted', [2, 4, 6, 8], [13]),
        fact_factory('substituted', [0, 2, 4, 8], [13]),
        lambda _, x: Fact('substituted', [x[0], x[2], Name('zero'), x[6]], [x[11]]),
        fact_factory('apha_normalized', [0], [4]),
        fact_factory('beta_normalized', [0], [4]),
        fact_factory('same', [0, 4], []),
        fact_factory('encoded', [2], [7]),
        fact_factory('decoded', [2], [7]),
        fact_factory('keys', [2], [7]),
        fact_factory('sort', [2], [7]),
        fact_factory('function_check', [0, 4], [8]),
        fact_factory('normalized_inferred_type', [0, 4], [9]),
        fact_factory('inferred_type', [0, 4], [8]),
        lambda _, x: Fact('normalized_inferred_type', [List.from_list([]), x[0]], [x[5]]),
        fact_factory('least_upper_bound', [0, 4], [8]),
    ],
    'context': [
        const(List.from_list([])),
        lambda _, x: Variable(x[0]),
        lambda _, x: List(
            head=ComplexTerm('field', [x[3], x[7]]),
            tail=Variable(x[0]),
        ),
        pass_single(1),
    ],
    'expr0': [
        lambda _, x: ComplexTerm('forall', [
            Name('_'),
            x[0],
            x[4],
        ]),
        pass_single(0),
    ],
    'expr1': [
        expression_factory('let_single_in', [2, 6, 10]),
        expression_factory('let_single_typed_in', [2, 6, 10, 14]),
        expression_factory('let_more_in', [2, 6]),
        expression_factory('let_signle_let_more_in', [2, 6, 10, 14]),
        expression_factory('let_single_typed_let_more_in', [2, 6, 10, 14, 18]),
        expression_factory('if_then_else', [2, 6, 10]),
        expression_factory('lambda', [2, 6, 11]),
        expression_factory('forall', [2, 6, 11]),
        expression_factory('nil', [5]),
        #expression_factory('nothing', [7]),
        #expression_factory('just', [2, 10]),
        binop_factory,
        pass_single(0),
    ],
    'expr2': [
        binop_factory,
        expression_factory('application', [0, 2]),
        expression_factory('merge_typed', [2, 4, 8]),
        expression_factory('merge', [2, 4]),
        expression_factory('to_map_typed', [2, 4]),
        expression_factory('to_map', [2]),
        expression_factory('assert', [4]),
        expression_factory('type_bound', [0, 4]),
        pass_single(0),
    ],
    'expr3': [
        pass_single(1),
        pass_single(0),
        lambda _, x: ComplexTerm('to_string', [Variable(x[1])]),

        expression_factory('var', [0, 2]),
        lambda _, x: ComplexTerm('var', [Name(x[0]), Name('zero')]),

        const(Name('zero')),
        const(ComplexTerm('s', [Name('zero')])),

        expression_factory('single_element_list', [2]),
        expression_factory('list_more', [2]),
        expression_factory('list_single_and_more', [2, 5]),

        binop_factory,

        expression_factory('field_select', [0, 2]),
        expression_factory('fields_projection_by_type', [0, 3]),
        expression_factory('fields_select_empty', [0]),
        expression_factory('fields_select_single', [0, 4]),
        expression_factory('fields_select_more', [0, 4]),
        expression_factory('fields_select_single_and_single', [0, 4, 7]),

        complex_term_factory('double', [0]),
        complex_term_factory('double_to_string', [1]),
        const_name_factory('natural'),
        const_name_factory('natural_to_integer'),
        const_name_factory('natural_to_text'),
        const_name_factory('integer'),
        const_name_factory('integer_to_double'),
        const_name_factory('integer_to_text'),

        const_name_factory('string_empty'),
        complex_term_factory('string_chunk', [1]),
        complex_term_factory('string_chunk_chunk', [1, 2]),
        complex_term_factory('string_more', [1]),
        complex_term_factory('string_chunk_chunk_more', [1, 2, 3]),
        complex_term_factory('string_interpolation_more', [3, 5]),
        complex_term_factory('string_chunk_interpolation_more', [1, 4, 6]),
        complex_term_factory('string_chunk_chunk_interpolation_more_more', [1, 2, 5, 7, 8]),
        complex_term_factory('string_interpolation_interpolation', [3, 7]),

        lambda _, x: ComplexTerm('record_type_or_value', [List.from_list([], x[2])]),
        const(ComplexTerm('record_type', [List.from_list([])])),
        lambda _, x: ComplexTerm('record_type', [
            List.from_list(x[2]),
        ]),
        lambda _, x: ComplexTerm('record_type', [
            List.from_list(x[2], x[5]),
        ]),
        const(ComplexTerm('record', [List.from_list([])])),
        lambda _, x: ComplexTerm('record', [
            List.from_list(x[2]),
        ]),
        lambda _, x: ComplexTerm('record', [
            List.from_list(x[2], x[5]),
        ]),

        const(ComplexTerm('union_type', [List.from_list([])])),
        lambda _, x: ComplexTerm('union_type', [x[2]]),
        lambda _, x: ComplexTerm('union_type', [List.from_list([
            ComplexTerm('field', [x[2], x[6]]),
        ])]),
        lambda _, x: ComplexTerm('union_type', [List(
            head=ComplexTerm('field', [x[2], x[6]]),
            tail=x[10],
        )]),
        lambda _, x: ComplexTerm('union_type', [List(
            head=ComplexTerm('label', [x[2]]),
            tail=x[6],
        )]),
        lambda _, x: ComplexTerm('union', [
            x[2],
            x[6],
            List.from_list([]),
        ]),
        lambda _, x: ComplexTerm('union', [
            x[2],
            x[6],
            x[10],
        ]),
        lambda _, x: ComplexTerm('union', [
            x[2],
            x[6],
            List(
                head=ComplexTerm('field', [x[10], x[14]]),
                tail=x[18],
            ),
        ]),

        complex_term_factory('some', [2]),
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,
        builtin,

        const_name_factory('missing_import'),
        const_name_factory('absolute_import'),
        const_name_factory('relative_import'),
        const_name_factory('relative_up_import'),
        const_name_factory('home_import'),
        const_name_factory('http_import'),
        const_name_factory('http_import_using'),
        const_name_factory('env_import'),
    ],
    'inc_or_dec': [
        const_name_factory('inc'),
        const_name_factory('dec'),
        lambda _, _2: Variable('d'),
    ],
    'nat': [
        const(Name('zero')),
        lambda _, x: x[0],
        complex_term_factory('s', [4]),
        complex_term_factory('s', [0]),
        lambda _, x: x[1],
    ],
    'identifier': [
        lambda _, x: Name(x[0]),
    ],
    'var': [
        lambda _, x: Variable(x[0]),
        lambda _, x: Variable(x[0]),
        lambda _, x: Variable(x[0]),
        lambda _, x: Variable(x[0]),
    ],
    'var*': [
        lambda _, _2: Variable('_'),
        lambda _, x: Variable(x[0]),
        complex_term_factory('set_difference', [0, 4]),
        complex_term_factory('set_intersection', [0, 4]),
    ],
    'var_string': [
        lambda _, x: Variable(x[0]),
    ],
    'var_string*': [
        lambda _, x: Variable(x[0] + x[1]),
    ],
    'var_nat': lambda _, x: Variable(x[0]),
    'record_type_fields': [
        lambda _, x: [ComplexTerm('field', [x[0], x[4]])],
        lambda _, x: x[0] + [ComplexTerm('field', [x[3], x[7]])],
    ],
    'record_value_fields': [
        lambda _, x: [ComplexTerm('field', [x[0], x[4]])],
        lambda _, x: x[0] + [ComplexTerm('field', [x[3], x[7]])],
    ],
    'var_or_label': [
        pass_single(0),
        lambda _, x: Name(x[0][1:-1]),
    ]
}

pg_grammar, start = to_parglare_grammar(grammar['productions'], grammar['terminals'], grammar['start'])
parser = parglare.GLRParser(pg_grammar, ws='', actions=actions)



current_block_lines = []
judgements = []
judgement = False
for i, line in enumerate(sys.stdin):
    if line.startswith('!stop'):
        break
    if line.startswith('    '):
        current_block_lines.append(line[4:])
        if line.startswith('    ─'):
            judgement = True
    else:
        if judgement:
            print('line {}'.format(i), file=sys.stderr)
            block = ''.join(current_block_lines)
            t = parser.parse(block)
            if len(t) > 1:
                pprint(t)
                assert len(t) == 1, "got multiple parses while parsing:\n{}".format(block)
            for j in t[0]:
                judgements.append(dataclasses.asdict(j))
            #    cpprint(dataclasses.asdict(j))
            #    #print(j.as_prolog_clause())
        current_block_lines = []
        judgement = False

print(json.dumps(
    judgements,
    sort_keys=True,
    indent=2,
))
