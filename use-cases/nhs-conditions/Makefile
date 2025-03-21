all: all-conditions.txt

# xidel extracts part of the HTML identified by an XPath locator 
all-conditions.txt: www_nhs_uk-conditions.html
	xidel $< -e '/html/body//article/ol//ul/li/a/@href' | uniq > $@

www_nhs_uk-conditions.html:
	curl "https://www.nhs.uk/conditions/" > $@ 

