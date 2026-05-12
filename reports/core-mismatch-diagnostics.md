# Core Mismatch Diagnostics

## Paper Target

- Edges point from defining word to defined word.
- WordNet reference from Vincent-Lamarre: `132,477` word meanings, Kernel `9,802`, Core `6,392`, Satellites `3,410`.
- Core should be the largest/source SCC inside the Kernel after the paper preprocessing.

## paper-wordnet

- Full nodes: `160010`
- Full edges: `677823`

### Original Orientation Kernel

- Kernel nodes: `12853`
- Kernel edges: `51837`
- SCC count: `3841`
- Source SCCs: `286` / `288` nodes
- Sink SCCs: `578` / `1276` nodes
- Largest SCC: `8138` nodes
- Largest SCC indegree/outdegree: `907` / `14168`
- Largest SCC is source: `False`
- Largest SCC is sink: `False`
- Top source SCC sizes: `[2, 2, 1, 1, 1, 1, 1, 1, 1, 1]`
- Top sink SCC sizes: `[6, 6, 5, 5, 5, 5, 4, 4, 4, 4]`
- Top SCC sizes: `[8138, 11, 10, 6, 6, 6, 5, 5, 5, 5]`

### Same Kernel, Reversed Orientation

- Kernel nodes: `12853`
- Kernel edges: `51837`
- SCC count: `3841`
- Source SCCs: `578` / `1276` nodes
- Sink SCCs: `286` / `288` nodes
- Largest SCC: `8138` nodes
- Largest SCC indegree/outdegree: `14168` / `907`
- Largest SCC is source: `False`
- Largest SCC is sink: `False`
- Top source SCC sizes: `[6, 6, 5, 5, 5, 5, 4, 4, 4, 4]`
- Top sink SCC sizes: `[2, 2, 1, 1, 1, 1, 1, 1, 1, 1]`
- Top SCC sizes: `[8138, 11, 10, 6, 6, 6, 5, 5, 5, 5]`

### Reversed Full Graph Kernel

- Kernel nodes: `155350`
- Kernel edges: `655992`
- SCC count: `146338`
- Source SCCs: `115492` / `115570` nodes
- Sink SCCs: `2` / `4` nodes
- Largest SCC: `8138` nodes
- Largest SCC indegree/outdegree: `438930` / `14`
- Largest SCC is source: `False`
- Largest SCC is sink: `False`
- Top source SCC sizes: `[4, 4, 3, 3, 3, 3, 3, 3, 3, 2]`
- Top sink SCC sizes: `[2, 2]`
- Top SCC sizes: `[8138, 11, 10, 6, 6, 6, 5, 5, 5, 5]`

## sense

- Full nodes: `120630`
- Full edges: `223324`

### Original Orientation Kernel

- Kernel nodes: `10430`
- Kernel edges: `23328`
- SCC count: `6335`
- Source SCCs: `1599` / `1710` nodes
- Sink SCCs: `863` / `1844` nodes
- Largest SCC: `2769` nodes
- Largest SCC indegree/outdegree: `1999` / `4164`
- Largest SCC is source: `False`
- Largest SCC is sink: `False`
- Top source SCC sizes: `[4, 4, 3, 3, 3, 2, 2, 2, 2, 2]`
- Top sink SCC sizes: `[6, 5, 5, 4, 4, 4, 4, 4, 4, 4]`
- Top SCC sizes: `[2769, 15, 11, 10, 10, 8, 8, 7, 7, 6]`

### Same Kernel, Reversed Orientation

- Kernel nodes: `10430`
- Kernel edges: `23328`
- SCC count: `6335`
- Source SCCs: `863` / `1844` nodes
- Sink SCCs: `1599` / `1710` nodes
- Largest SCC: `2769` nodes
- Largest SCC indegree/outdegree: `4164` / `1999`
- Largest SCC is source: `False`
- Largest SCC is sink: `False`
- Top source SCC sizes: `[6, 5, 5, 4, 4, 4, 4, 4, 4, 4]`
- Top sink SCC sizes: `[4, 4, 3, 3, 3, 2, 2, 2, 2, 2]`
- Top SCC sizes: `[2769, 15, 11, 10, 10, 8, 8, 7, 7, 6]`

### Reversed Full Graph Kernel

- Kernel nodes: `77109`
- Kernel edges: `147667`
- SCC count: `73014`
- Source SCCs: `51036` / `51393` nodes
- Sink SCCs: `215` / `449` nodes
- Largest SCC: `2769` nodes
- Largest SCC indegree/outdegree: `58492` / `143`
- Largest SCC is source: `False`
- Largest SCC is sink: `False`
- Top source SCC sizes: `[4, 4, 3, 3, 3, 3, 3, 3, 3, 3]`
- Top sink SCC sizes: `[4, 4, 4, 3, 3, 3, 3, 3, 3, 3]`
- Top SCC sizes: `[2769, 15, 11, 10, 10, 8, 8, 7, 7, 6]`

## Initial Verdict

- If the largest SCC is source only after reversing the same kernel, the mismatch is primarily edge-orientation terminology.
- If the largest SCC is neither source nor sink under the paper orientation, the mismatch is in preprocessing or sense/lemma mapping.
- If the reversed full graph kernel size changes radically, reversing edges is not a valid reproduction of the paper pipeline.
