import requests_mock
import pytest

from microsoft_outlook_modules.action_forward_message import ForwardMessageAction


def test_forward_message(configured_action):
    with requests_mock.Mocker() as mock:
        mock.register_uri(
            "GET",
            "https://login.microsoftonline.com/test_tenant_id/oauth2/v2.0/token",
            json={"access_token": "foo-token", "token_type": "bearer", "expires_in": 1799},
        )
        mock.register_uri(
            "POST",
            "https://graph.microsoft.com/v1.0/users/1111/messages/2222/forward",
            status_code=202,
            content=b"",
        )

        action = configured_action(ForwardMessageAction)
        result = action.run(arguments={"user": "1111", "message_id": "2222", "recipients": ["john.doe@example.com"]})
        assert result == {
            "action": "forward_message",
            "comment": "",
            "recipients": ["john.doe@example.com"],
            "status": "forwarded",
            "target_message_id": "2222",
            "user": "1111",
        }


def test_forward_message_accepts_message_object_from_foreach(configured_action):
    with requests_mock.Mocker() as mock:
        mock.register_uri(
            "GET",
            "https://login.microsoftonline.com/test_tenant_id/oauth2/v2.0/token",
            json={"access_token": "foo-token", "token_type": "bearer", "expires_in": 1799},
        )
        mock.register_uri(
            "POST",
            "https://graph.microsoft.com/v1.0/users/1111/messages/2222/forward",
            status_code=202,
            content=b"",
        )

        action = configured_action(ForwardMessageAction)
        result = action.run(
            arguments={
                "user": "1111",
                "message_id": {"message_id": "2222"},
                "recipients": ["john.doe@example.com"],
            }
        )
        assert result["target_message_id"] == "2222"


def test_forward_message_rejects_message_object_without_message_id(configured_action):
    action = configured_action(ForwardMessageAction)
    with pytest.raises(ValueError, match="message_id must be a string or a message object"):
        action.run(arguments={"user": "1111", "message_id": {"subject": "x"}, "recipients": ["a@b.c"]})


def test_forward_message_rejects_non_string_non_object_message_id(configured_action):
    _ = configured_action(ForwardMessageAction)
    with pytest.raises(ValueError, match="message_id must be a string or a message object"):
        ForwardMessageAction._resolve_message_id(123)  # type: ignore[arg-type]
