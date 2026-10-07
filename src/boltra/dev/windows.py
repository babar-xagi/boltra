"""Run Uvicorn reload without Windows console broadcast signals.

Executed by the generated project's Python, which provides Uvicorn. Windows
reload must terminate only the old worker, rather than broadcast CTRL_C_EVENT
to the console or wait forever for a worker that ignored it.
See https://github.com/Kludex/uvicorn/issues/1972.
"""

from __future__ import annotations

import runpy

from uvicorn._subprocess import get_subprocess
from uvicorn.supervisors.basereload import BaseReload


def _stop_worker(supervisor: BaseReload) -> None:
    """Stop the reload worker without signalling unrelated console processes."""
    if supervisor.process.is_alive():
        supervisor.process.terminate()
    supervisor.process.join()


def _restart(supervisor: BaseReload) -> None:
    _stop_worker(supervisor)
    supervisor.process = get_subprocess(
        config=supervisor.config, target=supervisor.target, sockets=supervisor.sockets
    )
    supervisor.process.start()


_original_shutdown = BaseReload.shutdown


def _shutdown(supervisor: BaseReload) -> None:
    _stop_worker(supervisor)
    _original_shutdown(supervisor)


if __name__ == "__main__":
    BaseReload.restart = _restart  # type: ignore[method-assign, assignment]
    BaseReload.shutdown = _shutdown  # type: ignore[method-assign, assignment]
    runpy.run_module("uvicorn", run_name="__main__")
