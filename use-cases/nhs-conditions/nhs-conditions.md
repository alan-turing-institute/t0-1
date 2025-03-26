# RAG for NHS conditions

## Overview

Our challenge is to demonstrate the use of a “small” model (small
enough to run “locally”) in retrieving information from a private
knowledge base consisting of a set of documents. Our hypothesis is
that this is a challenge faced by civil servants in retrieving
material from their department's knowledge management system. 

Our proposal is to use the contents of https://nhs.uk/conditions as a
“private knowledge base” and to fine-tune a “small” model to query
that knowledge base.

## Evaluation

In outline: 
1. Generate a set of example queries, each of which a set of symptoms
   from a condition, perhaps with “noise;”
2. Ask the model to find conditions which match these symptoms.
3. Evaluate the 




