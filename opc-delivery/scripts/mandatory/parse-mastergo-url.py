#!/usr/bin/env python3
"""Parse MasterGo URLs into MCP-ready identifiers."""

from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import parse_qs, unquote, urlparse


def parse_mastergo_url(url: str) -> dict[str, str]:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    file_match = re.search(r"/file/([^/?#]+)", parsed.path)
    raw_file = (
        [file_match.group(1)]
        if file_match
        else query.get("file") or query.get("fileId") or query.get("file_id")
    )
    if not raw_file:
        raise ValueError("Could not extract fileId from /file/<id> path or file= query parameter.")

    raw_layer = (
        query.get("layer_id")
        or query.get("layerId")
        or query.get("layer-id")
        or query.get("node-id")
    )
    if not raw_layer:
        raise ValueError("Could not extract layerId. page_id/pageid is not layerId.")

    file_id = unquote(raw_file[0])
    layer_id = unquote(raw_layer[0])
    if ":" not in layer_id:
        raise ValueError(f"Suspicious layerId '{layer_id}': expected a value like 2:77196.")

    return {
        "fileId": file_id,
        "layerId": layer_id,
        "contentId": f"{file_id}-{layer_id.replace(':', '-')}",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="MasterGo URL containing /file/<fileId> or file=<fileId>, plus layer_id=<layerId>")
    args = parser.parse_args()
    try:
        print(json.dumps(parse_mastergo_url(args.url), ensure_ascii=False, indent=2))
        return 0
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
