"""Run the caliper-only stream logger."""
from shared.caliper_streamer import run_caliper_stream


def main() -> None:
    run_caliper_stream(
        duration=None,
        port=None,
        log_path=None,
        read_size=19,
        reconnect_delay=2.0,
    )


if __name__ == "__main__":
    main()
