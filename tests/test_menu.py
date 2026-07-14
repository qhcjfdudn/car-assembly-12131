from assemblycar.cli.menu import is_valid_range


def test_car_type_step_rejects_zero():
    # 차종 단계는 뒤로가기가 없으므로 0은 허용되지 않는다.
    assert not is_valid_range(0, 0)


def test_car_type_step_accepts_1_to_3():
    for ans in (1, 2, 3):
        assert is_valid_range(0, ans)


def test_car_type_step_rejects_out_of_range():
    assert not is_valid_range(0, 4)


def test_engine_step_accepts_0_to_4():
    for ans in (0, 1, 2, 3, 4):
        assert is_valid_range(1, ans)


def test_engine_step_rejects_out_of_range():
    assert not is_valid_range(1, 5)


def test_brake_step_accepts_0_to_3():
    for ans in (0, 1, 2, 3):
        assert is_valid_range(2, ans)


def test_brake_step_rejects_out_of_range():
    assert not is_valid_range(2, 4)


def test_steering_step_accepts_0_to_2():
    for ans in (0, 1, 2):
        assert is_valid_range(3, ans)


def test_steering_step_rejects_out_of_range():
    assert not is_valid_range(3, 3)


def test_run_test_step_accepts_0_to_2():
    for ans in (0, 1, 2):
        assert is_valid_range(4, ans)


def test_run_test_step_rejects_out_of_range():
    assert not is_valid_range(4, 3)
