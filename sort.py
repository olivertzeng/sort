import os
import re

from rich.console import Console

console = Console()


def initFile(file, type):
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


def isMain(l):
    """Check if a line is a main line (starts with a number + ',')."""
    return re.match(r"^\d+,", l)


def blocked(l, n):
    noUnblock = l.split()[n] in BLOCKED or re.search(r"\([^)]*\)", l.split()[n])
    return not (l[: l.index(",")] in UNBLOCKED) and noUnblock


# Define constants
INPUT_FILE = "phrases.csv"
OUTPUT_FILE = "output.csv"
BLOCK_FILE = "blocked.txt"
UNBLOCK_FILE = "unblocked.txt"
BLOCKED = set(initFile(BLOCK_FILE, "txt") or [])
UNBLOCKED = set(initFile(UNBLOCK_FILE, "txt") or [])
BLOCK_LABEL = "峀"
NEWLINE_LABEL = "甭"
PARENTHESIS_LABEL = "刂"
DEBUG = True
x = 1


def check(lines):
    for i, l in enumerate(lines):
        phrase = l.split(",")[0].replace(PARENTHESIS_LABEL, " ")
        if (
            set(re.sub(r"\([^)]*\)", "", phrase).split()) <= set(BLOCKED)
            and not phrase in UNBLOCKED
        ):
            console.print(
                f"You currently have a conflicting phrase [bold red]{phrase}[/bold red] on line [bold red]{i+1}[/bold red], append it to [bold red]{UNBLOCK_FILE}"
            )
            promptInProccess = True
            while promptInProccess:
                if os.path.exists(UNBLOCK_FILE):
                    console.print(
                        f"[bold green]==> [Y]Append to list[/bold green] [N]Abort [S]Show the culprit line"
                    )
                else:
                    console.print(
                        f"[bold green]==> [Y]Touch {UNBLOCK_FILE} and append to list[/bold green] [N]Abort [S]Show the culprit line"
                    )
                response = console.input("[bold green]==> ")
                if response.lower() == "n":
                    console.print("Phrase not appended, aborting.")
                    quit()
                elif response.lower() == "s":
                    console.print(l)
                else:
                    with open(UNBLOCK_FILE, "a") as f:
                        f.write(phrase + "\n")
                    console.print(f"Phrase appended to [bold red]{UNBLOCK_FILE}")
                    promptInProccess = False


def group(lines):
    result = []
    mainLine = None
    for l in lines:
        if isMain(l):
            if mainLine:
                result.append(mainLine)
            mainLine = l
        else:
            if mainLine:
                mainLine += NEWLINE_LABEL + l
    if mainLine:
        result.append(mainLine)
    for i, l in enumerate(result):
        result[i] = l[l.index(",") + 1 :]
    return result


def block(lines):
    """Add block labels until the nth word isn't blocked."""
    n = 0
    for i, l in enumerate(lines):
        """Group parenthesis into a single word(setup)"""
        if "(" in l and ")" in l:
            # find the substring within the parenthesis
            start_idx = l.find("(")
            end_idx = l.find(")")

            # replace extra spaces within the parenthesis
            substring = re.sub(r"\s+", PARENTHESIS_LABEL, l[start_idx + 1 : end_idx])

            # replace the original substring with the modified one
            lines[i] = l[: start_idx + 1] + substring + l[end_idx:]
    for i, l in enumerate(lines):
        lines[i] = l.replace('"', '" ')

    while True:
        """the main proccess"""
        allBlocked = True
        for i, l in enumerate(lines):
            if blocked(l, n):
                allBlocked = False
                break
        if allBlocked:
            break
        for i, l in enumerate(lines):
            if not blocked(l, n):
                lines[i] = BLOCK_LABEL + " " + l
        n += 1
    console.print("iterated " + str(n) + " times")
    return n, lines


def label(lines):
    """Add line numbers to each line."""
    return [f"{i+1},{l}" for i, l in enumerate(lines)]


def restore(lines, buf):
    """Remove labels"""
    result = []
    for l in lines:
        l = l.replace(BLOCK_LABEL + " ", "")
        l = l.replace(PARENTHESIS_LABEL, " ")
        l = l.replace(NEWLINE_LABEL, "\n")
        l = l.replace('" ', '"')
        result.append(l)
    result = buf + result
    return result


def write_to_file(file, lines, debug=True):
    """Write the given lines to a new csv file."""
    with open(file, "w", newline="") as f_out:
        for l in lines:
            f_out.write(l + "\n")
    if debug:
        console.log(f"[bold yellow]DEBUG: [/bold yellow]Lines written to {file}")
    else:
        console.log(f"Lines written to {file}")


def process_file(input_file, output_file):
    """Process the input file and write to the output file."""
    with open(input_file, "r") as f_in:
        buf = []
        lines = f_in.readlines()
        buf = lines[:x]
        lines = [line.strip() for line in lines[x:]]
        if DEBUG and not os.path.exists("debug"):
            os.mkdir("debug")
        console.log("cleaning complete")
        if DEBUG:
            write_to_file("debug/cleaned.csv", lines)

        lines = group(lines)
        console.log("grouping complete")
        if DEBUG:
            write_to_file("debug/grouped.csv", lines)

        check(lines)
        n, lines = block(lines)
        console.log("blocking complete")
        if DEBUG:
            write_to_file("debug/blocked.csv", lines)

        lines = sorted(lines, key=lambda x: x.split()[n].lower().strip())
        console.log("sorting complete")
        if DEBUG:
            write_to_file("debug/sorted.csv", lines)

        lines = label(lines)
        console.log("labeling complete")
        if DEBUG:
            write_to_file("debug/labeled.csv", lines)

        lines = restore(lines, buf)
        console.log("restoring complete")
        write_to_file(output_file, lines, False)
        console.log("task complete")


process_file(initFile(INPUT_FILE, "csv"), OUTPUT_FILE)
