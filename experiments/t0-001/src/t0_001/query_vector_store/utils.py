import logging
import os
from pathlib import Path

from bs4 import BeautifulSoup
from tqdm import tqdm


def remove_saved_directory(path: str | Path, directory_name: str) -> None:
    if path is None:
        return
    if os.path.exists(path):
        # remove the existing directory if it exists
        logging.info(f"Found existing directory at '{path}'. Attempting to remove...")
        confirm = input(
            f"Are you sure you want to remove the existing directory at '{path}'? (y/n): "
        )

        while confirm.lower() not in ("y", "yes", "n", "no"):
            confirm = input("Invalid input. Please enter 'y'/'yes' or 'n'/'no': ")

        if confirm.lower() not in ("y", "yes"):
            raise ValueError(
                f"For force_create=True, {directory_name} is passed and the directory exists. Please remove it first."
            )

        import shutil

        shutil.rmtree(path)

        logging.info(f"Removed existing directory at '{path}'.")


def load_conditions(
    conditions_folder: str | Path,
    main_only: bool = True,
    max_conditions: int | None = None,
) -> dict[str, str]:
    """
    Load the conditions from the folder and extract the text from the HTML files
    from the scraped NHS website.

    Parameters
    ----------
    conditions_folder : str | Path
        Path to the folder containing the conditions. This should be a folder where
        each sub-folder is a condition and contains an index.html file. For example:
        if conditions_folder = "nhs-use-case/conditions", then the folder should look like this:
        - nhs-use-case/conditions/condition1/index.html
        - nhs-use-case/conditions/condition2/index.html
        ...
    main_only : bool, optional
        If True, only the main element of the HTML file is extracted with class "nhsuk-main-wrapper".
        If False, the whole HTML file is extracted. The default is True.

    max_conditions : int | None, optional
        The maximum number of conditions to load. If None, all conditions are loaded.
        The default is None.

    Returns
    -------
    dict[str, str]
        A dictionary where the keys are the names of the conditions and the values
        are the text extracted from the HTML files. For example:
        {
            "condition1": "text from condition1",
            "condition2": "text from condition2",
            ...
        }

    Raises
    ------
    ValueError
        If the conditions_folder does not exist or is not a folder.
    """
    # check if the folder exists
    if not os.path.exists(conditions_folder):
        raise ValueError(f"Folder {conditions_folder} does not exist")

    logging.info(f"Loading conditions from {conditions_folder}")

    # read all conditions and put them in a list
    conditions = {}
    max_conditions = max_conditions or len(os.listdir(conditions_folder))
    for condition in tqdm(os.listdir(conditions_folder)[:max_conditions]):
        try:
            content = open(
                os.path.join(conditions_folder, condition, "index.html"), "r"
            ).read()
            conditions[condition] = parse_condition_html_page(
                content=content, main_only=main_only
            )
        except Exception as e:
            print(f"Error reading condition {condition}: {e}")
            continue

    return conditions


def parse_condition_html_page(content: str, main_only: bool = True) -> str:
    """TODO: Make this more robust."""
    soup = BeautifulSoup(content, "html.parser")
    if main_only:
        # extract the main element
        main_element = soup.find("main", class_="nhsuk-main-wrapper")
        # extract the text from the main element
        text = main_element.get_text(separator="\n", strip=True)
    else:
        text = soup.get_text(separator="\n", strip=True)
    return text
