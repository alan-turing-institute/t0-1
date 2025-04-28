import json
import os

import regex as re
import tqdm

# path to the condition folder (download them from sharepoint or scrape them again)
conditions_folder = "data/nhs-conditions/conditions/"


def remove_further_information(text):
    """
    Removes "Further information" headers followed by bullet points from a string.
    """
    pattern = r"Further information\s*\n(- .+\n)+"
    return re.sub(pattern, "", text)


def remove_contents_section(text):
    """
    Removes "Contents" headers followed by a numbered list from a string.
    """
    pattern = r"Contents\s*\n(\d+\.\s+.+\n)+"
    return re.sub(pattern, "", text)


def clean_bullet_points(text):
    """
    Cleans up bullet points in the text by ensuring they are formatted correctly.
    """
    pattern = r"-\s*\[]\s*\n\s*(\S.+)"
    replacement = r"- \1"

    return re.sub(pattern, replacement, text)


def clean_bullet_points_2(text):
    """
    Replace "- [ ]" with "- " in the text.
    """
    pattern = r"-\s*\[\s*\]\s*"
    replacement = r"- "

    return re.sub(pattern, replacement, text)


def convert_simple_tables_in_text(text):
    """
    Identifies and converts text-based tables (in pandoc's simple_table format:
    https://pandoc.org/MANUAL.html#extension-simple_tables) within a larger text to a
    bulleted list format.
    """
    lines = text.split("\n")
    output_lines = []
    in_table = False
    table_lines = []

    def process_table(table_lines):
        """
        Processes a list of lines representing a table and converts
        it to a bulleted list format.
        """
        if not table_lines or len(table_lines) < 2:
            return []

        header_line = table_lines[0].strip()
        headers = [h.strip() for h in re.split(r"\s{2,}", header_line)]
        if len(headers) < 2:
            return []

        converted = [f"{headers[0]} | {headers[1]}"]
        data_lines = table_lines[2:]

        for line in data_lines:
            line = line.strip()
            if line:
                parts = [p.strip() for p in re.split(r"\s{2,}", line, maxsplit=1)]
                if len(parts) == 2:
                    converted.append(f"- {parts[0]} | {parts[1]}")

        return converted

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # heuristic to detect the start of a potential table:
        # line with multiple words separated by significant space
        if re.search(r"\w+\s{2,}\w+", line) and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            # followed by a line containing mostly hyphens and spaces
            if re.fullmatch(r"[\s-]+", next_line):
                in_table = True
                table_lines = [line, next_line]
                i += 2  # skip the header and separator
                while i < len(lines):
                    data_line = lines[i].strip()
                    # words or word+end bracket followed by multiple spaces and then more words
                    if re.search(r"(\w+|\w+\))\s{2,}\w+", data_line) or not data_line:
                        table_lines.append(data_line)
                        i += 1
                    else:
                        # end of the potential table
                        converted_table = process_table(table_lines)
                        output_lines.extend(converted_table)
                        in_table = False
                        break

                if in_table:
                    # handle table ending at the end of the text
                    converted_table = process_table(table_lines)
                    output_lines.extend(converted_table)
                    in_table = False
                continue

        output_lines.append(line)
        i += 1

    return "\n".join(output_lines)


def convert_grid_tables_in_text(text):
    """
    Identifies and converts text-based tables (in pandoc's grid_tables format:
    https://pandoc.org/MANUAL.html#extension-grid_tables) within a larger text to a
    bulleted list format.
    """
    lines = text.strip().splitlines()

    def extract_table_rows(table_lines):
        """
        Extracts data rows from a list of strings representing a table.
        """
        rows = []
        current_row_items = []
        collecting_multiline = False

        for line in table_lines:
            if line.startswith("+") and line.endswith("+"):
                if current_row_items:
                    rows.append([item.strip() for item in current_row_items])
                    current_row_items = []
                collecting_multiline = False
                continue

            parts = [part.strip() for part in line.strip("|").split("|")]

            if not collecting_multiline:
                current_row_items = parts
                # check if the row spans multiple lines
                if any(len(part) > 0 for part in parts):
                    collecting_multiline = True
            else:
                # append non-empty parts to the corresponding previous items
                for i, part in enumerate(parts):
                    if part:
                        if i < len(current_row_items):
                            current_row_items[i] += " " + part
                        else:
                            # handle cases where a multiline row has more columns in subsequent lines
                            current_row_items.append(part)

        # handle the last row if the table doesn't end with a separator
        if current_row_items:
            rows.append([item.strip() for item in current_row_items])

        return rows

    def parse_text_table(table_lines):
        """
        Parses a text table and converts it to a bulleted list format.
        """
        rows = extract_table_rows(table_lines)
        if not rows:
            return ""

        headers = rows[0]
        parsed_items = rows[1:]
        output = " | ".join(headers) + "\n"
        for row in parsed_items:
            output += "- " + " | ".join(row) + "\n"

        return output.strip()

    text = []
    table_lines = []
    # iterate through the lines of the text and add them to the text list
    # if they are not part of a table, just append to the text list
    # if they are part of a table, build up table_lines list to be processed
    # if we end a table, process the table_lines and add output to the text list
    # if we reach another table, start a new table_lines list
    for line in lines:
        if line.startswith("+") or line.startswith("|"):
            table_lines.append(line)
        else:
            if table_lines:
                # process the table lines
                output = parse_text_table(table_lines)
                if output:
                    text.append(output)
                text.append(output)
                table_lines = []

            text.append(line)

    # process any remaining table lines
    if table_lines:
        output = parse_text_table(table_lines)
        if output:
            text.append(output)

    return "\n".join(text)


