from pathlib import Path
import re
import pathlib
from typing import Dict, List, Set, Tuple

CURRENT_FILE_PATH = pathlib.Path(__file__).parent.resolve()
DEFAULT_TESTCASE_DIR = "input"


class OperatorPrecedenceParser:
    def __init__(self) -> None:
        self.start = "E"
        self.grammar = {
            "E": ["E+T", "E-T", "T"],
            "T": ["T*F", "T/F", "F"],
            "F": ["(E)", "i"],
        }
        self.reversed_grammar: Dict[str, str] = {}
        self.VT = set()
        self.VN = set()
        self.FirstVT: Dict[str, Set[str]] = {}
        self.LastVT: Dict[str, Set[str]] = {}
        self.chart: Dict[Tuple[str, str], str] = {}
        self.preprocess()
        self.build_FirstVT()
        self.build_LastVT()
        self.build_chart()

    def read_file(self, filepath: Path) -> str:
        f = open(filepath, "r")
        pattern = r"'[^']*'"
        string = ""
        read_string = f.readline()
        while read_string:
            match_string = re.findall(pattern, read_string)[0]
            if match_string is not None:
                string += match_string[1 : len(match_string) - 1]
            read_string = f.readline()
        f.close()
        return string

    def preprocess(self) -> None:
        # build reversed grammar
        for key, values in self.grammar.items():
            for value in values:
                self.reversed_grammar[value] = key
        # build VT and VN set
        for key, values in self.grammar.items():
            for chr in key:
                if chr.isupper():
                    self.VN.add(chr)
                else:
                    self.VT.add(chr)
            for value in values:
                for chr in value:
                    if chr.isupper():
                        self.VN.add(chr)
                    else:
                        self.VT.add(chr)
        # initialize FirstVT and LastVT
        self.FirstVT = {key: set() for key in self.VN}
        self.LastVT = {key: set() for key in self.VN}

    def build_FirstVT(self) -> None:
        # rule 1: initialization
        for key, values in self.grammar.items():
            for value in values:
                if len(value) >= 1 and value[0] in self.VT:
                    self.FirstVT[key].add(value[0])
                if len(value) >= 2 and value[0] in self.VN and value[1] in self.VT:
                    self.FirstVT[key].add(value[1])

        # rule 2: update
        need_update = True
        while need_update:
            need_update = False
            for key, values in self.grammar.items():
                for value in values:
                    if len(value) >= 1 and value[0] in self.VN:
                        prev_length = len(self.FirstVT[key])
                        self.FirstVT[key] |= self.FirstVT[value[0]]
                        if prev_length < len(self.FirstVT[key]):
                            need_update = True
        # Done
        return

    def build_LastVT(self) -> None:
        # rule 1: initialization
        for key, values in self.grammar.items():
            for value in values:
                if len(value) >= 1 and value[-1] in self.VT:
                    self.LastVT[key].add(value[-1])
                if len(value) >= 2 and value[-1] in self.VN and value[-2] in self.VT:
                    self.LastVT[key].add(value[-2])
        # rule 2: update
        need_update = True
        while need_update:
            need_update = False
            for key, values in self.grammar.items():
                for value in values:
                    if len(value) >= 1 and value[-1] in self.VN:
                        prev_length = len(self.LastVT[key])
                        self.LastVT[key] |= self.LastVT[value[-1]]
                        if prev_length < len(self.LastVT[key]):
                            need_update = True
        # Done
        return

    def build_chart(self) -> None:
        for _, values in self.grammar.items():
            for value in values:
                for i in range(0, len(value) - 1):
                    if value[i] in self.VT and value[i + 1] in self.VT:
                        self.chart[(value[i], value[i + 1])] = "="
                    if i < len(value) - 2 and value[i] in self.VT and value[i + 1] in self.VN and value[i + 2] in self.VT:
                        self.chart[(value[i], value[i + 2])] = "="
                    if value[i] in self.VT and value[i + 1] in self.VN:
                        for b in self.FirstVT[value[i + 1]]:
                            self.chart[(value[i], b)] = "<"
                    if value[i] in self.VN and value[i + 1] in self.VT:
                        for a in self.LastVT[value[i]]:
                            self.chart[(a, value[i + 1])] = ">"
        for vt in self.VT:
            self.chart[("#", vt)] = "<"
            self.chart[(vt, "#")] = ">"
        self.chart[("#", "#")] = "="
        return

    def reduce_sentence(self, input: str) -> str:
        # hard coded, if use another grammar, then we need to rewrite this method
        if input is None or len(input) == 0:
            raise Exception("error: the input string is empty.")
        elif len(input) == 1:
            if input in {"i", "F", "T"}:
                return self.reversed_grammar[input]
            elif input == "E":
                return "E"
            else:
                raise Exception("error: unexpected character, {}".format(input))
        elif len(input) == 3:
            if input[1] == "+" and input[0] in self.VN and input[2] in self.VN:
                return self.reversed_grammar["E+T"]
            elif input[1] == "-" and input[0] in self.VN and input[2] in self.VN:
                return self.reversed_grammar["E-T"]
            elif input[1] == "*" and input[0] in self.VN and input[2] in self.VN:
                return self.reversed_grammar["T*F"]
            elif input[1] == "/" and input[0] in self.VN and input[2] in self.VN:
                return self.reversed_grammar["T/F"]
            elif input[0] == "(" and input[2] == ")" and input[1] in self.VN:
                return self.reversed_grammar["(E)"]
            else:
                raise Exception("error: unexpected character, {}".format(input))
        else:
            raise Exception("error: unexpected character, {}".format(input))

    def _find_operators_helper(self, stack: List[str]) -> List[Tuple[int, str]]:
        res = []
        for idx, s in enumerate(stack):
            if s in self.VT or s == "#":
                res.append((idx, s))
        return res

    def parse(self, filepath: Path) -> bool:
        string = self.read_file(filepath) + "#"
        pt = 0
        stack = []
        stack.append("#")
        start = 0
        cur_operator_idx = 0

        while stack and pt < len(string):
            key = (stack[cur_operator_idx], string[pt])
            print("stack: {}, cur_ch: {}".format(stack, string[pt]))
            if key not in self.chart:
                raise Exception("error: no such compare relationship: {}".format(key))
            elif self.chart[key] == "<":
                # if S[start] < string[pt], it means that we haven't found the start of handle yet
                stack.append(string[pt])
                # update the value of start and cur_operator_idx
                if cur_operator_idx > start:
                    start = cur_operator_idx
                cur_operator_idx = len(stack) - 1
                pt += 1
            elif self.chart[key] == "=":
                # if S[start] = string[pt], it means that the handle already started, but not ended
                stack.append(string[pt])
                cur_operator_idx = len(stack) - 1
                pt += 1
            else:
                # if S[start] < string[pt], it means that the last character is the end of handle.
                # We need to do reduction in this case
                end = len(stack) - 1
                sentence = "".join(stack[start + 1 : end + 1])
                # remove the sentence
                for _ in range(len(sentence)):
                    stack.pop()
                # reduce the sentence and add it to stack
                reduced_sentence = self.reduce_sentence(sentence)
                stack.extend([ch for ch in reduced_sentence])
                # reset the start and cur_operator_idx index
                operators = self._find_operators_helper(stack)
                if len(operators) == 0:
                    raise Exception("error: the stack doesn't have operators")
                elif len(operators) == 1:
                    cur_operator_idx = start = operators[0][0]
                else:
                    # find the last position such that prev_str < cur_str
                    # in this case, prev_idx will be the updated start, and
                    # cur_idx will be the updated cur_operator_idx
                    for i in range(len(operators) - 2, -1, -1):
                        prev_idx, prev_str = operators[i]
                        cur_idx, cur_str = operators[i + 1]
                        if self.chart[(prev_str, cur_str)] == "=":
                            continue
                        elif self.chart[(prev_str, cur_str)] == "<":
                            start = prev_idx
                            cur_operator_idx = cur_idx
                            break
                        else:
                            raise Exception("error: operations in stack have errors. Please check. {}".format(stack))
        # judge the result
        if "".join(stack) == "#{}#".format(self.start):
            return True
        else:
            return False


if __name__ == "__main__":
    parser = OperatorPrecedenceParser()
    testcase = "test_case1.txt"
    filepath = Path(CURRENT_FILE_PATH).joinpath(DEFAULT_TESTCASE_DIR).joinpath(testcase)
    string = parser.read_file(filepath)
    print("The input string is: {}".format(string))
    res = parser.parse(filepath)
    print(res)
