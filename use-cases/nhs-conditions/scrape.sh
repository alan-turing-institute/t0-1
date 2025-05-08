echo "Information from the NHS website as at" `date` > ogl-requirement.txt

# There are multiple pages we need to check
URLS=(
    "https://www.nhs.uk/conditions/"
    "https://www.nhs.uk/medicines/"
    "https://www.nhs.uk/tests-and-treatments/"
    "https://www.nhs.uk/symptoms"
)

CONDITIONS=()
for URL in "${URLS[@]}"; do
  ENTRIES=$(curl -sL "$URL" \
    | grep -E '<a href="/conditions/.+/">' \
    | cut -d'/' -f3)
  CONDITIONS+=($ENTRIES)
done

CONDITIONS=($(printf "%s\n" "${CONDITIONS[@]}" | sort -u))

for i in "${CONDITIONS[@]}"; do
    # -r             Recursively download
    # -l 0           Download to arbitrary depth
    # --no-parent    ... but nothing above this level
    # --domains      ... and only from this domain
    # --reject-regex ... ignore some weird embedded URLs
    # -nv            Be less verbose
    # -nH            Don't make www.nhs.uk the top-level directory of the output
    # -w X           Add an X second delay between each request
    wget -r -nv -nH -w 0.1 -l 0 --no-parent --no-clobber --domains www.nhs.uk --reject-regex '\\\"' "https://www.nhs.uk/conditions/${i}/"
done
