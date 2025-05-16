import os
import re

from rich.console import Console

console = Console()


class sortLib:
    def __init__(self, block_file, unblock_file, ceec_file, debug):
        self.BLOCK_FILE = block_file
        self.UNBLOCK_FILE = unblock_file
        self.CEEC_FILE = ceec_file
        self.BLOCKED = self.init_file(block_file, "txt") or set()
        self.UNBLOCKED = self.init_file(unblock_file, "txt") or set()
        self.CEEC = self.init_file(ceec_file, "txt") or set()
        self.BLOCK_LABEL = "峀"
        self.NEWLINE_LABEL = "甭"
        self.PARENTHESIS_LABEL = "刂"
        self.DEBUG = debug

    def init_file(self, file, type):
        if type == "csv":
            try:
                open(file, "r").close()
            except FileNotFoundError:
                console.print(
                    f"[bold red]CRITICAL ERROR[/bold red]: {file} not found. Aborting"
                )
                quit()
            return file

        elif type == "txt":
            if os.path.exists(file):
                with open(file, "r") as f:
                    return set([line.strip() for line in f.readlines()])
            else:
                console.print(f"[bold yellow]Warning[/bold yellow]: {file} not found.")
                return set()

    def is_main(self, l):
        return re.match(r"^\d+,", l)

    def blocked(self, l, n):
        no_unblock = l.split()[n] in self.BLOCKED or re.search(
            r"\([^)]*\)", l.split()[n]
        )
        return not (l[: l.index(",")] in self.UNBLOCKED) and no_unblock

    def check(self, lines):
        for i, l in enumerate(lines):
            phrase = l.split(",")[0].replace(self.PARENTHESIS_LABEL, " ")
            if (
                set(re.sub(r"\([^)]*\)", "", phrase).split()) <= self.BLOCKED
                and phrase not in self.UNBLOCKED
            ):
                console.print(
                    f"You currently have a conflicting phrase [bold red]{phrase}[/bold red] on line [bold red]{i+1}[/bold red], append it to [bold red]{self.UNBLOCK_FILE}"
                )
                prompt_in_process = True
                while prompt_in_process:
                    if os.path.exists(self.UNBLOCK_FILE):
                        console.print(
                            f"[bold green]==> [Y]Append to list[/bold green] [N]Abort [S]Show the culprit line"
                        )
                    else:
                        console.print(
                            f"[bold green]==> [Y]Touch {self.UNBLOCK_FILE} and append to list[/bold green] [N]Abort [S]Show the culprit line"
                        )
                    response = console.input("[bold green]==> ")
                    if response.lower() == "n":
                        console.print("Phrase not appended, aborting.")
                        quit()
                    elif response.lower() == "s":
                        console.print(l)
                    else:
                        with open(self.UNBLOCK_FILE, "a") as f:
                            f.write(phrase + "\n")
                        console.print(
                            f"Phrase appended to [bold red]{self.UNBLOCK_FILE}"
                        )
                        prompt_in_process = False

    def group(self, lines):
        result = []
        main_line = None
        for l in lines:
            if self.is_main(l):
                if main_line:
                    result.append(main_line)
                main_line = l
            else:
                if main_line:
                    main_line += self.NEWLINE_LABEL + l
        if main_line:
            result.append(main_line)
        for i, l in enumerate(result):
            result[i] = l[l.index(",") + 1 :]
        if self.DEBUG:
            self.writeToFile("../debug/grouped.csv", lines)
        return result

    def block(self, lines):
        n = 0
        for i, l in enumerate(lines):
            if "(" in l and ")" in l:
                start_idx = l.find("(")
                end_idx = l.find(")")
                substring = re.sub(
                    r"\s+", self.PARENTHESIS_LABEL, l[start_idx + 1 : end_idx]
                )
                lines[i] = l[: start_idx + 1] + substring + l[end_idx:]
        for i, l in enumerate(lines):
            lines[i] = l.replace('"', '" ')
        while True:
            all_blocked = True
            for i, l in enumerate(lines):
                if self.blocked(l, n):
                    all_blocked = False
                    break
            if all_blocked:
                break
            for i, l in enumerate(lines):
                if not self.blocked(l, n):
                    lines[i] = self.BLOCK_LABEL + " " + l
            n += 1
        if self.DEBUG:
            console.log(
                "[bold yellow]DEBUG: [/bold yellow]iterated " + str(n) + " times"
            )
            self.writeToFile("../debug/blocked.csv", lines)

        return n, lines

    def label(self, lines):
        return [f"{i+1},{l}" for i, l in enumerate(lines)]

    def restore(self, lines, buf):
        result = []
        for l in lines:
            l = l.replace(self.BLOCK_LABEL + " ", "")
            l = l.replace(self.PARENTHESIS_LABEL, " ")
            # l = l.replace(self.NEWLINE_LABEL, "\n")
            l = l.replace('" ', '"')
            result.append(l)
        result = buf + result
        console.log("restoring complete")
        return result

    def sortc(self, lines, n):
        lines = sorted(lines, key=lambda x: x.split()[n].lower().strip())
        if self.DEBUG:
            self.writeToFile("../debug/sorted.csv", lines)
        return lines

    def process(self, input_lines):
        lines = [line.strip() for line in input_lines]
        if self.DEBUG and not os.path.exists("debug"):
            os.mkdir("debug")
        # lines = self.group(self.label(lines))
        self.check(lines)
        n, lines = self.block(lines)
        lines = self.sortc(lines, n)
        lines = self.restore(lines, [])
        return lines

    def writeToFile(self, file, lines, newline=True):
        with open(file, "w") as f_out:
            for l in lines:
                f_out.write(l + ("\n" if newline else ""))
