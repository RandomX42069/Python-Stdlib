
import os
import sys
import shutil
import pathlib
import datetime
import re
from typing import List

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

BIT8_SIGNED_MAX = 127
BIT8_UNSIGNED_MAX = 255
BIT16_SIGNED_MAX = 32767
BIT16_UNSIGNED_MAX = 65535
BIT32_SIGNED_MAX = 2147483647
BIT32_UNSIGNED_MAX = 4294967295
BIT64_SIGNED_MAX = 9223372036854775807
BIT64_UNSIGNED_MAX = 18446744073709551615

if colorama:
    FBLACK   = colorama.Fore.BLACK
    FRED     = colorama.Fore.RED
    FGREEN   = colorama.Fore.GREEN
    FYELLOW  = colorama.Fore.YELLOW
    FBLUE    = colorama.Fore.BLUE
    FMAGENTA = colorama.Fore.MAGENTA
    FCYAN    = colorama.Fore.CYAN
    FWHITE   = colorama.Fore.WHITE
    FRESET   = colorama.Fore.RESET

    FBRIGHTBLACK   = colorama.Fore.LIGHTBLACK_EX
    FBRIGHTRED     = colorama.Fore.LIGHTRED_EX
    FBRIGHTGREEN   = colorama.Fore.LIGHTGREEN_EX
    FBRIGHTYELLOW  = colorama.Fore.LIGHTYELLOW_EX
    FBRIGHTBLUE    = colorama.Fore.LIGHTBLUE_EX
    FBRIGHTMAGENTA = colorama.Fore.LIGHTMAGENTA_EX
    FBRIGHTCYAN    = colorama.Fore.LIGHTCYAN_EX
    FBRIGHTWHITE   = colorama.Fore.LIGHTWHITE_EX

    BBLACK   = colorama.Back.BLACK
    BRED     = colorama.Back.RED
    BGREEN   = colorama.Back.GREEN
    BYELLOW  = colorama.Back.YELLOW
    BBLUE    = colorama.Back.BLUE
    BMAGENTA = colorama.Back.MAGENTA
    BCYAN    = colorama.Back.CYAN
    BWHITE   = colorama.Back.WHITE
    BRESET   = colorama.Back.RESET

    BBRIGHTBLACK   = colorama.Back.LIGHTBLACK_EX
    BBRIGHTRED     = colorama.Back.LIGHTRED_EX
    BBRIGHTGREEN   = colorama.Back.LIGHTGREEN_EX
    BBRIGHTYELLOW  = colorama.Back.LIGHTYELLOW_EX
    BBRIGHTBLUE    = colorama.Back.LIGHTBLUE_EX
    BBRIGHTMAGENTA = colorama.Back.LIGHTMAGENTA_EX
    BBRIGHTCYAN    = colorama.Back.LIGHTCYAN_EX
    BBRIGHTWHITE   = colorama.Back.LIGHTWHITE_EX

    STYLEBRIGHT = colorama.Style.BRIGHT
    STYLEDIM    = colorama.Style.DIM
    STYLERESET  = colorama.Style.RESET_ALL
else:
    FBLACK = FRED = FGREEN = FYELLOW = FBLUE = FMAGENTA = FCYAN = FWHITE = FRESET = ""
    FBRIGHTBLACK = FBRIGHTRED = FBRIGHTGREEN = FBRIGHTYELLOW = FBRIGHTBLUE = FBRIGHTMAGENTA = FBRIGHTCYAN = FBRIGHTWHITE = ""
    BBLACK = BRED = BGREEN = BYELLOW = BBLUE = BMAGENTA = BCYAN = BWHITE = BRESET = ""
    BBRIGHTBLACK = BBRIGHTRED = BBRIGHTGREEN = BBRIGHTYELLOW = BBRIGHTBLUE = BBRIGHTMAGENTA = BBRIGHTCYAN = BBRIGHTWHITE = ""
    STYLEBRIGHT = STYLEDIM = STYLERESET = ""

