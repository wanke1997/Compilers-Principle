from pathlib import Path
import re
import pathlib
from typing import Dict, List, Set, Tuple, Optional

CURRENT_FILE_PATH = pathlib.Path(__file__).parent.resolve()
DEFAULT_TESTCASE_DIR = "input"


class SLR1Parser:
    def __init__(self) -> None:
        self.start = "A"
        self.end = "i"
        self.grammar: Dict[str, List[str]] = {
            "A": ["V=E"],
            "E": ["E+T", "E-T", "T"],
            "T": ["T*F", "T/F", "F"],
            "F": ["(E)", "i"],
            "V": ["i"],
        }
        self.operations = {"+", "-", "*", "/"}
        # self.start = "S"
        # self.end = "i"
        # self.grammar: Dict[str, List[str]] = {
        #     "S": ["E"],
        #     "E": ["E+T", "T"],
        #     "T": ["T*F", "F"],
        #     "F": ["(E)", "i"],
        # }
        self.grammar_idx: Dict[str, int] = {}
        self.reversed_grammar: Dict[str, str] = {}
        self.VT: Set[str] = set()
        self.VN: Set[str] = set()
        self.states: Dict[int, Set[str]] = {}
        self.goto_chart: Dict[Tuple[int, str], int] = {}
        self.action_chart: Dict[Tuple[int, str], str] = {}
        self.first_dict: Dict[str, Set[str]] = {}
        self.follow_dict: Dict[str, Set[str]] = {}
        self.quad_expressions: List[str] = []
        self.quad_syntax_cnt = 0
        self.preprocess()
        self.get_first_set()
        self.get_follow_set()
        self.build_dfa()

    def read_file(self, filepath: Path) -> str:
        """
        Read file from a given filepath

        Args:
            filepath (Path): filepath given

        Returns:
            str: the parsed string read from the file
        """
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
        """
        Preprocess before parsing, including build reversed grammar, build VT and VN set,
        and flatten the grammar as strings
        """
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
        """
        Get first sets for non-terminal characters in the grammar
        """
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
        """
        Get follow sets for non-terminal characters in the grammar
        """
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
                            if ch not in self.VN or idx == len(r) - 1:
                                continue
                            else:
                                next_ch = r[idx + 1]
                                prev_len = len(self.follow_dict[ch])
                                self.follow_dict[ch] |= self.first_dict[next_ch] - {"e"}
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
                            if ch not in self.VN or idx == len(r) - 1:
                                continue
                            else:
                                next_ch = r[idx + 1]
                                if "e" in self.first_dict[next_ch]:
                                    prev_len = len(self.follow_dict[ch])
                                    self.follow_dict[ch] |= self.follow_dict[x]
                                    if len(self.follow_dict[ch]) > prev_len:
                                        set_updated = True

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
        """
        Build closure for an item given

        Args:
            item (str): item given

        Return:
            Set (str): a set of closure for item
        """
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

    def _find_state(self, target_items: Set[str]) -> Optional[int]:
        """
        Find the state index of the set given

        Args:
            target_items (Set[str]): the input set given

        Returns:
            Optional[int]: if we can find the state index, we will return the index.
            Otherwise, return None.
        """
        for idx, items in self.states.items():
            if target_items == items:
                return idx
        return None

    def _find_terminal_item(self, idx: int) -> Optional[str]:
        """
        Find an item ending with "." from a given state

        Args:
            idx (int): the index of state

        Returns:
            Optional[str]: if we can find an item ending with ".", return
            the item. Otherwise return None.
        """
        for item in self.states[idx]:
            if item[-1] == ".":
                return item
        return None

    def _find_grammar(self, idx: int) -> str:
        """
        Given the index of grammar, find the grammar sentence

        Args:
            idx (int): index given

        Returns:
            sentence from grammar
        """
        for key, value in self.grammar_idx.items():
            if value == idx:
                return key
        return ""

    def _go(self, state_idx: int) -> None:
        """
        _go method is used to build states, goto_chart, and action_chart, which are components of DFA. It
        starts from index 0, and does a recursive search to get all states and all edges for DFA.

        Args:
            state_idx (int): current state index

        """
        state: Set[str] = self.states[state_idx]
        cache: Dict[str, Set[str]] = {}
        for item in state:
            if item[-1] == ".":
                continue
            next_chr = item[item.index(".") + 1]
            next_item = self._get_next_item(item)[0]
            closure = self._build_closure(next_item)
            if next_chr in cache:
                cache[next_chr] |= closure
            else:
                cache[next_chr] = set(closure)

        for input_chr, items in cache.items():
            next_idx = self._find_state(items)
            if next_idx is None:
                next_idx = len(self.states)
                self.states[next_idx] = items
                if input_chr in self.VT:
                    self.action_chart[(state_idx, input_chr)] = "S{}".format(next_idx)
                else:
                    self.goto_chart[(state_idx, input_chr)] = next_idx
                self._go(next_idx)
            else:
                if input_chr in self.VT:
                    self.action_chart[(state_idx, input_chr)] = "S{}".format(next_idx)
                else:
                    self.goto_chart[(state_idx, input_chr)] = next_idx

    def build_dfa(self) -> None:
        """
        Entry point of building a DFA. It initialize the state index 0, then it calls _go method
        from state index 0, and then build DFA recursively.
        """
        # initialize start point
        start_item: Set[str] = self._build_initial_items(self.start)
        if start_item is None or len(start_item) != 1:
            raise Exception("error: there is an error with self.start. Please check again")
        start_closure = self._build_closure(list(start_item)[0])
        self.states[0] = start_closure
        # start loop to find all states
        self._go(state_idx=0)
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
        """
        Parse and judge the correctness of a given string

        Args:
            filepath (Path): filepath given to read

        Returns:
            bool: the correctness of the string parsed from file. If it
            is correct, return True. Otherwise, return False.
        """
        string = self.read_file(filepath) + "#"
        pt = 0
        state_stack = [0]
        sign_stack = "#"
        quad_stack: List[int] = []
        while pt < len(string):
            print("status stack: {}".format(state_stack))
            print("sign stack: {}".format(sign_stack))
            print("input string: {}".format(string[pt:]))
            cur_state = state_stack[-1]
            cur_input = string[pt]
            action = None
            try:
                action = self.action_chart[(cur_state, cur_input)]
            except Exception:
                raise Exception("error: index {} has an error with {}".format(pt, cur_input))
            if action.startswith("S"):
                if cur_input == "i":
                    quad_stack.append(self.quad_syntax_cnt)
                    self.quad_syntax_cnt += 1
                next_state = int(action[1:])
                state_stack.append(next_state)
                sign_stack += cur_input
                pt += 1
            elif action.startswith("r"):
                # 1. reduce
                idx = int(action[1:])
                terminal_item = self._find_grammar(idx)
                reduced_sentence = terminal_item.split("->")[1]
                length = len(reduced_sentence)
                sign_stack = sign_stack[: len(sign_stack) - length]
                sign_stack += terminal_item.split("->")[0]
                # 2. pop the current state
                state_stack = state_stack[: len(state_stack) - length]
                # 3. call goto to get next state
                next_state = self.goto_chart[(state_stack[-1], sign_stack[-1])]
                # 4. update the next state
                state_stack.append(next_state)
                # 5. update quad expressions
                if reduced_sentence[-1] == "i":
                    prev = quad_stack.pop()
                    quad_stack.append(self.quad_syntax_cnt)
                    self.quad_expressions.append("(=, X{}, _, X{})".format(prev, self.quad_syntax_cnt))
                    self.quad_syntax_cnt += 1
                elif len(reduced_sentence)>=2 and reduced_sentence[-2] in self.operations:
                    prev2 = quad_stack.pop()
                    prev1 = quad_stack.pop()
                    quad_stack.append(self.quad_syntax_cnt)
                    self.quad_expressions.append("({}, X{}, X{}, X{})".format(reduced_sentence[-2], prev1, prev2, self.quad_syntax_cnt))
                    self.quad_syntax_cnt += 1
                elif len(reduced_sentence)>=2 and reduced_sentence[-2] == "=":
                    prev = quad_stack.pop()
                    quad_stack.append(self.quad_syntax_cnt)
                    self.quad_expressions.append("(=, X{}, _, X{})".format(prev, self.quad_syntax_cnt))
                    self.quad_syntax_cnt += 1
            elif action == "acc":
                return True
            else:
                raise Exception("error: action {} error".format(action))
            print("#" * 30)
        return False


if __name__ == "__main__":
    parser = SLR1Parser()
    testcase = "test_case1.txt"
    filepath = Path(CURRENT_FILE_PATH).joinpath(DEFAULT_TESTCASE_DIR).joinpath(testcase)
    string = parser.read_file(filepath)
    try:
        res = parser.parse(filepath)
    except Exception as e:
        print("### {}".format(e))
        print("The expression judge result is: False")
    else:
        print("The expression judge result is: {}".format(res))
        print("#"*30)
        for expression in parser.quad_expressions:
            print(expression)
        print("The final result is stored in X{}".format(parser.quad_syntax_cnt-1))
