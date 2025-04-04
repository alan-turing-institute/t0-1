## Bugs: The subdirectory conditions/conditions should really be /conditions/mental-health

.PHONY: all

# -w 3 adds a 3 second delay between each request
all: all-conditions.txt
	echo "Information from the NHS website as at " `date` > conditions/README.txt
	wget -P conditions -x -nH --cut-dirs=1 -w 3 -i $<

# xidel extracts part of the HTML identified by an XPath locator
all-conditions.txt: www_nhs_uk-conditions.html add-url.awk
	xidel $< -e '/html/body//article/ol//ul/li/a/@href' | sort | uniq | awk -f add-url.awk - > $@

www_nhs_uk-conditions.html:
	curl "https://www.nhs.uk/conditions/" > $@
