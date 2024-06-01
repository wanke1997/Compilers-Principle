from pathlib import Path
import re
import pathlib
from typing import Dict, List, Set, Tuple

CURRENT_FILE_PATH = pathlib.Path(__file__).parent.resolve()
DEFAULT_TESTCASE_DIR = "input"


class LL1Parser:
    def __init__(self) -> None:
        self.start = "A"
        self.grammar: Dict[str, List[str]] = {
            "A": ["V=E"],
            "E": ["TG"],
            "G": ["BTG", "e"],
            "T": ["FQ"],
            "Q": ["MFQ", "e"],
            "F": ["(E)", "i"],
            "B": ["+", "-"],
            "M": ["*", "/"],
            "V": ["i"],
        }
        # self.start = "S"
        # self.grammar: Dict[str, List[str]] = {
        #     "S": ["BT"],
        #     "T": ["aB", "e"],
        #     "B": ["DC"],
        #     "C": ["b", "e"],
        #     "D": ["d", "e"],
        # }
        # self.start = "S"
        # self.grammar = {
        #     "S": ["E$"],
        #     "E": ["TG"],
        #     "G": ["+TG", "e"],
        #     "T": ["FQ"],
        #     "Q": ["*FQ", "e"],
        #     "F": ["(E)", "i"],
        # }
        self.string = ""
        self.terminals: Set[str] = set()
        self.non_terminals: Set[str] = set()
        self.first_dict: Dict[str, Set[str]] = {}
        self.first_sentence_dict: Dict[str, Set[str]] = {}
        self.follow_dict: Dict[str, Set[str]] = {}
        self.chart: Dict[Tuple[str, str], str] = {}

        self.preprocess()
        self.get_first_set()
        self.get_first_sentence_dict()
        self.get_follow_set()
        self.build_chart()

    def read_file(self, filepath: Path) -> None:
        f = open(filepath, "r")
        pattern = r"'[^']*'"
        read_string = f.readline()
        while read_string:
            match_string = re.findall(pattern, read_string)[0]
            if match_string is not None:
                self.string += match_string[1 : len(match_string) - 1]
            read_string = f.readline()
        f.close()

    def preprocess(self) -> None:
        self.terminals.add("#")
        for key, value in self.grammar.items():
            self.non_terminals.add(key)
            for s in value:
                for ch in s:
                    if ch.isupper():
                        self.non_terminals.add(ch)
                    else:
                        self.terminals.add(ch)

    def get_first_set(self) -> None:
        self.first_dict = {s: set() for s in (self.terminals | self.non_terminals)}
        # 1. calculate first set for terminals
        for x in self.terminals:
            self.first_dict[x].add(x)
        # 2. calculate first set for x->aX, which a is a terminal
        for x, right in self.grammar.items():
            for r in right:
                if r[0] in self.terminals:
                    self.first_dict[x].add(r[0])
        # 3. calculate first set for normal cases
        set_updated = True
        while set_updated:
            set_updated = False
            for x, right in self.grammar.items():
                if x in self.terminals:
                    continue
                for r in right:
                    if r[0] in self.terminals:
                        continue
                    # rule 3.1
                    prev_len = len(self.first_dict[x])
                    self.first_dict[x] |= self.first_dict[r[0]] - {"e"}
                    if len(self.first_dict[x]) > prev_len:
                        set_updated = True
                    # rule 3.2
                    for i in range(1, len(r)):
                        if r[i - 1] not in self.non_terminals or "e" not in self.first_dict[r[i - 1]]:
                            break
                        else:
                            prev_len = len(self.first_dict[x])
                            self.first_dict[x] |= self.first_dict[r[i]] - {"e"}
                            if len(self.first_dict[x]) > prev_len:
                                set_updated = True
                    # rule 3.3
                    add_e = sum(
                        [1 if r[i] in self.non_terminals and "e" in self.first_dict[r[i]] else 0 for i in range(len(r))]
                    ) == len(r)
                    if add_e == True:
                        prev_len = len(self.first_dict[x])
                        self.first_dict[x].add("e")
                        if len(self.first_dict[x]) > prev_len:
                            set_updated = True

    def get_first_sentence_dict(self) -> None:
        for sentences in self.grammar.values():
            for sentence in sentences:
                self.first_sentence_dict[sentence] = set()
                self.first_sentence_dict[sentence] |= self.first_dict[sentence[0]] - {"e"}
                for i in range(1, len(sentence)):
                    if "e" in self.first_dict[sentence[i - 1]]:
                        self.first_sentence_dict[sentence] |= self.first_dict[sentence[i]] - {"e"}
                    else:
                        break
                add_e = sum([1 if "e" in self.first_dict[sentence[i]] else 0 for i in range(len(sentence))]) == len(sentence)
                if add_e == True:
                    self.first_sentence_dict[sentence].add("e")

    def get_follow_set(self) -> None:
        self.follow_dict = {s: set() for s in (self.non_terminals)}
        # rule 1
        self.follow_dict[self.start].add("#")
        # rule 2 and rule 3 iteration
        set_updated = True
        while set_updated:
            set_updated = False
            for x, right in self.grammar.items():
                if x not in self.non_terminals:
                    continue
                for r in right:
                    # rule 2
                    if len(r) >= 2:
                        for idx, ch in enumerate(r):
                            if ch not in self.non_terminals or idx == len(r) - 1:
                                continue
                            else:
                                next_ch = r[idx + 1]
                                prev_len = len(self.follow_dict[ch])
                                self.follow_dict[ch] |= self.first_dict[next_ch] - {"e"}
                                if len(self.follow_dict[ch]) > prev_len:
                                    set_updated = True
                    # rule 3.1
                    if len(r) >= 1 and r[-1] in self.non_terminals:
                        prev_len = len(self.follow_dict[r[-1]])
                        self.follow_dict[r[-1]] |= self.follow_dict[x]
                        if len(self.follow_dict[r[-1]]) > prev_len:
                            set_updated = True
                    # rule 3.2
                    if len(r) >= 2:
                        for idx, ch in enumerate(r):
                            if ch not in self.non_terminals or idx == len(r) - 1:
                                continue
                            else:
                                next_ch = r[idx + 1]
                                if "e" in self.first_dict[next_ch]:
                                    prev_len = len(self.follow_dict[ch])
                                    self.follow_dict[ch] |= self.follow_dict[x]
                                    if len(self.follow_dict[ch]) > prev_len:
                                        set_updated = True

    def build_chart(self) -> None:
        self.chart = {}
        for A in self.grammar:
            for a in self.terminals:
                if a == "e":
                    continue
                for sentence in self.grammar[A]:
                    if a in self.first_sentence_dict[sentence]:
                        self.chart[(A, a)] = sentence
                    if "e" in self.first_sentence_dict[sentence]:
                        for b in self.follow_dict[A]:
                            if b in self.terminals:
                                self.chart[(A, b)] = sentence

    def parse(self, filepath: Path) -> bool:
        self.read_file(filepath)
        # initialization
        appended_string = self.string + "#"
        stack: List[str] = list()
        stack.append("#")
        stack.append(self.start)
        pt = 0

        while stack and pt < len(appended_string):
            print("stack: {}, string: {}".format(stack, appended_string[pt:]))
            X = stack[-1]
            a = appended_string[pt]
            # case1: X is non-terminal
            if X in self.non_terminals:
                key = (X, a)
                if key not in self.chart:
                    raise Exception("error: tuple ({},{}) not in the chart".format(X, a))
                else:
                    sentence = self.chart[key]
                    stack.pop()
                    if sentence != "e":
                        for idx in range(len(sentence) - 1, -1, -1):
                            stack.append(sentence[idx])
            # case 2: X is terminal, but not '#'
            elif X in self.terminals and X != "#":
                if X == a:
                    stack.pop()
                    pt += 1
                else:
                    raise Exception("error: X and a do not match")
            # case 3: X is '#'
            elif X == "#":
                if X == a:
                    return True
                else:
                    raise Exception("error: X and a do not match")
            # error handling
            else:
                raise Exception("error: unrecognized character detected: {}, {}".format(X, a))
        return False


if __name__ == "__main__":
    testcase = "test_case1.txt"
    filepath = Path(CURRENT_FILE_PATH).joinpath(DEFAULT_TESTCASE_DIR).joinpath(testcase)
    parser = LL1Parser()
    res = parser.parse(filepath)
    print("Parse result is {}".format(res))
