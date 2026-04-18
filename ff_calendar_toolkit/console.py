from datetime import datetime

try:
    from rich.console import Console
except ModuleNotFoundError:
    Console = None


class AppConsole:
    def __init__(self) -> None:
        self.console = Console() if Console else None

    def _stamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _line(self, label: str, color: str, message: str) -> None:
        if self.console:
            self.console.print(
                f"[dim]{self._stamp()}[/dim] [{color}]{label:<7}[/{color}] {message}"
            )
            return
        print(f"{self._stamp()} {label:<7} {message}", flush=True)

    def step(self, message: str) -> None:
        self._line("INFO", "cyan", message)

    def success(self, message: str) -> None:
        self._line("DONE", "green", message)

    def warn(self, message: str) -> None:
        self._line("WARN", "yellow", message)

    def error(self, message: str) -> None:
        self._line("ERROR", "red", message)
