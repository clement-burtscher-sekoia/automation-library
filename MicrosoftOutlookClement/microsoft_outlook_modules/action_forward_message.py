from typing import Any

from pydantic import BaseModel, ConfigDict

from .action_base import MicrosoftGraphActionBase


class ForwardMessageArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user: str
    message_id: str | dict[str, Any]
    recipients: list[str]
    comment: str = ""


class ForwardMessageAction(MicrosoftGraphActionBase):
    @staticmethod
    def _resolve_message_id(message_id_or_item: str | dict[str, Any]) -> str:
        if isinstance(message_id_or_item, str):
            return message_id_or_item

        if isinstance(message_id_or_item, dict):
            nested_message_id = message_id_or_item.get("message_id")
            if isinstance(nested_message_id, str):
                return nested_message_id

        raise ValueError("message_id must be a string or a message object containing a string message_id")

    def run(self, arguments: Any) -> Any:
        validated_arguments = ForwardMessageArguments.model_validate(arguments)
        user_id_or_principal_name = validated_arguments.user
        message_id = self._resolve_message_id(validated_arguments.message_id)
        recipients = validated_arguments.recipients
        comment = validated_arguments.comment

        payload: dict[str, Any] = {
            "comment": comment,
            "toRecipients": [{"emailAddress": {"name": recipient, "address": recipient}} for recipient in recipients],
        }

        response = self.client.post(
            f"https://graph.microsoft.com/v1.0/users/{user_id_or_principal_name}/messages/{message_id}/forward",
            json=payload,
            timeout=60,
        )
        self.handle_response(response)

        return {
            "status": "forwarded",
            "action": "forward_message",
            "comment": comment,
            "target_message_id": message_id,
            "user": user_id_or_principal_name,
            "recipients": recipients,
        }
