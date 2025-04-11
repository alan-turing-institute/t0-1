import os
import tqdm
from bs4 import BeautifulSoup
import json

# path to the condition folder (download them from sharepoint or scrape them again)
conditions_folder = "../nhs-use-case/v2/conditions/"

def convert_html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    main_element = soup.find("main", class_="nhsuk-main-wrapper")
    try:
        # Extract the text from the main element
        conditions_content = main_element.get_text(separator="\n", strip=True)

        # Remove last reviewed date
        conditions_content = conditions_content.split("\nPage last reviewed:")[0]
    except AttributeError:
        return None
    return conditions_content   

def parse_downloaded_conditions(conditions_folder, selected_condition):

    # skip if selected_condition is not a folder
    if not os.path.isdir(os.path.join(conditions_folder, selected_condition)):
        print(f"Condition {selected_condition} is not a folder")
        return None

    text = []

    if "index.html" in os.listdir(
        os.path.join(conditions_folder, selected_condition)
    ):
        content = open(
            os.path.join(conditions_folder, selected_condition, "index.html"), "r"
        ).read()

        conditions_content = convert_html_to_text(content)

        if conditions_content is not None:
            text.append(conditions_content)


    for folder in os.listdir(
        os.path.join(conditions_folder, selected_condition)
    ):
        if not os.path.isdir(os.path.join(conditions_folder, selected_condition, folder)):
            continue
        # skip if index.html is not in the folder
        if "index.html" not in os.listdir(
            os.path.join(conditions_folder, selected_condition, folder)
        ):
            continue
        content = open(
            os.path.join(conditions_folder, selected_condition, folder, "index.html"), "r"
        ).read()
        conditions_content = convert_html_to_text(content)
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

#save the output to a jsonl file
output_folder = "../data/nhs-conditions/"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

with open(
    os.path.join(output_folder, "conditions.jsonl"), "w", encoding="utf-8") as f:
    for condition in all_conditions_content:
        f.write(json.dumps(condition) + "\n")