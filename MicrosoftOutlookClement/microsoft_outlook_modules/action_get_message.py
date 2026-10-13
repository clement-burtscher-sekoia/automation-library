from typing import Any

from pydantic import BaseModel, ConfigDict

from .action_base import MicrosoftGraphActionBase


class GetMessageArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user: str
    message_id: str | dict[str, Any]


class GetMessageAction(MicrosoftGraphActionBase):
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
        validated_arguments = GetMessageArguments.model_validate(arguments)
        user_id_or_principal_name = validated_arguments.user
        message_id = self._resolve_message_id(validated_arguments.message_id)

        response = self.client.get(
            f"https://graph.microsoft.com/v1.0/users/{user_id_or_principal_name}/messages/{message_id}",
            timeout=60,
        )
        self.handle_response(response)

        result = response.json()
        if isinstance(result, dict):
            resolved_message_id = result.get("id") if isinstance(result.get("id"), str) else message_id
            normalized_result = self._snake_case_keys(result)
            normalized_result.pop("id", None)
            normalized_result["user"] = user_id_or_principal_name
            normalized_result["message_id"] = resolved_message_id
            return normalized_result
        return result
