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
        self.reverse_grammar: Dict[str, int] = {}
        self.VT: Set[str] = set()
        self.VN: Set[str] = set()
        self.states: Dict[int, Set[str]] = {}
        self.state_chart: Dict[Tuple[int, str], int] = {}
        self.first_dict: Dict[str, Set[str]] = {}
        self.follow_dict: Dict[str, Set[str]] = {}
        self.preprocess()
        self.get_first_set()
        self.get_follow_set()
        self.build_state_chart()

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
        # build VT and VN set
        # flatten the grammar as strings
        cnt = 0
        for key, values in self.grammar.items():
            self.VN.add(key)
            for value in values:
                string = "{}->{}".format(key, value)
                self.reverse_grammar[string] = cnt
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
                    if len(r) >= 2 and r[-1] != "e" and r[-2] in self.VN:
                        prev_len = len(self.follow_dict[r[-2]])
                        self.follow_dict[r[-2]] |= self.first_dict[r[-1]] - {"e"}
                        if len(self.follow_dict[r[-2]]) > prev_len:
                            set_updated = True
                    # rule 3.1
                    if len(r) >= 1 and r[-1] in self.VN:
                        prev_len = len(self.follow_dict[r[-1]])
                        self.follow_dict[r[-1]] |= self.follow_dict[x]
                        if len(self.follow_dict[r[-1]]) > prev_len:
                            set_updated = True
                    # rule 3.2
                    if len(r) >= 2 and r[-2] in self.VN and "e" in self.first_dict[r[-1]]:
                        prev_len = len(self.follow_dict[r[-2]])
                        self.follow_dict[r[-2]] |= self.follow_dict[x]
                        if len(self.follow_dict[r[-2]]) > prev_len:
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

    def _goto(self, state_idx: int, input: str) -> int:
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
        self.state_chart[(state_idx, input)] = total
        return total

    def _find_item_state(self, item: str) -> Optional[int]:
        for idx, items in self.states.items():
            if item in items:
                return idx
        return None

    def _build_states(self, state_idx: int) -> None:
        state: Set[str] = self.states[state_idx]
        for item in state:
            if item[-1] == ".":
                continue
            else:
                potencial_next_idx = self._find_item_state(self._get_next_item(item)[0])
                if potencial_next_idx is not None:
                    self.state_chart[(state_idx, item[item.index(".") + 1])] = potencial_next_idx
                    # add the result to self.state_chart
                else:
                    dot_idx = item.index(".")
                    next_idx = self._goto(state_idx, item[dot_idx + 1])
                    self._build_states(next_idx)

    def build_state_chart(self) -> None:
        # initialize start point
        start_item: Set[str] = self._build_initial_items(self.start)
        if start_item is None or len(start_item) != 1:
            raise Exception("error: there is an error with self.start. Please check again")
        start_closure = self._build_closure(list(start_item)[0])
        self.states[0] = start_closure
        # start loop to find all states
        self._build_states(state_idx=0)


if __name__ == "__main__":
    parser = SLR1Parser()
    testcase = "test_case1.txt"
    filepath = Path(CURRENT_FILE_PATH).joinpath(DEFAULT_TESTCASE_DIR).joinpath(testcase)
    string = parser.read_file(filepath)
    # print("The input string is: {}".format(string))
    print(len(parser.states))
    print(len(parser.state_chart))
    for (state, input), value in parser.state_chart.items():
        print("{}, {} : {}".format(state, input, value))
