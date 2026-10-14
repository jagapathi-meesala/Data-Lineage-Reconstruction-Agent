# Explainability

## Inputs
The agent consumes user-supplied SQL statements, explicit pipeline dependency pairs, and optional known assets. It does not connect to external systems.

## Decision
Recognized SQL patterns and explicit dependency pairs become candidate source-to-target edges. Each edge records origin and evidence. Impact analysis traverses only supplied or reconstructed edges.

## Limits
Parsing is heuristic and may miss dynamic SQL, macros, stored procedures, dialect-specific syntax, alias resolution, and external orchestration dependencies. Outputs are not authoritative lineage.

## Tool: extract-lineage
### Inputs and Data Sources
SQL statements, explicit dependency pairs, and optional asset inventory supplied in the request.
### Decision and Reasoning
Recognized SQL references are connected to detected targets; explicit dependency pairs are preserved as supplied evidence.
### Outputs and Evidence
Returns edges, evidence snippets, origin, warnings, and unresolved assets.
### Limits and Constraints
Does not execute SQL or connect to catalogs; parsing is pattern-based.
### Failure Handling
Malformed entries are skipped with warnings where possible; invalid top-level input returns a clear error.
### Human Review
Verify edge direction and object names against query history, orchestration configuration, and the catalog.

## Tool: analyze-impact
### Inputs and Data Sources
A graph of source-to-target edges and a requested asset identifier.
### Decision and Reasoning
Traverses reverse edges for upstream dependencies and forward edges for downstream dependencies.
### Outputs and Evidence
Returns upstream, downstream, and direct dependents.
### Limits and Constraints
Impact is limited to edges present in the supplied graph.
### Failure Handling
Missing assets return empty traversal and an existence flag.
### Human Review
Confirm freshness and conditional dependencies before relying on impact results.

## Tool: validate-lineage
### Inputs and Data Sources
Lineage edges and optional known asset inventory.
### Decision and Reasoning
Checks endpoint quality, duplicates, unknown references, and directed cycles.
### Outputs and Evidence
Returns findings and a validity summary.
### Limits and Constraints
Cycles may be legitimate in iterative pipelines; incomplete inventories may create false unknown-asset findings.
### Failure Handling
Malformed edges become findings when possible.
### Human Review
Review severe findings and determine whether cycles are expected.
