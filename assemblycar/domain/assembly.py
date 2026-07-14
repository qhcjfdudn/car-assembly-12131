from dataclasses import dataclass
from typing import Optional

from assemblycar.domain.rules import Reason, incompatibilities, is_compatible
from assemblycar.domain.spec import CarSpec
from assemblycar.domain.types import Engine


@dataclass(frozen=True)
class RunResult:
    ok: bool
    broken_engine: bool
    spec: Optional[CarSpec]


@dataclass(frozen=True)
class TestResult:
    passed: bool
    reasons: list[Reason]


def run(spec: CarSpec) -> RunResult:
    if not is_compatible(spec):
        return RunResult(ok=False, broken_engine=False, spec=None)

    if spec.engine is Engine.BROKEN:
        return RunResult(ok=False, broken_engine=True, spec=None)

    return RunResult(ok=True, broken_engine=False, spec=spec)


def test(spec: CarSpec) -> TestResult:
    reasons = incompatibilities(spec)
    return TestResult(passed=not reasons, reasons=reasons)
