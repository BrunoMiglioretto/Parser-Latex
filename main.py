import sys
import copy
from enum import Enum
from typing import Any

ALPHABET = list(r"abcdefghijklmnopqrstuvwxyz0123456789\() ")


class Lexeme(Enum):
    CONSTANT = 1
    PROPOSITION = 2
    OPEN_PARENTHESIS = 3
    CLOSE_PARENTHESIS = 4
    UNARY_OPERATOR = 5
    BINARY_OPERATOR = 6


class DeterministicFiniteAutomata:
    def __init__(
        self,
        transactions: set[tuple[int, Any, int]],
        initial_state: int,
        final_states: set[int],
    ):
        self.alphabet = ALPHABET
        self.transactions = transactions
        self.initial_state = initial_state
        self.final_states = final_states
        self.state = self.initial_state

    @property
    def in_final_state(self) -> bool:
        return self.state in self.final_states

    def validate_symbol_symbols_in_alphabet(self, symbol):
        if symbol not in self.alphabet:
            raise Exception(f'Invalid symbol "{symbol}".')

    def execute(self, symbol: str):
        self.validate_symbol_symbols_in_alphabet(symbol)
        for transaction in self.transactions:
            if transaction[0] == self.state and transaction[1](symbol):
                self.state = transaction[2]
                break

    def reset(self):
        self.state = self.initial_state


def build_patterns():
    patterns = [
        (
            Lexeme.CONSTANT,
            DeterministicFiniteAutomata(
                transactions={
                    (0, lambda x: x not in "tf", 999),
                    # true
                    (0, lambda x: x == "t", 1),
                    (1, lambda x: x == "r", 2),
                    (2, lambda x: x == "u", 3),
                    (3, lambda x: x == "e", 4),
                    (4, lambda x: True, 5),
                    # false
                    (0, lambda x: x == "f", 6),
                    (6, lambda x: x == "a", 7),
                    (7, lambda x: x == "l", 8),
                    (8, lambda x: x == "s", 9),
                    (9, lambda x: x == "e", 10),
                    (10, lambda x: True, 11),
                },
                initial_state=0,
                final_states={4, 10},
            ),
        ),
        (
            Lexeme.PROPOSITION,
            DeterministicFiniteAutomata(
                transactions={
                    (0, lambda x: x in "0123456789", 1),
                    (0, lambda x: x not in "abcdefghijklmnopqrstuvwxyz0123456789", 999),
                    (1, lambda x: x in "abcdefghijklmnopqrstuvwxyz0123456789", 1),
                    (1, lambda x: x not in "abcdefghijklmnopqrstuvwxyz0123456789", 999),
                },
                initial_state=0,
                final_states={1},
            ),
        ),
        (
            Lexeme.OPEN_PARENTHESIS,
            DeterministicFiniteAutomata(
                transactions={
                    (0, lambda x: x == "(", 1),
                    (0, lambda x: x != "(", 999),
                    (1, lambda x: True, 999),
                },
                initial_state=0,
                final_states={1},
            ),
        ),
        (
            Lexeme.CLOSE_PARENTHESIS,
            DeterministicFiniteAutomata(
                transactions={
                    (0, lambda x: x == ")", 1),
                    (1, lambda x: True, 999),
                    (0, lambda x: x != ")", 999),
                },
                initial_state=0,
                final_states={1},
            ),
        ),
        (
            Lexeme.UNARY_OPERATOR,
            DeterministicFiniteAutomata(
                transactions={
                    (0, lambda x: x == "\\", 1),
                    (0, lambda x: x != "\\", 999),
                    (1, lambda x: x == "n", 2),
                    (2, lambda x: x == "e", 3),
                    (3, lambda x: x == "g", 4),
                    (4, lambda x: True, 999),
                },
                initial_state=0,
                final_states={4},
            ),
        ),
        (
            Lexeme.BINARY_OPERATOR,
            DeterministicFiniteAutomata(
                transactions={
                    (0, lambda x: x == "\\", 1),
                    (0, lambda x: x != "\\", 999),
                    # wedge
                    (1, lambda x: x == "w", 2),
                    (2, lambda x: x == "e", 3),
                    (3, lambda x: x == "d", 4),
                    (4, lambda x: x == "g", 5),
                    (5, lambda x: x == "e", 6),
                    (6, lambda x: True, 999),
                    # vee
                    (1, lambda x: x == "v", 7),
                    (7, lambda x: x == "e", 8),
                    (8, lambda x: x == "e", 9),
                    (9, lambda x: True, 999),
                    # rightarrow
                    (1, lambda x: x == "r", 10),
                    (10, lambda x: x == "i", 11),
                    (11, lambda x: x == "g", 12),
                    (12, lambda x: x == "h", 13),
                    (13, lambda x: x == "t", 14),
                    (14, lambda x: x == "a", 15),
                    (15, lambda x: x == "r", 16),
                    (16, lambda x: x == "r", 17),
                    (17, lambda x: x == "o", 18),
                    (18, lambda x: x == "w", 19),
                    (19, lambda x: True, 999),
                    # leftrightarrow
                    (1, lambda x: x == "l", 20),
                    (20, lambda x: x == "e", 21),
                    (21, lambda x: x == "f", 22),
                    (22, lambda x: x == "t", 23),
                    (23, lambda x: x == "r", 24),
                    (24, lambda x: x == "i", 25),
                    (25, lambda x: x == "g", 26),
                    (26, lambda x: x == "h", 27),
                    (27, lambda x: x == "t", 28),
                    (28, lambda x: x == "a", 29),
                    (29, lambda x: x == "r", 30),
                    (30, lambda x: x == "r", 31),
                    (31, lambda x: x == "o", 32),
                    (32, lambda x: x == "w", 33),
                    (33, lambda x: True, 999),
                },
                initial_state=0,
                final_states={6, 9, 19, 33},
            ),
        ),
    ]

    return patterns