class AGC_GLOBAL:
    def err(self, msg: str, raiseException: bool = True):
        text = f"{FRED}[ FATAL ]: [ GLOBAL ]: {msg}{FRESET}"
        if raiseException:
            raise RuntimeError(text)
        print(text)
        sys.exit(1)

    def ok(self, msg: str):
        print(f"{FGREEN}[ OK ]: {msg}{FRESET}")

_global_err = AGC_GLOBAL()

def get_flag_value(lst: list, flag: str):
    if flag not in lst:
        return None
    idx = lst.index(flag)
    if idx + 1 >= len(lst):
        _global_err.err(f"Flag '{flag}' requires a value.")
        return None
    return lst[idx + 1]

def clear_empty_gap(lst: list):
    return [x for x in lst if x]

def cmpList(lst1: list, lst2: list) -> bool:
    if not lst1 or not lst2:
        return True
    return len(lst1) == len(lst2)

def cmpLLen(lst1: list, lst2: list) -> bool:
    return len(lst1) == len(lst2)

def ulen(lst: list) -> int:
    total = 0
    for item in lst:
        total += ulen(item) if isinstance(item, list) else 1
    return total

class filesystem:
    def __init__(self):
        self.recursiveSteps = 0
        self._glob = _global_err

    def isExistAndFile(self, path: str) -> bool:
        return pathlib.Path(os.path.abspath(path)).is_file()

    def isExistAndDir(self, path: str) -> bool:
        return pathlib.Path(os.path.abspath(path)).is_dir()

    def rmdir(self, directory: str):
        shutil.rmtree(directory, ignore_errors=True)

    def rmEachDir(self, directories: list):
        for d in directories:
            self.rmdir(d)

    def createFile(self, filename: str):
        with open(filename, "wb"):
            pass

    def createEachFile(self, files: list):
        for f in files:
            self.createFile(f)

    def mvfile(self, file: str, newdir: str):
        if not self.isExistAndFile(file):
            self._glob.err(f"File doesn't exists: {file}")
        if not self.isExistAndDir(newdir):
            self._glob.err(f"Dir doesn't exists: {newdir}")
        shutil.move(file, newdir)

    def cpyfile(self, file: str, newdir: str):
        if not self.isExistAndFile(file):
            self._glob.err(f"File doesn't exists: {file}")
        if not self.isExistAndDir(newdir):
            self._glob.err(f"Dir doesn't exists: {newdir}")
        shutil.copy(file, newdir)

    def _mode_write(self, mode: str, files: list, tdata: list):
        if not cmpLLen(files, tdata):
            self._glob.err(f"List length doesn't match: lst1: {len(files)}, lst2: {len(tdata)}")
        for path, data in zip(files, tdata):
            if mode == "ab":
                self.appendToFile(path, data)
            elif mode == "wb":
                self.writeToFile(path, data)

    def appendToFile(self, filename: str, content):
        if not self.isExistAndFile(filename):
            self._glob.err(f"File doesn't exists: {filename}")
        if not isinstance(content, (bytes, bytearray)):
            content = str(content).encode("utf-8")
        with open(filename, "ab") as f:
            f.write(content)

    def appendEachFile(self, files: list, tdata: list):
        self._mode_write("ab", files, tdata)

    def writeToFile(self, filename: str, content):
        if not self.isExistAndFile(filename):
            self._glob.err(f"File doesn't exists: {filename}")
        if not isinstance(content, (bytes, bytearray)):
            content = str(content).encode("utf-8")
        with open(filename, "wb") as f:
            f.write(content)

    def writeEachFile(self, files: list, tdata: list):
        self._mode_write("wb", files, tdata)

    def readFromFile(self, filename: str) -> bytes:
        if not self.isExistAndFile(filename):
            self._glob.err(f"File doesn't exists: {filename}")
        with open(filename, "rb") as f:
            return f.read()

    def readEachFile(self, files: list) -> list[bytes]:
        return [self.readFromFile(f) for f in files]

    def filebufferlen(self, filename: str) -> int:
        return ulen([self.readFromFile(filename)])

    def mfilesbufferlen(self, filesNames: list) -> int:
        return ulen(self.readEachFile(filesNames))

    def dirbufferlen(self, directory: str) -> int:
        if not self.isExistAndDir(directory):
            self._glob.err(f"Dir doesn't exists: {directory}")
        return ulen(self.dirlist(directory))

    def dirlist(self, directory: str) -> list[str]:
        if not self.isExistAndDir(directory):
            self._glob.err(f"Dir doesn't exists: {directory}")
        full = []
        for dp, dn, fn in os.walk(directory):
            full.extend(os.path.join(dp, name) for name in dn + fn)
        return full

    def recursiveFind(self, reserve: int = 2, fileName=None):
        target = pathlib.Path(fileName)
        reserved = []
        self.recursiveSteps = 0
        while self.recursiveSteps <= reserve:
            if self.recursiveSteps == 0:
                expanded = target
            else:
                expanded = pathlib.Path("../" * self.recursiveSteps) / target
            reserved.append(expanded)
            if expanded.is_file():
                self.recursiveSteps = 0
                return expanded
            self.recursiveSteps += 1
        self.recursiveSteps = 0
        self._glob.err(f"Reserved file paths don't exist: {reserved}")

