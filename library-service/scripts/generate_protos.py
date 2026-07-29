#!/usr/bin/env python3
"""Generate Python gRPC stubs from ../proto into app/pb."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from grpc_tools import protoc

ROOT = Path(__file__).resolve().parents[1]
PROTO_DIR = ROOT.parent / "proto"
OUT_DIR = ROOT / "app" / "pb"


def main() -> int:
    if not PROTO_DIR.is_dir():
        print(f"proto directory not found: {PROTO_DIR}", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "__init__.py").touch()

    proto_files = sorted(str(p) for p in PROTO_DIR.glob("*.proto"))
    if not proto_files:
        print(f"no .proto files in {PROTO_DIR}", file=sys.stderr)
        return 1

    # Well-known types (google/protobuf/*.proto) ship with grpcio-tools.
    grpc_tools_proto = Path(protoc.__file__).resolve().parent / "_proto"

    args = [
        "grpc_tools.protoc",
        f"-I{PROTO_DIR}",
        f"-I{grpc_tools_proto}",
        f"--python_out={OUT_DIR}",
        f"--grpc_python_out={OUT_DIR}",
        *proto_files,
    ]
    code = protoc.main(args)
    if code != 0:
        return code

    _fix_imports(OUT_DIR)
    print(f"generated stubs in {OUT_DIR.relative_to(ROOT)}")
    return 0


def _fix_imports(out_dir: Path) -> None:
    """Rewrite absolute pb2 imports to package-relative (app.pb)."""
    pattern = re.compile(r"^import (\w+_pb2) as (\w+_pb2)$", re.MULTILINE)
    for path in out_dir.glob("*_pb2*.py"):
        text = path.read_text()
        updated = pattern.sub(r"from app.pb import \1 as \2", text)
        if updated != text:
            path.write_text(updated)


if __name__ == "__main__":
    raise SystemExit(main())
