## Instructions:
## `make download` scrapes the website; then
## `make all` makes index.txt from every index.html
## `make clean` deletes all the created .txt files

.PHONY: download all

download:
	bash scrape.sh

htmls := $(patsubst %.html, %.txt, $(shell find conditions/ -name index.html))

all: $(htmls)

%.txt: %.html
	pandoc --to=plain --wrap=none -o $@ $<

# make clean deletes all the .txt files
clean:
	rm -f $(htmls)

## New approach:
## wget -r -nH -w 2 -l 0 --no-parent --domains www.nhs.uk https://www.nhs.uk/conditions
## NB: -nc (--no-clobber) prevents redownload of existing files