class LexicalAnalyser:
    def __init__(self, content: str):
        self.patterns = build_patterns()
        self.content = content
        self.symbols = list(content)
        self.next_character_position = 0

    @property
    def end_of_file(self):
        return self.content[self.next_character_position] == "\n"

    def get_next_token(self) -> tuple[Lexeme, str] | None:
        if self.peek() == " ":
            self.next_character()

        word = ""
        while not self.end_of_file:
            symbol = self.next_character()
            word += symbol
            for pattern in self.patterns:
                dfa = pattern[1]
                dfa.execute(symbol)
                if dfa.in_final_state:
                    while dfa.in_final_state and not self.end_of_file:
                        dfa.execute(self.peek())
                        if dfa.in_final_state:
                            symbol = self.next_character()
                            word += symbol
                    self.reset_dfas()
                    return pattern[0], word
        else:
            return None

    def peek_next_token(self) -> tuple[Lexeme, str] | None:
        s = copy.copy(self)
        return s.get_next_token()

    def peek_peek_next_token(self):
        s = copy.copy(self)
        s.get_next_token()
        s = copy.copy(s)
        return s.get_next_token()

    def next_character(self) -> str:
        char = self.symbols[self.next_character_position]
        self.next_character_position += 1
        return char.lower()

    def peek(self) -> str:
        char = self.symbols[self.next_character_position]
        return char.lower()

    def reset_dfas(self):
        for pattern in self.patterns:
            pattern[1].reset()


class Rule(Enum):
    FORMULA = 0
    CONSTANT = 1
    PROPOSITION = 2
    UNARY_FORMULA = 3
    BINARY_FORMULA = 4
    OPEN_PARENTHESIS = 5
    CLOSE_PARENTHESIS = 6
    UNARY_OPERATOR = 7
    BINARY_OPERATOR = 8


class FormulaNode:
    def __init__(self, child):
        self.child = child


class ConstantNode:
    def __init__(self, value):
        self.value = value


class PropositionNode:
    def __init__(self, value):
        self.value = value


class UnaryFormulaNode:
    def __init__(self, child):
        self.child = child


class NegationFormulaNode(UnaryFormulaNode):
    def __init__(self, child):
        super().__init__(child=child)


class BinaryFormulaNode:
    def __init__(self, left_child, right_child):
        self.left_child = left_child
        self.right_child = right_child


class AndFormulaNode(BinaryFormulaNode):
    def __init__(self, left_child, right_child):
        super().__init__(left_child=left_child, right_child=right_child)


class OrFormulaNode(BinaryFormulaNode):
    def __init__(self, left_child, right_child):
        super().__init__(left_child=left_child, right_child=right_child)