fs = filesystem()

class clock:
    def __init__(self, stamp=None):
        self.stamp = stamp
        self.logRate = {"newborn": 86400, "normal": 360000, "ancient": 13234342342}
        self._egg_global = _global_err
        self._fs = fs

    def integerDate(self) -> int:
        return int(datetime.datetime.now().timestamp())

    def _isFar(self, t: int, override=None) -> bool:
        threshold = self.stamp if override is None else override
        return (self.integerDate() - t) > threshold

    def _filetime(self, fn: str) -> int:
        if not self._fs.isExistAndFile(fn):
            self._egg_global.err(f"File doesn't exist: {fn}")
            sys.exit(0)
        return int(os.path.getmtime(fn))

    def _ancient_log(self, fn: str, suffixes: list|tuple, threshold=None) -> bool:
        if not self._fs.isExistAndFile(fn):
            self._egg_global.err(f"File doesn't exist: {fn}")
            sys.exit(0)
        p = pathlib.Path(fn)
        if p.suffix not in suffixes:
            return False
        file_ts = self._filetime(str(p))
        return self._isFar(file_ts, override=threshold)

    def clean_directory(self, directory: str, suffixes: list|tuple, rate: str = "normal"):
        if rate not in self.logRate:
            self._egg_global.err(f"Invalid rate '{rate}', must be one of: {list(self.logRate.keys())}")
            sys.exit(1)
        age_limit = self.logRate[rate]
        if not self._fs.isExistAndDir(directory):
            self._egg_global.err(f"Directory doesn't exist: {directory}")
            sys.exit(0)
        dirpath = pathlib.Path(directory)
        deleted = scanned = 0
        for file in dirpath.iterdir():
            if not file.is_file():
                continue
            scanned += 1
            abs_path = str(file)
            if self._ancient_log(abs_path, suffixes, threshold=age_limit):
                try:
                    os.remove(abs_path)
                    deleted += 1
                    self._egg_global.ok(f"Deleted old log: {abs_path}")
                except Exception as e:
                    self._egg_global.err(f"Error deleting {abs_path}: {e}")
        return {"scanned": scanned, "deleted": deleted}

def encodeChar(char: str) -> int:
    return ord(char)

def encodeStr(string: str) -> int:
    string = string.strip()
    total = 0
    for c in string:
        total += encodeChar(c)
    return total

def encodeStrReversible(s: str) -> bytes:
    return s.encode('utf-8')

def decodeStrReversible(b: bytes) -> str:
    return b.decode('utf-8')

def encodeStrToInt(s: str) -> int:
    result = 0
    for c in s:
        result = (result << 16) | ord(c)
    return result

def decodeIntToStr(n: int) -> str:
    chars = []
    while n > 0:
        chars.append(chr(n & 0xFFFF))
        n >>= 16
    return ''.join(reversed(chars))

