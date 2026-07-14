"""
assemblycar.cli.app.main()의 위저드 루프에 대한 블랙박스 테스트.

input()을 미리 준비한 응답 목록으로, delay()를 no-op으로 monkeypatch해
실제 대기 없이 전체 흐름(내비게이션, RUN, Test)을 구동하고 capsys로
출력을 검증한다.
"""
import assemblycar.cli.app as app


def run_wizard(monkeypatch, inputs):
    monkeypatch.setattr(app, "delay", lambda ms: None)
    responses = iter(inputs)

    def fake_input(prompt=""):
        try:
            return next(responses)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)
    app.main()


def test_exit_quits_immediately(monkeypatch, capsys):
    run_wizard(monkeypatch, ["exit"])
    output = capsys.readouterr().out
    assert "바이바이" in output


def test_back_navigation_returns_to_previous_step(monkeypatch, capsys):
    # 엔진 단계에서 0을 입력하면 차종 선택 화면으로 돌아간다.
    run_wizard(monkeypatch, ["1", "0", "exit"])
    output = capsys.readouterr().out
    assert output.count("어떤 차량 타입을 선택할까요?") == 2


def test_run_test_screen_back_returns_to_car_type_step(monkeypatch, capsys):
    run_wizard(monkeypatch, ["1", "1", "1", "1", "0", "exit"])
    output = capsys.readouterr().out
    assert output.count("어떤 차량 타입을 선택할까요?") == 2


def test_full_run_flow_prints_spec_and_runs(monkeypatch, capsys):
    run_wizard(monkeypatch, ["1", "1", "1", "1", "1", "exit"])
    output = capsys.readouterr().out
    assert "Car Type : Sedan" in output
    assert "Engine   : GM" in output
    assert "Brake    : Mando" in output
    assert "Steering : Bosch" in output
    assert "자동차가 동작됩니다." in output


def test_broken_engine_run_reports_failure(monkeypatch, capsys):
    run_wizard(monkeypatch, ["1", "4", "1", "1", "1", "exit"])
    output = capsys.readouterr().out
    assert "엔진이 고장나있습니다." in output
    assert "자동차가 움직이지 않습니다." in output


def test_full_test_flow_prints_pass(monkeypatch, capsys):
    run_wizard(monkeypatch, ["1", "1", "1", "1", "2", "exit"])
    output = capsys.readouterr().out
    assert "Test..." in output
    assert "PASS" in output


def test_full_test_flow_prints_fail_reason(monkeypatch, capsys):
    # Sedan(1) + GM(1) + Continental(2) + Bosch(1) 조향 -> 세단/컨티넨탈 규칙 위반
    run_wizard(monkeypatch, ["1", "1", "2", "1", "2", "exit"])
    output = capsys.readouterr().out
    assert "FAIL" in output
    assert "Sedan에는 Continental제동장치 사용 불가" in output


def test_out_of_range_input_reprompts(monkeypatch, capsys):
    run_wizard(monkeypatch, ["9", "1", "1", "1", "1", "1", "exit"])
    output = capsys.readouterr().out
    assert "ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능" in output


def test_non_numeric_input_reprompts(monkeypatch, capsys):
    run_wizard(monkeypatch, ["abc", "1", "1", "1", "1", "1", "exit"])
    output = capsys.readouterr().out
    assert "ERROR :: 숫자만 입력 가능" in output
