from enum import Enum


ALPHABET = list(r"abcdefghijklmnopqrstuvwxyz0123456789\()")


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
        transactions: dict[tuple[int, str] : int],
        initial_state: int,
        final_states: set[int],
    ):
        self.alphabet = ALPHABET
        self.transactions = transactions
        self.initial_state = initial_state
        self.final_states = final_states

    def validate_word_symbols_in_alphabet(self, word):
        for symbol in word:
            if symbol not in self.alphabet:
                raise Exception(f'Invalid symbol "{symbol}".')

    def run(self, word: str) -> bool:
        self.validate_word_symbols_in_alphabet(word)

        state = self.initial_state
        symbols = list(word)

        while symbols:
            try:
                state = self.transactions[(state, symbols.pop(0))]
            except KeyError:
                break
        return state in self.final_states


def build_full_word_transactions(word: str) -> tuple[dict[tuple[int, str] : int], int]:
    state = 0
    final_state = state + 1
    transactions = {}
    for symbol in word:
        transactions[(state, symbol)] = final_state
        state += 1
        final_state += 1

    return transactions, final_state


def build_number_alphabet_transactions() -> dict[tuple[int, str] : int]:
    valid_symbols = "abcdefghijklmnopqrstuvwxyz0123456789"
    transactions = {}
    for symbol in valid_symbols:
        transactions[(0, symbol)] = 1
        transactions[(1, symbol)] = 1
    return transactions


def build_list_dfa():
    DFAs = {
        Lexeme.CONSTANT: [],
        Lexeme.UNARY_OPERATOR: [],
        Lexeme.BINARY_OPERATOR: [],
        Lexeme.PROPOSITION: [
            DeterministicFiniteAutomata(
                transactions=build_number_alphabet_transactions(),
                initial_state=0,
                final_states={1},
            ),
        ],
        Lexeme.OPEN_PARENTHESIS: [
            DeterministicFiniteAutomata(
                transactions={(0, "("): 1}, initial_state=0, final_states={1}
            ),
        ],
        Lexeme.CLOSE_PARENTHESIS: [
            DeterministicFiniteAutomata(
                transactions={(0, ")"): 1}, initial_state=0, final_states={1}
            ),
        ],
    }
    for word in ["true", "false"]:
        transactions, final_state = build_full_word_transactions(word)
        DFAs[Lexeme.CONSTANT].append(
            DeterministicFiniteAutomata(
                transactions=transactions, initial_state=0, final_states={final_state}
            )
        )

    for word in [r"\neg"]:
        transactions, final_state = build_full_word_transactions(word)
        DFAs[Lexeme.UNARY_OPERATOR].append(
            DeterministicFiniteAutomata(
                transactions=transactions, initial_state=0, final_states={final_state}
            )
        )

    for word in [
        r"\wedge",
        r"\vee",
        r"\rightarrow",
        r"\leftrightarrow",
    ]:
        transactions, final_state = build_full_word_transactions(word)
        DFAs[Lexeme.BINARY_OPERATOR].append(
            DeterministicFiniteAutomata(
                transactions=transactions, initial_state=0, final_states={final_state}
            )
        )

    return DFAs


class LexicalAnalyser:
    def __init__(self):
        self.lexemes = build_list_dfa()

    def execute(self, content: str) -> list[tuple[Lexeme, str]]:
        tokens: list[tuple[Lexeme, str]] = []

        index = 1
        word = ""
        while content:
            word += content[0]
            content = content[1:]

            for lexeme, DFAs in self.lexemes.items():
                for DFA in DFAs:
                    if DFA.run(word):
                        tokens.append((lexeme, word))
                        word = ""

        return tokens


content = "(asdf)"
analyser = LexicalAnalyser()
print(analyser.execute(content))
print(analyser.execute(content)[1][0] == Lexeme.CLOSE_PARENTHESIS)