def encodeFixed8(s: str) -> int:
    b = s.encode("utf-8")[:8].ljust(8, b'\x00')
    return int.from_bytes(b, "little")

def decodeFixed8(n: int) -> str:
    b = n.to_bytes(8, "little")
    return b.rstrip(b'\x00').decode("utf-8")

def __glue__(filenames: List[str]) -> str:
    parts = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for fp in filenames:
        abs_fp = os.path.join(script_dir, fp)
        if fs.isExistAndFile(abs_fp):
            content = fs.readFromFile(abs_fp).decode("utf-8", errors="replace")
            parts.append(f"# src file: {abs_fp}\n{content}")
    return "\n\n".join(parts)

def __glue__package__(filenames, output="bundled.py"):
    fs.createFile(output)
    data = __glue__(filenames)
    out_dir = os.path.dirname(os.path.abspath(output))
    if out_dir and not fs.isExistAndDir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    fs.writeToFile(output, data.encode("utf-8"))

class IndexableTool:
    def get_last_occurrence(self, obj: list | str, occurrence):
        try:
            return obj.rindex(occurrence)
        except ValueError:
            return None

class pAst_if:
    def __init__(self, con: str):
        self.context = con

def doFuncWhenIfMatch(functions: list, statements: list[pAst_if]):
    if not cmpList(functions, statements):
        _global_err.err("Functions and statement cmp list return false")
    for i, each in enumerate(functions):
        if bool(eval(statements[i].context)):
            each()

def checkInstance(string: str, unallowedChars: str | list | None = None) -> bool:
    if unallowedChars is None:
        unallowedChars = "`~!@#$%^&*()-=_+}{[]:;'\"\\|<>?/.,"
    return any(c in unallowedChars for c in string)

def isInteger(inputI: str) -> bool:
    try:
        int(inputI)
        return True
    except ValueError:
        return False

def isFloat(inputF: str) -> bool:
    try:
        float(inputF)
        return not isInteger(inputF)
    except ValueError:
        return False

def isString(s) -> bool:
    return isinstance(s, str) and (
        (s.startswith('"') and s.endswith('"')) or
        (s.startswith("'") and s.endswith("'"))
    )

def isChar(inputC) -> bool:
    return isString(inputC) and len(inputC) == 3

def isBool(inputB: str) -> bool:
    return inputB.strip() in ["false", "true", "True", "False"]

def split_arg(string: str):
    pattern = r'''((?:[^,"'()\[\]]+|"[^"]*"|'[^']*'|\([^\(\)]*\)|\[[^\[\]]*\])+)'''
    return [a.strip() for a in re.findall(pattern, string.strip(), re.VERBOSE)]

class StringTool:
    def __init__(self, string: str):
        self.string = string

    def _asm_define_from_string(self):
        match self._asm_strType():
            case "str": return "db"
            case "int": return "dd"
            case "bool": return "db"
            case "float": return "dq"

    def _asm_strType(self):
        if self._is_pure_string():
            return "str"
        elif self._is_int():
            return "int"
        elif self._is_float():
            return "float"
        elif self._is_bool():
            return "bool"
        return "Unknown"

    def _asm_def(self, name):
        raw = self.string.replace("\"", "\\\"")
        db_parts = []
        i = 0
        s = raw
        while i < len(s):
            if s.startswith("\\n", i):
                db_parts.append("0x0A")
                i += 2
                continue
            if s.startswith("\\r", i):
                db_parts.append("0x0D")
                i += 2
                continue
            db_parts.append(f"'{s[i]}'")
            i += 1
        db_parts.append('0')
        return f"{name} db " + ", ".join(db_parts) + ", 0"

    def _is_bool(self):
        return self.string.lower() in ("true", "false")

    def _is_int(self):
        try:
            int(self.string)
            return True
        except Exception:
            return False

    def _is_float(self):
        if self._is_int():
            return False
        try:
            float(self.string)
            return True
        except Exception:
            return False

    def _is_pure_string(self):
        return (
            (self.string.startswith('"') and self.string.endswith('"')) or
            (self.string.startswith("'") and self.string.endswith("'"))
        )