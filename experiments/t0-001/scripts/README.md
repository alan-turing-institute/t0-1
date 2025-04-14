# Readme

Overview of various scripts

## Script to download all NHS condition web pages

This script downloads each page from the NHS A-Z website
https://www.nhs.uk/conditions

Information on that website is subject to the [NHS terms and
conditions](https://www.nhs.uk/our-policies/terms-and-conditions/)
and, in particular, is released under the [Open Government
License](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

### Output structure

A list of directories, named by the condition, possibly containing
nested subdirectories. Each directory and subdirectory contains an
html file, `index.html`, describing the condition.

Top level:

- `robots.txt`
- `conditions/`
- `live-well/`
- `nhs-services/`
- `pregnancy/`
- `static/`
