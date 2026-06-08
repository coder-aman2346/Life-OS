from app.services.intent_detector import _detect_locally


def test_detect_note_intent() -> None:
    result = _detect_locally("Save a note: my AWS account ID is 123456789")
    assert result.intent == "create_note"
    assert "AWS" in result.title
    assert result.confidence >= 0.6


def test_detect_reminder_intent() -> None:
    result = _detect_locally("Remind me to call the dentist on Friday")
    assert result.intent == "create_reminder"
    assert "dentist" in result.title.lower()
    assert result.confidence >= 0.6


def test_detect_no_intent() -> None:
    result = _detect_locally("What is the weather like today?")
    assert result.intent == "none"


def test_detect_note_with_remember() -> None:
    result = _detect_locally("Remember that my favorite color is blue")
    assert result.intent == "create_note"
    assert "blue" in result.title.lower()


def test_detect_reminder_with_dont_forget() -> None:
    result = _detect_locally("Don't forget to buy groceries")
    assert result.intent == "create_reminder"
    assert "groceries" in result.title.lower()


def test_detect_note_with_jot_down() -> None:
    result = _detect_locally("Jot down: meeting notes from standup")
    assert result.intent == "create_note"
