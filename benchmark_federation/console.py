from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from benchmark_federation.federation import Application, load_review, run, verify


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog='benchmark_federation', description='多国人工智能评测基准互认验证台')
    commands = root.add_subparsers(dest="command", required=True)
    execute = commands.add_parser("run")
    execute.add_argument("--fixture", required=True)
    execute.add_argument("--database", required=True)
    execute.add_argument("--output", required=True)
    execute.add_argument("--review", help="optional JSON comparability review (baseline, mappings, policy, observations)")
    check = commands.add_parser("verify")
    check.add_argument("--database", required=True)
    check.add_argument("--output", required=True)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--database", required=True)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "run":
        review = load_review(args.review) if args.review else None
        result = run(args.fixture, args.database, args.output, review=review)
    elif args.command == "verify":
        result = verify(args.database, args.output)
    else:
        result = Application(args.database).inspect()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
