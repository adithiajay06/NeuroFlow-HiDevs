POST /pipelines → validate config, insert new pipeline version.

GET /pipelines → list all pipelines with last‑run metrics.

GET /pipelines/{id} → full config + aggregate evaluation scores.

PATCH /pipelines/{id} → create new version, preserve old.

DELETE /pipelines/{id} → soft delete (status="archived").
