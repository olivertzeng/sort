import os
import re

from rich.console import Console

c = Console()


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
        if self.DEBUG and not os.path.exists("debug"):
            os.mkdir("debug")

    def init_file(self, file, type):
        if type == "csv":
            try:
                open(file, "r").close()
            except FileNotFoundError as e:
                c.print(
                    f"[bold red]CRITICAL ERROR[/bold red]: {file} not found. Aborting"
                )
                quit()
            return file

        elif type == "txt":
            if os.path.exists(file):
                with open(file, "r") as f:
                    return set([line.strip() for line in f.readlines()])
            else:
                c.print(f"[bold yellow]Warning[/bold yellow]: {file} not found.")
                return set()

    def is_main(self, l):
        return re.match(r"^\d+,", l)

    def blocked(self, l, n):
        no_unblock = l.split()[n] in self.BLOCKED or re.search(
            r"\([^)]*\)", l.split()[n]
        )
        return not (l[: l.index(",")] in self.UNBLOCKED) and no_unblock

    def is_ceec(self, phrase):
        return phrase in self.CEEC

    def check(self, lines, remainder, cat):
        noPhrase = False
        for i, l in enumerate(lines):
            phrase = l[: l.index(",")].replace(self.PARENTHESIS_LABEL, " ")
            if (
                set(re.sub(r"\([^)]*\)", "", phrase).split()) <= self.BLOCKED
                and phrase not in self.UNBLOCKED
            ):
                if phrase == None or re.match(r"^\s*$", phrase):
                    c.print(
                        f"[bold red]ERROR:[/bold red] phrase not found on line [bold red]{remainder+i+2}[/bold red]\n[bold yellow]{l}[/bold yellow] in category {cat}"
                    )
                    noPhrase = True
                else:
                    c.print(
                        f"You currently have a conflicting phrase [bold red]{phrase}[/bold red] on line [bold red]{remainder+i+2}[/bold red] in category {cat}, do you want to append it to [bold red]{self.UNBLOCK_FILE}"
                    )
                prompt_in_process = True
                while prompt_in_process:
                    if os.path.exists(self.UNBLOCK_FILE):
                        c.print(
                            f"[bold green]==> [Y]Append to list[/bold green] [N]Abort [S]Show the culprit line"
                        )
                    else:
                        c.print(
                            f"[bold green]==> [Y]Touch {self.UNBLOCK_FILE} and append to list[/bold green] [N/Q]Abort [S]Show the culprit line"
                        )
                    response = c.input("[bold green]==> ")
                    if response.lower() == "n" or response.lower() == "q":
                        c.print("Phrase not appended, aborting.")
                        quit()
                    elif response.lower() == "s":
                        c.print(l)
                    else:
                        with open(self.UNBLOCK_FILE, "a") as f:
                            f.write(phrase + "\n")
                        c.print(f"Phrase appended to [bold red]{self.UNBLOCK_FILE}")
                        prompt_in_process = False
        if noPhrase:
            c.print(
                f"[bold red]ERROR: [/bold red][red]Some phrases were missing, aborting."
            )

    def removeLineNumbers(self, lines):
        for i, l in enumerate(lines):
            lines[i] = l[l.index(",") + 1 :]
        return lines

    def group(self, lines, cat):
        result = []
        main_line = None
        for l in lines:
            if self.is_main(l):
                if main_line:
                    result.append(main_line)
                main_line = l
            else:
                main_line = main_line + l
            # elif main_line:
            #         main_line += self.NEWLINE_LABEL + l
        if main_line:
            result.append(main_line)
        result = self.removeLineNumbers(result)
        if self.DEBUG:
            self.writeToFile(f"debug/grouped{cat}.csv", result)
        return result

    def block(self, lines, cat):
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
            c.log(
                f"[bold yellow]DEBUG: [/bold yellow]iterated {n} times in category {cat}"
            )
            self.writeToFile(f"debug/blocked{cat}.csv", lines)

        return n, lines

    def labelLineNumbers(self, lines):
        return [f"{i+1},{l}" for i, l in enumerate(lines)]

    def sortc(self, lines, n, cat):
        lines = sorted(lines, key=lambda x: x.split()[n].lower().strip())
        if self.DEBUG:
            self.writeToFile(f"debug/sorted{cat}.csv", lines)
        return lines

    def restore(self, lines, cat):
        result = []
        for l in lines:
            l = l.replace(self.BLOCK_LABEL + " ", "")
            l = l.replace(self.PARENTHESIS_LABEL, " ")
            # l = l.replace(self.NEWLINE_LABEL, "\n")
            l = l.replace('" ', '"')
            result.append(l)
        c.log("restoring complete")
        if self.DEBUG:
            self.writeToFile(f"debug/restored{cat}.csv", result)
        return result

    def labelCeec(self, lines, cat):
        for i, l in enumerate(lines):
            phrase = l[: l.index(",")]
            if self.is_ceec(phrase):
                if self.DEBUG:
                    c.log(
                        f"[bold yellow]DEBUG: [/bold yellow]Found CEEC phrase {phrase} in category {cat}"
                    )
                lines[i] = "★ " + phrase + " ★" + l[l.index(",") :]

        return lines

    def process(self, ilines, remainder, cat):
        lines = [line.strip() for line in ilines]
        self.check(lines, remainder, cat)
        n, lines = self.block(lines, cat)
        lines = self.sortc(lines, n, cat)
        lines = self.restore(lines, cat)
        lines = self.labelCeec(lines, cat)
        lines = self.labelLineNumbers(lines)
        if self.DEBUG:
            self.writeToFile(f"debug/output{cat}.csv", lines)
        return lines, remainder + len(ilines)

    def writeToFile(self, file, lines, newline=True):
        with open(file, "w") as f_out:
            for l in lines:
                f_out.write(l + ("\n" if newline else ""))
