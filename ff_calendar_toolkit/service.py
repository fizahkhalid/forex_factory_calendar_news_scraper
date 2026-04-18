from .console import AppConsole
from .models import RunOptions
from .normalize import normalize_rows
from .scraper import ForexFactoryScraper
from .storage import FileOutputStore


class ScrapeService:
    def __init__(self, console: AppConsole | None = None) -> None:
        self.console = console or AppConsole()

    def run(self, options: RunOptions) -> int:
        scraper = ForexFactoryScraper(self.console, headless=options.headless)
        store = FileOutputStore(options.output_dir)
        total_records = 0
        store.begin_run(options.output_format)

        for month in options.months:
            self.console.step(f"Scraping month selector '{month}'")
            raw_rows, context = scraper.scrape_month(month, options.target_timezone)
            self.console.step(
                f"Normalizing {len(raw_rows)} raw rows for {context.month_name} {context.year}"
            )
            records = normalize_rows(
                raw_rows,
                context.year,
                context.source_timezone,
                options.target_timezone,
                options.allowed_currencies,
                options.allowed_impacts,
                context.scraped_at,
            )
            self.console.step(
                f"Writing {len(records)} filtered rows as {options.output_format} output"
            )
            total_records += len(records)
            result = store.write(records, context, options.output_format)
            self.console.success(
                f"{context.month_name} {context.year}: {len(records)} rows written "
                f"to {options.output_dir}"
            )
            self.console.step(
                f"Last-run artifacts: {', '.join(str(path) for path in result.last_run_paths)}"
            )

        self.console.success(f"Run finished with {total_records} rows across {len(options.months)} month(s)")
        return 0
