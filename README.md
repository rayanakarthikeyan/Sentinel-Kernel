# Sentinel-Kernel: remediation workflow prototype

A Python/FastAPI demonstration of incident states, an isolated temporary
workspace, a reproduction test, a fixed patch template and post-mortem output.
It is an educational prototype, not an autonomous production SRE service.

## What is implemented

- Keyword-based severity and stack-trace filename extraction.
- A test for one demonstration `handle_request` interface.
- A gate requiring a failing assertion before a patch can be proposed.
- A fixed replacement function, followed by a repeat of the reproduction test.
- Missing source, passing reproductions, unrelated failures and timeouts escalate.

No LLM synthesizes patches. Existing application regression suites are not run.
Passing this one test does not prove a patch preserves business behavior.
The temporary directory and subprocess timeout are not a security sandbox:
only run trusted local fixture code. There is no network or OS isolation.
No zero-hallucination, production-safety or MTTR improvement claim is made.

```sh
pip install -e .
python -m unittest discover -s tests
uvicorn sentinel.server.app:app --host 127.0.0.1 --port 8000
```

The sample API alert has no source tree and correctly escalates. The test suite
supplies a deliberately failing trusted fixture to demonstrate the patch loop.
Before real use, add context-specific patch generation, full regression tests,
human approval and genuinely isolated execution infrastructure.
