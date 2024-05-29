from pathlib import Path
import re
import pathlib
from typing import Dict, List, Set, Tuple

CURRENT_FILE_PATH = pathlib.Path(__file__).parent.resolve()
DEFAULT_TESTCASE_DIR = "input"

class SLR1Parser:
    def __init__(self) -> None:
        self.start = "A"
        self.grammar: Dict[str, List[str]] = {
            "A": ["V=E"],
            "E": ["E+T", "E-T", "T"],
            "T": ["T*F", "T/F", "F"],
            "F": ["(E)", "i"],
            "V": ["i"],
        }
        self.VT: Set[str] = set()
        self.VN: Set[str] = set()
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
        if "S" in self.VN:
            raise Exception("error: cannot use 'S' as a non-terminal expression.")


if __name__ == "__main__":
    parser = SLR1Parser()
    testcase = "test_case1.txt"
    filepath = Path(CURRENT_FILE_PATH).joinpath(DEFAULT_TESTCASE_DIR).joinpath(testcase)
    string = parser.read_file(filepath)
    print("The input string is: {}".format(string))

