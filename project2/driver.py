from pathlib import Path
import pathlib
from typing import Dict
import re

CURRENT_FILE_PATH = pathlib.Path(__file__).parent.resolve()
DEFAULT_TESTCASE_DIR = "input"


class RecursiveParser:
    def __init__(self, filepath: Path) -> None:
        self.read_file(filepath)
        self.cache: Dict[str, bool] = {}
    
    def read_file(self, filepath: Path) -> None:
        f = open(filepath, "r")
        self.string = ""
        pattern = r"'[^']*'"
        read_string = f.readline()
        while read_string:
            match_string = re.findall(pattern, read_string)[0]
            if match_string is not None:
                self.string += match_string[1 : len(match_string) - 1]
            read_string = f.readline()
        f.close()

    def A(self) -> bool:
        s = self.string
        if s is None or len(s) == 0:
            return False
        elif "=" in s and s.count("=") == 1:
            idx = s.index("=")
            res1 = self.V(s[:idx])
            res2 = self.E(s[idx + 1 :])
            return res1 and res2
        else:
            return False

    def A_quote(self, s: str) -> bool:
        if s in self.cache:
            return self.cache[s]
        if s is None or len(s) == 0:
            return False
        elif s == "+" or s == "-":
            self.cache[s] = True
            return True
        else:
            return False

    def E(self, s: str) -> bool:
        if s in self.cache:
            return self.cache[s]
        if s is None or len(s) == 0:
            return False
        for idx in range(0, len(s) + 1):
            res1 = self.T(s[:idx])
            res2 = self.E_quote(s[idx:])
            if res1 and res2:
                self.cache[s] = True
                return True
        return False

    def E_quote(self, s: str) -> bool:
        if s in self.cache:
            return self.cache[s]
        if s is None or len(s) == 0:
            return True
        s1 = s[:1]
        res1 = self.A_quote(s1)
        for idx in range(1, len(s) + 1):
            res2 = self.T(s[1:idx])
            res3 = self.E_quote(s[idx:])
            if res1 and res2 and res3:
                self.cache[s] = True
                return True
        return False

    def F(self, s: str) -> bool:
        if s in self.cache:
            return self.cache[s]
        if s is None or len(s) == 0:
            return False
        elif s == "i":
            self.cache[s] = True
            return True
        elif s[0] == "(" and s[-1] == ")":
            substring = s[1:-1]
            return self.E(substring)

    def M(self, s: str) -> bool:
        if s in self.cache:
            return self.cache[s]
        if s is None or len(s) == 0:
            return False
        elif s == "*" or s == "/":
            self.cache[s] = True
            return True
        else:
            return False

    def T(self, s: str) -> bool:
        if s in self.cache:
            return self.cache[s]
        if s is None or len(s) == 0:
            return False
        for idx in range(0, len(s) + 1):
            res1 = self.F(s[:idx])
            res2 = self.T_quote(s[idx:])
            if res1 and res2:
                self.cache[s] = True
                return True
        return False

    def T_quote(self, s: str) -> bool:
        if s in self.cache:
            return self.cache[s]
        if s is None or len(s) == 0:
            return True
        res1 = self.M(s[:1])
        for idx in range(1, len(s) + 1):
            res2 = self.F(s[1:idx])
            res3 = self.T_quote(s[idx:])
            if res1 and res2 and res3:
                self.cache[s] = True
                return True
        return False

    def V(self, s: str) -> bool:
        if s in self.cache:
            return self.cache[s]
        if s is None or len(s) == 0:
            return False
        elif s == "i":
            self.cache[s] = True
            return True
        else:
            return False


if __name__ == "__main__":
    testcase = "test_case1.txt"

    filepath = Path(CURRENT_FILE_PATH).joinpath(DEFAULT_TESTCASE_DIR).joinpath(testcase)
    recursive_parser = RecursiveParser(filepath)
    print(recursive_parser.string)
    result = recursive_parser.A()
    print("result is {}.".format(result))
