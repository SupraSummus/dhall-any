from dataclasses import dataclass


class Term:
    pass


@dataclass
class Variable(Term):
    variable: str

    def as_prolog_term(self):
        return 'Var_{}'.format(self.variable)


@dataclass
class Name(Term):
    name: str

    def as_prolog_term(self):
        return self.name


@dataclass
class ComplexTerm(Term):
    name: str
    children: [Term]

    def as_prolog_term(self):
        return '{}({})'.format(self.name, ', '.join([
            c.as_prolog_term()
            for c in self.children
        ]))


class List(ComplexTerm):
    def __init__(self, head, tail):
        super().__init__('list', [head, tail])

    @classmethod
    def from_list(cls, elements, tail=None):
        if len(elements) == 0:
            if tail is None:
                return Nil()
            else:
                return tail
        return List(elements[0], List.from_list(elements[1:], tail))

    def as_prolog_term(self):
        return '[{} | {}]'.format(
            self.childred[0].as_prolog_term(),
            self.children[1].as_prolog_term(),
        )


class Nil(Name):
    def __init__(self):
        super().__init__('nil')

    def as_prolog_term(self):
        return '[]'


@dataclass
class Fact:
    name: str
    arguments: [Term]
    results: [Term]

    def as_prolog_predicate(self):
        return '{}({})'.format(
            self.name,
            ', '.join([
                a.as_prolog_term()
                for a in self.arguments + self.results
            ]),
        )


@dataclass
class Judgement:
    premises: [Fact]
    conclusion: Fact

    def as_prolog_clause(self):
        if len(self.premises) > 0:
            return '{} :-\n\t{}.'.format(
                self.conclusion.as_prolog_predicate(),
                ',\n\t'.join([
                    p.as_prolog_predicate()
                    for p in self.premises
                ]),
            )
        else:
            return '{}.'.format(self.conclusion.as_prolog_predicate())
