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

## What is the actual task?

There seem to be three possibilities but it is very unclear to me at
present which we are trying to do. In all three tasks: (a) the model
is presented with a prompt describing a set of "symptoms" as
experienced by an imaginary "patient"; and (b) we have available a set
of documents, each describing a particular medical condition, which
act as a proxy for a private knowledge base. It seems to me that the
possible tasks are:

1. We want the model to return (pointers to) a small set of
   _documents_ describing conditions that are relevant given the
   "patient's" symptoms. The user is being guided towards the
   appropriate information, but the information itself is
   authoritative and we don't do anything with it. We could in this
   case simply return some web links.
   
2. We want the model to suggest one or more _conditions_ (perhaps with
   reasons!). In this task, presumably the conditions are to be
   thought of as _keywords_ into the private knowledge base, which the
   user may then search themselves.
   
3. We want the model to suggest one or more conditions, together with
   a course of action for the supposed "patient" to follow.
   
Not all of these tasks work if what we are trying to do is proxy
a use-case that is LLM-mediated search into a private knowledge base. 










## Evaluation

In outline: 
1. Generate a set of example queries, each of which a set of symptoms
   from a condition, perhaps with “noise;”
2. Ask the model to find conditions which match these symptoms.
3. Evaluate the 




