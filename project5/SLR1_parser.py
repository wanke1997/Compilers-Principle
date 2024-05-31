from pathlib import Path
import re
import pathlib
from typing import Dict, List, Set, Tuple

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
        self.VT: Set[str] = set()
        self.VN: Set[str] = set()
        self.states: Dict[int, List[str]] = {}
        self.preprocess()

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
        for key, values in self.grammar.items():
            self.VN.add(key)
            for value in values:
                for ch in value:
                    if ch.isupper():
                        self.VN.add(ch)
                    else:
                        self.VT.add(ch)
    
    def build_initial_items(self, left: str) -> Set[str]:
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
            if key!=left:
                continue
            else:
                for value in values:
                    s = "{}->.{}".format(key,value)
                    res.add(s)
        return res
    
    def get_next_item(self, item: str) -> Tuple[str, str]:
        """
        Move the dot forward by 1 position. For example, if the input is
        A->B.*C, then the output will be A->B*.C

        Args:
            item (str): the item sentence provided
        
        Returns:
            Tuple[str, str]: the item sentence whose dot is moved forward by 1 position, 
            and the last read character

        """
        if item is None or len(item)<=2:
            raise Exception("error: the input item has issues.")
        if item.count(".")>1:
            raise Exception("error: the number of dot in the item {} is greater than 1. ".format(item))
        split_res = item.split(".")
        if split_res[1] is None or len(split_res[1])==0:
            return item
        else:
            read = split_res[0]+split_res[1][:1]
            todo = split_res[1][1:]
            res = read+"."+todo
            return res, read[-1]
    
    def build_closure(self, item: str) -> Set[str]:
        res: Set[str] = set()
        res.add(item)
        idx = item.index(".")
        if idx+1 == len(item):
            return res
        elif item[idx+1] in self.VT or item.split("->")[0] == item[idx+1]:
            return res
        else:
            next_items = self.build_initial_items(item[idx+1])
            res |= next_items
            for next_item in next_items:
                res |= self.build_closure(next_item)
            return res


    # def build_closure_state(self, state_idx: int) -> Set[str]:
    #     items: Set[str] = set()
    #     state: Set[str] = self.states[state_idx]
    #     items |= state
    #     for item in state:
    #         items |= self.build_closure(item)
    #     self.states[state_idx] = items
    #     return items
    
    def go(self, state_idx: int, input: str) -> int:
        state: Set[str] = self.states[state_idx]
        total = len(self.states)
        items: Set[str] = set()
        for item in state:
            next_item, last_chr = self.get_next_item(item)
            if last_chr == input:
                items.add(next_item)
                next_item_closure = self.build_closure(next_item)
                items |= next_item_closure
        self.states[total] = items
        return total


if __name__ == "__main__":
    parser = SLR1Parser()
    testcase = "test_case1.txt"
    filepath = Path(CURRENT_FILE_PATH).joinpath(DEFAULT_TESTCASE_DIR).joinpath(testcase)
    string = parser.read_file(filepath)
    print("The input string is: {}".format(string))

    item = "E->E+.T"
    parser.states[0] = parser.build_closure(item)
    next_state_idx = parser.go(0, "T")
    print(next_state_idx, parser.states[next_state_idx])
