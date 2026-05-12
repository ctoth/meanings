# Abstract

## Original Text (Verbatim)

We present OpenGloss, a synthetic encyclopedic dictionary and semantic knowledge graph for English that integrates lexicographic definitions, encyclopedic context, etymological histories, and semantic relationships in a unified resource. OpenGloss contains 537K senses across 150K lexemes, on par with WordNet 3.1 and Open English WordNet, while providing more than four times as many sense definitions. These lexemes include 9.1M semantic edges, 1M usage examples, 3M collocations, and 60M words of encyclopedic content.

Generated through a multi-agent procedural generation pipeline with schema-validated LLM outputs and automated quality assurance, the entire resource was produced in under one week for under $1,000. This demonstrates that structured generation can create comprehensive lexical resources at cost and time scales impractical for manual curation, enabling rapid iteration as foundation models improve. The resource addresses gaps in pedagogical applications by providing integrated content -- definitions, examples, collocations, encyclopedias, etymology -- that supports both vocabulary learning and natural language processing tasks.

As a synthetically generated resource, OpenGloss reflects both the capabilities and limitations of current foundation models. The dataset is publicly available on Hugging Face under CC-BY 4.0, enabling researchers and educators to build upon and adapt this resource.

---

## Our Interpretation

This paper is about scalable lexical-resource generation, not semantic minimality. Its value for this project is that it gives a large new typed lexical graph that could be mined, compared, or stress-tested for kernel structure once we are ready to go beyond WordNet-style resources.
