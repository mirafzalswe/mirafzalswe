"""Auto-translate Post.title / excerpt / content from EN into RU and UZ.

Usage:
    python manage.py translate_posts                # translate all posts, both languages
    python manage.py translate_posts --langs ru     # only Russian
    python manage.py translate_posts --post 12      # only post with pk=12
    python manage.py translate_posts --overwrite    # rewrite even if translation exists
    python manage.py translate_posts --provider mymemory  # google | mymemory | deepl

Providers:
    google     – default; uses deep-translator GoogleTranslator (no key, free, rate-limited)
    mymemory   – fallback if Google blocks; no key, free
    deepl      – needs DEEPL_API_KEY env var
"""

import os
import re
import time

from django.core.management.base import BaseCommand, CommandError

from apps.blogs.models import Post


SUPPORTED_LANGS = ("ru", "uz")
FIELDS = ("title", "excerpt", "content")
CHUNK_SIZE = 4500  # safe for free tiers; deep-translator splits longer text

# Patterns whose contents must NOT be translated (code, URLs, etc.)
_FENCED_CODE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_INLINE_CODE = re.compile(r"`[^`\n]+`")
_URL = re.compile(r"https?://\S+")
_PLACEHOLDER_RE = re.compile(r"§§(\d+)§§")


def _protect(text: str):
    """Replace code blocks/URLs with sentinel tokens; return (masked_text, mapping)."""
    parts = []

    def _stash(match):
        parts.append(match.group(0))
        return f"§§{len(parts) - 1}§§"

    masked = _FENCED_CODE.sub(_stash, text)
    masked = _INLINE_CODE.sub(_stash, masked)
    masked = _URL.sub(_stash, masked)
    return masked, parts


def _restore(text: str, parts):
    def _unstash(match):
        idx = int(match.group(1))
        return parts[idx] if 0 <= idx < len(parts) else match.group(0)

    return _PLACEHOLDER_RE.sub(_unstash, text)


def _load_translator(provider: str):
    """Return a callable translate(text, target) -> str."""
    try:
        from deep_translator import GoogleTranslator, MyMemoryTranslator, DeeplTranslator
    except ImportError as e:
        raise CommandError(
            "deep-translator is not installed. Run: pip install deep-translator"
        ) from e

    if provider == "google":
        def _tr(text, target):
            return GoogleTranslator(source="en", target=target).translate(text)
        return _tr

    if provider == "mymemory":
        def _tr(text, target):
            return MyMemoryTranslator(source="en-US", target=f"{target}-{target.upper()}").translate(text)
        return _tr

    if provider == "deepl":
        key = os.environ.get("DEEPL_API_KEY")
        if not key:
            raise CommandError("DEEPL_API_KEY is not set in environment")

        def _tr(text, target):
            return DeeplTranslator(api_key=key, source="en", target=target, use_free_api=True).translate(text)
        return _tr

    raise CommandError(f"Unknown provider: {provider}")


def _split_chunks(text: str, size: int = CHUNK_SIZE):
    """Split text into chunks at paragraph boundaries when possible."""
    if not text:
        return []
    if len(text) <= size:
        return [text]
    chunks, buf = [], ""
    for para in text.split("\n\n"):
        candidate = (buf + "\n\n" + para) if buf else para
        if len(candidate) > size and buf:
            chunks.append(buf)
            buf = para
        else:
            buf = candidate
    if buf:
        chunks.append(buf)
    return chunks


class Command(BaseCommand):
    help = "Auto-translate existing posts into RU and UZ."

    def add_arguments(self, parser):
        parser.add_argument("--langs", nargs="+", default=list(SUPPORTED_LANGS), choices=SUPPORTED_LANGS)
        parser.add_argument("--post", type=int, default=None, help="Only this post pk")
        parser.add_argument("--overwrite", action="store_true", help="Replace existing translations")
        parser.add_argument("--provider", default="google", choices=("google", "mymemory", "deepl"))
        parser.add_argument("--sleep", type=float, default=0.5, help="Pause between calls (s)")

    def handle(self, *args, **opts):
        translate = _load_translator(opts["provider"])
        langs = opts["langs"]
        overwrite = opts["overwrite"]
        sleep_s = opts["sleep"]

        qs = Post.objects.all()
        if opts["post"]:
            qs = qs.filter(pk=opts["post"])

        total = qs.count()
        if not total:
            self.stdout.write(self.style.WARNING("No posts found."))
            return

        self.stdout.write(f"Translating {total} post(s) into: {', '.join(langs)} via {opts['provider']}")

        for post in qs:
            self.stdout.write(self.style.HTTP_INFO(f"\n[#{post.pk}] {post.title[:80]}"))
            changed_fields = []

            for lang in langs:
                for field in FIELDS:
                    src = getattr(post, field, "") or ""
                    if not src.strip():
                        continue

                    target_attr = f"{field}_{lang}"
                    if not hasattr(post, target_attr):
                        continue

                    existing = getattr(post, target_attr, "") or ""
                    if existing.strip() and not overwrite:
                        self.stdout.write(f"  · {target_attr}: skip (already filled)")
                        continue

                    try:
                        masked, stash = _protect(src) if field == "content" else (src, [])
                        chunks = _split_chunks(masked)
                        translated_parts = []
                        for c in chunks:
                            translated_parts.append(translate(c, lang) or "")
                            time.sleep(sleep_s)
                        translated = "\n\n".join(translated_parts).strip()
                        if stash:
                            translated = _restore(translated, stash)
                    except Exception as exc:
                        self.stderr.write(self.style.ERROR(f"  · {target_attr}: FAILED — {exc}"))
                        continue

                    if not translated:
                        self.stdout.write(f"  · {target_attr}: empty result, skipped")
                        continue

                    setattr(post, target_attr, translated)
                    changed_fields.append(target_attr)
                    self.stdout.write(self.style.SUCCESS(f"  · {target_attr}: ok ({len(translated)} chars)"))

            if changed_fields:
                post.save()
                self.stdout.write(self.style.SUCCESS(f"  saved: {', '.join(changed_fields)}"))
            else:
                self.stdout.write("  nothing to update")

        self.stdout.write(self.style.SUCCESS("\nDone."))