class ImpliesFormulaNode(BinaryFormulaNode):
    def __init__(self, left_child, right_child):
        super().__init__(left_child=left_child, right_child=right_child)


class BiConditionalFormulaNode(BinaryFormulaNode):
    def __init__(self, left_child, right_child):
        super().__init__(left_child=left_child, right_child=right_child)


class OpenParenthesisNode:
    def __init__(self):
        pass


class CloseParenthesisNode:
    def __init__(self):
        pass


class UnaryOperatorNode:
    def __init__(self):
        pass


class NegationOperatorNode(UnaryOperatorNode):
    pass


class BinaryOperatorNode:
    def __init__(self):
        pass


class AndOperatorNode(BinaryOperatorNode):
    pass


class OrOperatorNode(BinaryOperatorNode):
    pass


class ImpliesOperatorNode(BinaryOperatorNode):
    pass


class BiConditionalOperatorNode(BinaryOperatorNode):
    pass


class Parser:
    def __init__(self, scanner: LexicalAnalyser):
        self.scanner = scanner

    def parse(self) -> FormulaNode:
        token = self.scanner.peek_next_token()

        if token[0] == Lexeme.CONSTANT:
            child_node = self.parse_constant()
        elif token[0] == Lexeme.PROPOSITION:
            child_node = self.parse_proposition()
        elif token[0] == Lexeme.OPEN_PARENTHESIS:
            next_token = self.scanner.peek_peek_next_token()
            if next_token[0] == Lexeme.UNARY_OPERATOR:
                child_node = self.parse_unary_formula()
            else:
                child_node = self.parse_binary_formula()
        else:
            raise Exception()

        root = FormulaNode(child=child_node)
        return root

    def parse_constant(self):
        token = self.scanner.get_next_token()
        if token[0] == Lexeme.CONSTANT:
            return ConstantNode(value=token[1])
        raise Exception()

    def parse_proposition(self):
        token = self.scanner.get_next_token()
        assert token[0] == Lexeme.PROPOSITION

        return PropositionNode(value=token[1])

    def parse_unary_formula(self):
        self.parse_open_parenthesis()
        self.parse_unary_operator()
        formula = self.parse()
        self.parse_close_parenthesis()

        return NegationFormulaNode(child=formula)

    def parse_binary_formula(self):
        self.parse_open_parenthesis()
        binary_operator = self.parse_binary_operator()
        left_child = self.parse()
        right_child = self.parse()
        self.parse_close_parenthesis()

        if AndOperatorNode == type(binary_operator):
            return AndFormulaNode(left_child=left_child, right_child=right_child)
        elif OrOperatorNode == type(binary_operator):
            return OrFormulaNode(left_child=left_child, right_child=right_child)
        elif ImpliesOperatorNode == type(binary_operator):
            return ImpliesFormulaNode(left_child=left_child, right_child=right_child)
        elif BiConditionalOperatorNode == type(binary_operator):
            return BiConditionalFormulaNode(
                left_child=left_child, right_child=right_child
            )
        raise Exception()

    def parse_open_parenthesis(self):
        token = self.scanner.get_next_token()
        if token[0] == Lexeme.OPEN_PARENTHESIS:
            return OpenParenthesisNode()
        raise Exception()

    def parse_close_parenthesis(self):
        token = self.scanner.get_next_token()
        if token[0] == Lexeme.CLOSE_PARENTHESIS:
            return CloseParenthesisNode()
        raise Exception()

    def parse_unary_operator(self):
        token = self.scanner.get_next_token()
        if token[0] == Lexeme.UNARY_OPERATOR:
            return NegationOperatorNode()
        raise Exception()

    def parse_binary_operator(self):
        token = self.scanner.get_next_token()
        if token[1] == r"\wedge":
            return AndOperatorNode()
        elif token[1] == r"\vee":
            return OrOperatorNode()
        elif token[1] == r"\rightarrow":
            return ImpliesOperatorNode()
        elif token[1] == r"\leftrightarrow":
            return BiConditionalOperatorNode()
        raise Exception()


if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "examples.txt"

with open(filename) as f:
    example_count = f.readline()
    examples = f.readlines()

for example in examples:
    scanner = LexicalAnalyser(example)
    parser = Parser(scanner)
    root_node = parser.parse()