def normalise_dash_spacing(text):
    """
    Normalises whitespace around hyphens in a string.
    """
    return re.sub(r"([ \t]{2,})-[ \t]*| [ \t]*-[ \t]{2,}", " - ", text)


def normalise_newlines(text):
    """
    Replaces three or more consecutive newlines with exactly two newlines.
    """
    return re.sub(r"\n{3,}", "\n\n", text)


def strip_whitespace_around_newlines(text):
    """
    Strips leading and trailing whitespace around newline characters in a string.
    """
    lines = text.split("\n")
    stripped_lines = [line.strip() for line in lines]
    return "\n".join(stripped_lines)


def clean_text(text):
    # remove page last reviewed date
    text = text.split("\nPage last reviewed:")[0]
    text = text.split("\nDate reviewed")[0]
    text = text.split("\nLast reviewed:")[0]

    # remove media last reviewed date
    text = text.split("\nMedia last reviewed:")[0]

    # some pages have "Further information" followed by some bullet points starting with "-"
    # remove them but keep the text before and after with regex
    text = remove_further_information(text)

    # some pages has "Contents" followed by a numbered list
    # remove them but keep the text before and after with regex
    text = remove_contents_section(text)

    # some pages have bullet points starting with "- [ ]" but have a lot of unnecessary spaces
    # clean them up with regex
    text = clean_bullet_points(text)
    text = clean_bullet_points_2(text)

    # some pages have tables in the text but they can be converted to a bulleted list
    # some are formatted as a simple_table (https://pandoc.org/MANUAL.html#extension-simple_tables)
    text = convert_simple_tables_in_text(text)
    # some are formatted as a grid_table (https://pandoc.org/MANUAL.html#extension-grid_tables)
    text = convert_grid_tables_in_text(text)

    # some headings have a lot of unnecessary spaces before and after the dash
    # clean them up with regex
    text = normalise_dash_spacing(text)

    # some pages have a lot of unnecessary newlines
    # clean them up with regex
    text = normalise_newlines(text)

    # some pages have a lot of unnecessary spaces before and after the newlines
    # clean them up with regex
    text = strip_whitespace_around_newlines(text)

    return text


def parse_downloaded_conditions(conditions_folder, selected_condition):
    specific_folder = os.path.join(conditions_folder, selected_condition)

    # skip if selected_condition is not a folder
    if not os.path.isdir(specific_folder):
        print(f"Condition {selected_condition} is not a folder")
        return None

    text = []

    if "index.txt" in os.listdir(specific_folder):
        filename = os.path.join(specific_folder, "index.txt")
        with open(filename, "r") as f:
            conditions_content = f.read()
            if conditions_content is None:
                print(f"{filename} does not have content")
            else:
                conditions_content = clean_text(conditions_content)

        if conditions_content is not None:
            text.append(conditions_content)

    for folder in os.listdir(specific_folder):
        specific_subfolder = os.path.join(conditions_folder, selected_condition, folder)
        if not os.path.isdir(specific_subfolder):
            continue
        # skip if index.txt is not in the folder
        if "index.txt" not in os.listdir(specific_subfolder):
            continue
        filename = os.path.join(specific_subfolder, "index.txt")
        with open(filename, "r") as f:
            conditions_content = f.read()
            if conditions_content is None:
                print(f"{filename} does not have content")
            else:
                conditions_content = clean_text(conditions_content)

        if conditions_content is not None:
            text.append(conditions_content)

    if len(text) == 0:
        print(f"Condition {selected_condition} does not have content")
        return None

    # join the text
    conditions_content = "\n".join(text)
    return conditions_content


# create a pandas dataframe with condition title and converted text
all_conditions_content = []

for condition in tqdm.tqdm(os.listdir(conditions_folder)):
    conditions_content = parse_downloaded_conditions(conditions_folder, condition)
    if conditions_content is not None:
        all_conditions_content.append(
            {
                "condition_title": condition,
                "condition_content": conditions_content,
            }
        )

# save the output to a jsonl file
output_folder = "data/nhs-conditions/"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

with open(os.path.join(output_folder, "conditions.jsonl"), "w", encoding="utf-8") as f:
    for condition in all_conditions_content:
        f.write(json.dumps(condition) + "\n")
