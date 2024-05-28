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
        self.string = ""

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

if __name__ == "__main__":
    parser = OperatorPrecedenceParser()
    testcase = "test_case1.txt"
    filepath = Path(CURRENT_FILE_PATH).joinpath(DEFAULT_TESTCASE_DIR).joinpath(testcase)
    parser.read_file(filepath)
    print(parser.string)