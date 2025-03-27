# RAG for NHS conditions

## Background

### Idea

Our idea is to demonstrate the use of a “small” model (small enough to
run “locally”) in retrieving information from a private knowledge
base, which is imagined to consist of a set of documents. Our
hypothesis is that this is a challenge faced by civil servants in
retrieving material from their department's knowledge management
system.

The proposal here is to use the contents of https://nhs.uk/conditions
as a “private knowledge base” and to fine-tune a “small” model to
query that knowledge base. Very roughly:

(a) The model is presented with a prompt describing a set of
    "symptoms" as experienced by an imaginary "patient"; and 
	
(b) We have available a set of documents, each describing a particular
    medical condition, which act as a proxy for a private knowledge
    base. 
	
(c) The model returns “something useful.”

### What is the actual task?

There seem to be three possibilities but it is very unclear to me at
present which one we are trying to do. They are:

1. Document retrieval;
2. Knowledge retrieval;
3. Decision support.

It seems to me that the possible tasks are:

1. **Document retrieval** The model should return (pointers to) a
   small set of _documents_ describing conditions that are relevant
   given the “patient's” symptoms. The user is being guided towards
   the appropriate information, but the information itself is
   authoritative and we don't do anything with it. (We could in this
   case simply return some web links.)
   
2. The model should suggest one or more _conditions_ (perhaps with
   reasons). In this task, the conditions are perhaps to be thought of
   as _keywords_ into the private knowledge base, which the user may
   then search themselves.
   
3. We want the model to suggest one or more conditions, together with
   a course of action for the supposed "patient" to follow. That is,
   it is to do domain-specific decision-support, based on the decision
   processes described in the private knowledge base.
   
Not all of these tasks work if what we are trying to do is proxy a
use-case that is LLM-mediated search into a private knowledge base.

### Why is this important?

Task (3) -- decision support -- is not what we were originally trying
to proxy. We should explicitly decide if that's what we're going with. 

Task (1) might not even need an LLM. As I understand RAG, one
typically computes a vector embedding for each document and for the
search query, then does a lookup via vector similarity. We could just
do that, no LLM required. Actually, we *should* do that, as a
benchmark.

Task (2) is closest to "searching a private knowledge base"


## Task: `nhs-01`

### Test set

1. Randomly generate a list of conditions from the NHS 1000
2. For each, ask a large model to generate a description of the
   symptoms of an imaginary patient with that condition.

### Evaluation

Each of three possible metrics:

1. Generate a predicted condition. Score 1 for correct, 0 for
   incorrect.
2. Generate a probability distibution over all conditions in the
   NHS 1000. Score the log-likelihood of the actual answer.
3. Generate a list of 3 (or 5) possible conditions. Score 1 if that
   list contains the correct condition, 0 otherwise.
   






	
