import json
from pprint import pprint
from unification import var, unify


def make_term_or_variable(d, variables):
    if isinstance(d, dict) and 'variable' in d:
        assert 'name' not in d
        name = d['variable']
        if name not in variables:
            variables[name] = var()
        return variables[name]

    if isinstance(d, dict) and 'name' in d:
        assert 'variable' not in d
        return (d['name'],) + tuple(
            make_term_or_variable(c, variables)
            for c in d.get('children', [])
        )

    assert False


def make_arguments(d, variables):
    return (d['name'],) + tuple(
        make_term_or_variable(arg, variables)
        for arg in d['arguments'] + d['results']
    )


with open('build/semantics.json', 'rt') as f:
    semantics = json.load(f)


rules = []
for judgement in semantics:
    variables = {}
    arguments = make_arguments(judgement['conclusion'], variables)
    premises = [
        make_arguments(p, variables)
        for p in judgement['premises']
    ]
    #print(arguments)
    #print('\t', premises)

    #def goal(args):
    #    return conde([eq(args, arguments)] + [
    #        satisfy(p)
    #        for p in premises
    #    ])
    rules.append((arguments, premises))


class SatisfyError(Exception):
    def __init__(self, statement, cause=None):
        super().__init__()
        self.statement = statement
        self.cause = cause

    def __str__(self):
        if self.cause is None:
            return f'Can\'t prove {self.statement}'
        else:
            return f'Can\'t prove {self.statement} because:\n\n{self.cause}'


def satisfy(statement, s=None):
    if s is None:
        s = {}

    # select rule we will be proving
    selected_rule = None
    for arguments, premises in rules:
        new_s = unify(statement, arguments, s)
        if new_s:
            if selected_rule is None:
                selected_rule = (
                    arguments,
                    premises,
                    new_s,
                )
            else:
                # more than one rule matches
                assert False

    # no matching rule
    if selected_rule is None:
        raise SatisfyError(statement)

    arguments, premises, new_s = selected_rule

    # debug
    print('\n#####')
    print('to prove: ', arguments)
    print('we need to prove first (all):', selected_rule[1])
    print('where', selected_rule[2])

    # prove premises
    for premise in premises:
        try:
            new_s = satisfy(premise, new_s)
        except SatisfyError as e:
            raise SatisfyError(statement, e)

    return new_s

x = var()
statetment = ('inferred_type', (), ('application', ('Double/show',), ('double', 3.14)), x)
print(satisfy(statetment))
