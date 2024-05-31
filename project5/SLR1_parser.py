from pathlib import Path
import re
import pathlib
from typing import Dict, List, Set, Tuple, Optional

CURRENT_FILE_PATH = pathlib.Path(__file__).parent.resolve()
DEFAULT_TESTCASE_DIR = "input"


class SLR1Parser:
    def __init__(self) -> None:
        # self.start = "A"
        # self.grammar: Dict[str, List[str]] = {
        #     "A": ["V=E"],
        #     "E": ["E+T", "E-T", "T"],
        #     "T": ["T*F", "T/F", "F"],
        #     "F": ["(E)", "i"],
        #     "V": ["i"],
        # }
        self.start = "S"
        self.grammar: Dict[str, List[str]] = {
            "S": ["E"],
            "E": ["E+T", "T"],
            "T": ["T*F", "F"],
            "F": ["(E)", "i"],
        }
        self.grammar_idx: Dict[str, int] = {}
        self.reversed_grammar: Dict[str, str] = {}
        self.VT: Set[str] = set()
        self.VN: Set[str] = set()
        self.states: Dict[int, Set[str]] = {}
        self.goto_chart: Dict[Tuple[int, str], int] = {}
        self.action_chart: Dict[Tuple[int, str], str] = {}
        self.first_dict: Dict[str, Set[str]] = {}
        self.follow_dict: Dict[str, Set[str]] = {}
        self.preprocess()
        self.get_first_set()
        self.get_follow_set()
        self.build_dfa()

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
        # flatten the grammar as strings
        cnt = 0
        self.VT.add("#")
        for key, values in self.grammar.items():
            self.VN.add(key)
            for value in values:
                string = "{}->{}".format(key, value)
                self.grammar_idx[string] = cnt
                cnt += 1
                for ch in value:
                    if ch.isupper():
                        self.VN.add(ch)
                    else:
                        self.VT.add(ch)

    def get_first_set(self) -> None:
        self.first_dict = {s: set() for s in (self.VT | self.VN)}
        # 1. calculate first set for terminals
        for x in self.VT:
            self.first_dict[x].add(x)
        # 2. calculate first set for x->aX, which a is a terminal
        for x, right in self.grammar.items():
            for r in right:
                if r[0] in self.VT:
                    self.first_dict[x].add(r[0])
        # 3. calculate first set for normal cases
        set_updated = True
        while set_updated:
            set_updated = False
            for x, right in self.grammar.items():
                if x in self.VT:
                    continue
                for r in right:
                    if r[0] in self.VT:
                        continue
                    # rule 3.1
                    prev_len = len(self.first_dict[x])
                    self.first_dict[x] |= self.first_dict[r[0]] - {"e"}
                    if len(self.first_dict[x]) > prev_len:
                        set_updated = True
                    # rule 3.2
                    for i in range(1, len(r)):
                        if r[i - 1] not in self.VN or "e" not in self.first_dict[r[i - 1]]:
                            break
                        else:
                            prev_len = len(self.first_dict[x])
                            self.first_dict[x] |= self.first_dict[r[i]] - {"e"}
                            if len(self.first_dict[x]) > prev_len:
                                set_updated = True
                    # rule 3.3
                    add_e = sum([1 if r[i] in self.VN and "e" in self.first_dict[r[i]] else 0 for i in range(len(r))]) == len(r)
                    if add_e == True:
                        prev_len = len(self.first_dict[x])
                        self.first_dict[x].add("e")
                        if len(self.first_dict[x]) > prev_len:
                            set_updated = True

    def get_follow_set(self) -> None:
        self.follow_dict = {s: set() for s in (self.VN)}
        # rule 1
        self.follow_dict[self.start].add("#")
        # rule 2 and rule 3 iteration
        set_updated = True
        while set_updated:
            set_updated = False
            for x, right in self.grammar.items():
                if x not in self.VN:
                    continue
                for r in right:
                    # rule 2
                    if len(r) >= 2:
                        for idx, ch in enumerate(r):
                            if ch not in self.VN or idx==len(r)-1:
                                continue
                            else:
                                next_ch = r[idx+1]
                                prev_len = len(self.follow_dict[ch])
                                self.follow_dict[ch] |= (self.first_dict[next_ch]-{"e"})
                                if len(self.follow_dict[ch]) > prev_len:
                                    set_updated = True
                    # rule 3.1
                    if len(r) >= 1 and r[-1] in self.VN:
                        prev_len = len(self.follow_dict[r[-1]])
                        self.follow_dict[r[-1]] |= self.follow_dict[x]
                        if len(self.follow_dict[r[-1]]) > prev_len:
                            set_updated = True
                    # rule 3.2
                    if len(r) >= 2:
                        for idx, ch in enumerate(r):
                            if ch not in self.VN or idx==len(r)-1:
                                continue
                            else:
                                next_ch = r[idx+1]
                                if "e" in self.first_dict[next_ch]:
                                    prev_len = len(self.follow_dict[ch])
                                    self.follow_dict[ch] |= self.follow_dict[x]
                                    if len(self.follow_dict[ch]) > prev_len:
                                        set_updated = True
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

    def _build_initial_items(self, left: str) -> Set[str]:
        """
        Build an initial item set such as A->.B, which the left part is provided, and the
        position of dot is set to initial state on the right part of the sentence.

        Args:
            left (str): the left side of the sentence, such as S, E, F, T, etc

        Returns:
            Set (str): a set of initial items whose left part is $left variable

        """
        res: Set[str] = set()
        for key, values in self.grammar.items():
            if key != left:
                continue
            else:
                for value in values:
                    s = "{}->.{}".format(key, value)
                    res.add(s)
        return res

    def _get_next_item(self, item: str) -> Tuple[str, str]:
        """
        Move the dot forward by 1 position. For example, if the input is
        A->B.*C, then the output will be A->B*.C

        Args:
            item (str): the item sentence provided

        Returns:
            Tuple[str, str]: the item sentence whose dot is moved forward by 1 position,
            and the last read character

        """
        if item is None or len(item) <= 2:
            raise Exception("error: the input item has issues.")
        if item.count(".") > 1:
            raise Exception("error: the number of dot in the item {} is greater than 1. ".format(item))
        split_res = item.split(".")
        if split_res[1] is None or len(split_res[1]) == 0:
            return item, ""
        else:
            read = split_res[0] + split_res[1][:1]
            todo = split_res[1][1:]
            res = read + "." + todo
            return res, read[-1]

    def _build_closure(self, item: str) -> Set[str]:
        res: Set[str] = set()
        res.add(item)
        idx = item.index(".")
        if idx + 1 == len(item):
            return res
        elif item[idx + 1] in self.VT or item.split("->")[0] == item[idx + 1]:
            return res
        else:
            next_items = self._build_initial_items(item[idx + 1])
            res |= next_items
            for next_item in next_items:
                res |= self._build_closure(next_item)
            return res

    def _go(self, state_idx: int, input: str) -> int:
        state: Set[str] = self.states[state_idx]
        total = len(self.states)
        items: Set[str] = set()
        for item in state:
            next_item, last_chr = self._get_next_item(item)
            if last_chr == input:
                items.add(next_item)
                next_item_closure = self._build_closure(next_item)
                items |= next_item_closure
        self.states[total] = items
        if input in self.VN:
            print("####", str((state_idx, input)), str(total))
            self.goto_chart[(state_idx, input)] = total
        else:
            self.action_chart[(state_idx, input)] = "S{}".format(total)
        return total

    def _find_item_state(self, item: str) -> Optional[int]:
        for idx, items in self.states.items():
            if item in items:
                return idx
        return None
    
    def _find_terminal_item(self, idx: int) -> Optional[str]:
        for item in self.states[idx]:
            if item[-1] == ".":
                return item
        return None

    def _find_grammar(self, idx: int) -> str:
        for key, value in self.grammar_idx.items():
            if value == idx:
                return key
        return ""
    
    # def _find_set_index(self, dict: Dict[str, Set[str]], next_chr: str) -> Optional[int]:
    #     set = dict[next_chr]


    def _build_states(self, state_idx: int) -> None:
        state: Set[str] = self.states[state_idx]
        # dict: Dict[str, Set[str]] = {}
        # for item in state:
        #     next_chr = item[item.index(".") + 1]
        #     next_item = self._get_next_item(item)[0]
        #     if next_chr in dict:
        #         dict[next_chr].add(next_item)
        #     else:
        #         dict[next_chr] = {next_item}

        for item in state:
            if item[-1] == ".":
                continue
            else:
                next_chr = item[item.index(".") + 1]
                potencial_next_idx = self._find_item_state(self._get_next_item(item)[0])
                if potencial_next_idx is not None:
                    
                    if next_chr in self.VN:
                        print("####", str((state_idx, input)), str(potencial_next_idx))
                        self.goto_chart[(state_idx, next_chr)] = potencial_next_idx
                    else:
                        self.action_chart[(state_idx, next_chr)] = "S{}".format(potencial_next_idx)
                else:
                    dot_idx = item.index(".")
                    next_idx = self._go(state_idx, item[dot_idx + 1])
                    self._build_states(next_idx)

    def build_dfa(self) -> None:
        # initialize start point
        start_item: Set[str] = self._build_initial_items(self.start)
        if start_item is None or len(start_item) != 1:
            raise Exception("error: there is an error with self.start. Please check again")
        start_closure = self._build_closure(list(start_item)[0])
        self.states[0] = start_closure
        # start loop to find all states
        self._build_states(state_idx=0)
        for idx in range(len(self.states)):
            T_item = self._find_terminal_item(idx)
            if T_item is None:
                continue
            left = T_item.split("->")[0]
            for a in self.follow_dict[left]:
                r_idx = self.grammar_idx[T_item[:-1]]
                self.action_chart[(idx, a)] = "r{}".format(r_idx)
            if left == self.start:
                self.action_chart[(idx, "#")] = "acc"

    def parse(self, filepath: Path) -> bool:
        string = self.read_file(filepath) + "#"
        pt = 0
        state_stack = [0]
        sign_stack = "#"
        while pt < len(string):
            print("status stack: {}".format(state_stack))
            print("sign stack: {}".format(sign_stack))
            print("input string: {}".format(string[pt:]))
            cur_state = state_stack[-1]
            cur_input = string[pt]
            action = self.action_chart[(cur_state, cur_input)]
            if action.startswith("S"):
                next_state = int(action[1:])
                state_stack.append(next_state)
                sign_stack += cur_input
                pt += 1
            elif action.startswith("r"):
                # 1. reduce
                idx = int(action[1:])
                terminal_item = self._find_grammar(idx)
                length = len(terminal_item.split("->")[1])
                sign_stack = sign_stack[:len(sign_stack)-length]
                sign_stack += terminal_item.split("->")[0]
                # 2. pop the current state
                state_stack = state_stack[:len(state_stack)-length]
                # 3. call goto to get next state
                next_state = self.goto_chart[(state_stack[-1], sign_stack[-1])]
                # 4. update the next state
                state_stack.append(next_state)
            elif action == "acc":
                return True
            else:
                raise Exception("error: action {} error".format(action))
            print("#"*30)
        return False


if __name__ == "__main__":
    parser = SLR1Parser()
    testcase = "test_case1.txt"
    filepath = Path(CURRENT_FILE_PATH).joinpath(DEFAULT_TESTCASE_DIR).joinpath(testcase)
    string = parser.read_file(filepath)
    # for key, value in parser.action_chart.items():
    #     print(key, value)
    # for key, value in parser.goto_chart.items():
    #     print(key, value)
    for key, value in parser.states.items():
        print(key, value)
    res = parser.parse(filepath)
    print(res)