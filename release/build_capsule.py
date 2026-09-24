"""Build a small, public, deterministic snapshot for immutable publication."""

import argparse
import hashlib
import json
from pathlib import Path


CERT_SHA256 = "5228f6c12fda873ebb2eecdb34a858a193e92c718efedf81b2c9de4fd72d3d70"
PACKET_COMMIT = "33eaa82859576b1127bd1805cba2f32d66e8a7e4"
BLOG_COMMIT = "ed3948fc24aa2a74d9f7c7af2d5236e9b7f6126a"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-root", required=True, type=Path)
    parser.add_argument("--blog-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    certificate = (args.packet_root / "research/p384-422/certificate.txt").read_bytes()
    article = (args.blog_root / "content/p384-422.md").read_bytes()
    if sha256(certificate) != CERT_SHA256:
        raise SystemExit("CERTIFICATE_HASH_MISMATCH")
    if not article.startswith(b"---\n") or b"author: Tommy Tai" not in article:
        raise SystemExit("ARTICLE_AUTHOR_MISMATCH")
    for marker in (b"C:\\Dev", b"private", b"gmail.com", b"@live.com", b"api_key", b"secret_key"):
        if marker.lower() in article.lower():
            raise SystemExit("ARTICLE_PRIVACY_MARKER:" + marker.decode("ascii"))

    capsule = {
        "schema": "tommytai.public_research_snapshot.v1",
        "author": "Tommy Tai",
        "published_utc": "2026-09-23T21:49:16Z",
        "snapshot_utc": "2026-09-23T22:07:18Z",
        "human_site": "https://tommytai.dev/",
        "ai_companion": "https://worldweaver.dev/",
        "post_url": "https://tommytai.dev/posts/p384-422/",
        "review_url": "https://github.com/TTaoGaming/portfolio/pull/1",
        "packet_commit": PACKET_COMMIT,
        "blog_commit": BLOG_COMMIT,
        "article_markdown_sha256": sha256(article),
        "certificate_sha256": sha256(certificate),
        "scope": "Public arithmetic research candidate; no novelty, optimality, native speed, side-channel, or external adoption claim.",
        "article_markdown": article.decode("utf-8"),
        "certificate_ascii": certificate.decode("ascii"),
    }
    payload = (json.dumps(capsule, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    if len(payload) >= 100_000:
        raise SystemExit("PAYLOAD_EXCEEDS_FREE_TIER_TARGET")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(json.dumps({"output": str(args.output), "bytes": len(payload), "sha256": sha256(payload), "certificate_sha256": sha256(certificate), "article_markdown_sha256": sha256(article)}))


if __name__ == "__main__":
    main()
