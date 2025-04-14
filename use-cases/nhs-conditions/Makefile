## Instructions:
## `make download` scrapes the website; then
## `make all` makes index.txt from every index.html

.PHONY: download all

# -r             Recursively download
# -l 0           Download to arbitrary depth
# --no-parent    ... but nothing above this level
# --domains      ... and only from this domain
# --reject-regex ... ignore some weird embedded URLs
# -nH            Don't make www.nhs.uk the top-level directory of the output
# -w 2           Add a 2 second delay between each request
download:
	echo "Information from the NHS website as at" `date` > ogl-requirement.txt
	wget -r -nH -w 2 -l 0 --no-parent --no-clobber --domains www.nhs.uk --reject-regex '\\\"' https://www.nhs.uk/conditions/

htmls := $(patsubst %.html, %.txt, $(shell find conditions/ -name index.html))

all: $(htmls)

%.txt: %.html
	pandoc --to=plain -o $@ $<


## New approach:
## wget -r -nH -w 2 -l 0 --no-parent --domains www.nhs.uk https://www.nhs.uk/conditions
## NB: -nc (--no-clobber) prevents redownload of existing files
