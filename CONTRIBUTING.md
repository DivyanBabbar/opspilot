# Contributing

Add or update tests when changing anomaly thresholds, incident transitions, or action gating. Explain any change that alters response behavior. Do not include real telemetry, credentials, or infrastructure identifiers in examples.

Run `pip install -e '.[dev]'`, `ruff check .`, and `pytest` before submitting. Changes that introduce a real executor require a threat model, least-privilege design, dry-run path, audit events, and explicit approval semantics.
