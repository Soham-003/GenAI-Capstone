from app.agents.actions import trigger_quality_check


def test_trigger_quality_check_contains_status() -> None:
    result = trigger_quality_check("test_pipeline")
    assert "test_pipeline" in result
    assert "PASS" in result or "WARN" in result
