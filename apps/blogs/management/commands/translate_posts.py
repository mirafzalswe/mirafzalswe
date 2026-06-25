"""Bulk auto-translate posts into the empty languages.

Posts already translate themselves on save (see apps.blogs.translation). This
command is for back-filling existing posts or forcing a re-translation.

Usage:
    python manage.py translate_posts                # all posts, fill empty languages
    python manage.py translate_posts --post 12      # only post with pk=12
    python manage.py translate_posts --overwrite    # rewrite even if a translation exists
    python manage.py translate_posts --provider mymemory  # google | mymemory | deepl

Providers:
    google     – default; deep-translator GoogleTranslator (no key, free, rate-limited)
    mymemory   – fallback if Google blocks; no key, free
    deepl      – needs DEEPL_API_KEY env var

The source language is detected per post (EN→RU→UZ priority) — translation
always flows from whichever language the post was authored in.
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.blogs.models import Post
from apps.blogs.translation import autofill_translations, detect_source_lang


class Command(BaseCommand):
    help = "Back-fill post translations into the empty languages."

    def add_arguments(self, parser):
        parser.add_argument("--post", type=int, default=None, help="Only this post pk")
        parser.add_argument("--overwrite", action="store_true", help="Replace existing translations")
        parser.add_argument(
            "--provider",
            default=getattr(settings, "POST_TRANSLATE_PROVIDER", "google"),
            choices=("google", "mymemory", "deepl"),
        )
        parser.add_argument("--sleep", type=float, default=0.3, help="Pause between calls (s)")

    def handle(self, *args, **opts):
        provider = opts["provider"]
        overwrite = opts["overwrite"]
        sleep_s = opts["sleep"]

        qs = Post.objects.all()
        if opts["post"]:
            qs = qs.filter(pk=opts["post"])

        total = qs.count()
        if not total:
            self.stdout.write(self.style.WARNING("No posts found."))
            return

        self.stdout.write(f"Translating {total} post(s) via {provider} (overwrite={overwrite})")

        for post in qs:
            src = detect_source_lang(post)
            self.stdout.write(self.style.HTTP_INFO(f"\n[#{post.pk}] {post.title[:80] or '(no EN title)'}  src={src}"))
            if src is None:
                self.stdout.write("  empty post, skipped")
                continue

            try:
                changed = autofill_translations(
                    post, provider=provider, overwrite=overwrite, sleep_s=sleep_s,
                )
            except Exception as exc:
                raise CommandError(f"Translation failed for post #{post.pk}: {exc}") from exc

            if changed:
                # Skip a second round of translation; just persist + re-render HTML.
                post.save(auto_translate=False)
                self.stdout.write(self.style.SUCCESS(f"  saved: {', '.join(changed)}"))
            else:
                self.stdout.write("  nothing to update")

        self.stdout.write(self.style.SUCCESS("\nDone."))
