from pathlib import Path
import pathlib
from typing import Dict, Optional, List, Tuple

CURRENT_FILE_PATH = pathlib.Path(__file__).parent.resolve()
DEFAULT_TESTCASE_DIR = "input"

class Parser:
    def __init__(self, filepath: str) -> None:
        # index 0 is for spaces, "\t", or "\n"
        # index 1 is for digits
        self.offset = 2
        self.spaces = {" ", "\n", "\t"}
        signs = ["<", "=", ">", "/", "!", "*", "(", ")", "[", "]", "{", "}", ":", "+", "-", ";", "#"]
        self.signs = set(signs)
        reserved_words = ["void", "int", "float", "double", "string", "if", "else", "for", "do", "while", "printf", "include", "stdio.h"]
        self.reserved_words = set(reserved_words)

        self.encode_dict: Dict[str, int] = {}
        for idx, sign in enumerate(signs):
            self.encode_dict[sign] = idx+self.offset
        
        for idx, reserved_word in enumerate(reserved_words):
            self.encode_dict[reserved_word] = idx+self.offset+len(signs)
        
        f = open(filepath, "r")
        self.string = f.read()
        f.close()

    
    def parse_helper(self, s: str) -> Optional[int]:
        if s in self.spaces:
            return 0
        elif s.isdigit():
            return 1
        else:
            if s in self.encode_dict:
                return self.encode_dict[s]
            else:
                if self.is_valid(s):
                    return self.offset+len(self.signs)+len(self.reserved_words)
                else:
                    return None
    
    def is_valid(self, s: str) -> bool:
        if len(s) == 0:
            return False
        else:
            if not s[0].isalpha() and s[0]!="_":
                return False
            else:
                for ch in s:
                    if not ch.isalpha() and not ch.isdigit() and ch!="_":
                        return False
                return True
    
    def parse(self) -> Optional[List[Tuple[int, str]]]:
        result = []
        length = len(self.string)
        idx = 0
        count_parentheses = 0
        count_bracket = 0
        count_curly_bracket = 0
        
        while idx < length:
            substring = self.string[idx:]
            # ignore comments in the program
            if substring.startswith("//") or substring.startswith("/*"):
                if substring.startswith("//"):
                    idx += 2
                    while idx<length and self.string[idx]!="\n":
                        idx += 1
                else:
                    idx += 2
                    while idx<length and not self.string[idx:].startswith("*/"):
                        idx += 1
                    if self.string[idx:].startswith("*/"):
                        idx += 2
                    else:
                        return None
            else:
                # parse operation signs
                if self.string[idx] in self.signs or self.string[idx] in self.spaces:
                    category = self.parse_helper(self.string[idx])
                    if category is None:
                        raise Exception("There is an error")
                    if category != 0:
                        result.append((category, self.string[idx]))
                    # Parentheses matching check
                    if self.string[idx] == "(":
                        count_parentheses += 1
                    elif self.string[idx] == ")":
                        count_parentheses -= 1
                    elif self.string[idx] == "[":
                        count_bracket += 1
                    elif self.string[idx] == "]":
                        count_bracket -= 1
                    elif self.string[idx] == "{":
                        count_curly_bracket += 1
                    elif self.string[idx] == "}":
                        count_curly_bracket -= 1
                    idx += 1
                # parse one number
                elif self.string[idx].isdigit():
                    digit_buffer = ""
                    while idx < length and self.string[idx].isdigit():
                        digit_buffer += self.string[idx]
                        idx += 1
                    category = self.parse_helper(digit_buffer)
                    if category is not None:
                        result.append((category, digit_buffer))
                    else:
                        raise Exception("There is an error")
                # check reserved words and general variables
                else:
                    has_reserved_word = False
                    # every iteration only parses one reserved word
                    for reserved_word in self.reserved_words:
                        if substring.startswith(reserved_word):
                            has_reserved_word = True
                            category = self.parse_helper(reserved_word)
                            if category is not None:
                                result.append((category, reserved_word))
                            else:
                                raise Exception("There is an error")
                            idx += len(reserved_word)
                            break
                    # parse general variables
                    if not has_reserved_word:
                        variable_buffer = ""
                        while idx<len(self.string) and self.string[idx] not in self.spaces and self.string[idx] not in self.signs:
                            variable_buffer += self.string[idx]
                            idx += 1
                        category = self.parse_helper(variable_buffer)
                        if category is not None:
                            result.append((category, variable_buffer))
                        else:
                            raise Exception("There is an error")
        
        if count_bracket!=0 or count_curly_bracket!= 0 or count_parentheses!=0:
            raise Exception("error: parentheses do not match")
        else:
            return result

if __name__ == "__main__":
    testcase = "test_case1.txt"

    filepath = Path(CURRENT_FILE_PATH).joinpath(DEFAULT_TESTCASE_DIR).joinpath(testcase)
    parser = Parser(filepath=filepath)
    result = parser.parse()
    if result is not None:
        result_file = str(filepath).split(".")[-2]+"_result.txt"
        f = open(result_file, "w")
        for res in result:
            f.write(str(res)+"\n")
        f.close()
    else:
        print("There is an error. ")