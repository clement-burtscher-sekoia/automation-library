from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field

from .action_base import GraphAPIException, MicrosoftGraphActionBase


class SearchMessagesArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user: str
    email_message_id: str | None = None
    email_local_id: str | None = None
    max_messages_to_return: int = Field(default=10, ge=1, le=100)
    return_most_recent_first: bool = False


class SearchMessagesAction(MicrosoftGraphActionBase):
    NETWORK_MESSAGE_ID_EXTENDED_PROPERTY = "String {41F28F13-83F4-4114-A584-EEDB5A6B0BFF} Name NetworkMessageId"
    FALLBACK_PAGE_SIZE = 50
    FALLBACK_MAX_MESSAGES_SCANNED = 1000

    @staticmethod
    def _escape_odata_literal(value: str) -> str:
        return value.replace("'", "''")

    @staticmethod
    def _extract_network_message_id(message: dict[str, Any]) -> str | None:
        for prop in message.get("singleValueExtendedProperties", []):
            if prop.get("id") == SearchMessagesAction.NETWORK_MESSAGE_ID_EXTENDED_PROPERTY:
                value = prop.get("value")
                return value if isinstance(value, str) else None
        return None

    def _search_by_network_message_id_fallback(
        self, user_id_or_principal_name: str, network_message_id: str, max_messages_to_return: int
    ) -> Any:
        escaped_property = self._escape_odata_literal(self.NETWORK_MESSAGE_ID_EXTENDED_PROPERTY)
        params: dict[str, Any] | None = {
            "$top": max(max_messages_to_return, self.FALLBACK_PAGE_SIZE),
            "$select": "id,internetMessageId,subject,receivedDateTime,from,toRecipients",
            "$expand": "singleValueExtendedProperties(" f"$filter=id eq '{escaped_property}'" ")",
            "$orderby": "receivedDateTime desc",
        }

        next_url = f"https://graph.microsoft.com/v1.0/users/{user_id_or_principal_name}/messages"
        matched_messages: list[dict[str, Any]] = []
        scanned_messages = 0

        while (
            next_url
            and len(matched_messages) < max_messages_to_return
            and scanned_messages < self.FALLBACK_MAX_MESSAGES_SCANNED
        ):
            response = self.client.get(next_url, params=params, timeout=60)
            self.handle_response(response)

            payload = response.json()
            messages: list[dict[str, Any]] = payload.get("value", [])
            scanned_messages += len(messages)

            matched_messages.extend(
                message for message in messages if self._extract_network_message_id(message) == network_message_id
            )

            next_url = payload.get("@odata.nextLink")
            params = None

        return {
            "value": matched_messages[:max_messages_to_return],
            "@odata.nextLink": next_url,
        }

    def run(self, arguments: Any) -> Any:
        validated_arguments = SearchMessagesArguments.model_validate(arguments)
        user_id_or_principal_name = validated_arguments.user
        internet_message_id = validated_arguments.email_message_id
        network_message_id = validated_arguments.email_local_id
        max_messages_to_return = validated_arguments.max_messages_to_return
        return_most_recent_first = validated_arguments.return_most_recent_first

        if not internet_message_id and not network_message_id:
            raise ValueError("Either email_message_id or email_local_id must be provided")

        if internet_message_id and network_message_id:
            query_type = "combined"
            query_value = f"email_message_id={internet_message_id};email_local_id={network_message_id}"
        elif internet_message_id:
            query_type = "email_message_id"
            query_value = internet_message_id
        else:
            query_type = "email_local_id"
            query_value = network_message_id

        filters: list[str] = []
        if internet_message_id:
            escaped_internet_message_id = self._escape_odata_literal(internet_message_id)
            filters.append(f"internetMessageId eq '{escaped_internet_message_id}'")

        if network_message_id:
            escaped_network_message_id = self._escape_odata_literal(network_message_id)
            escaped_property = self._escape_odata_literal(self.NETWORK_MESSAGE_ID_EXTENDED_PROPERTY)
            filters.append(
                "singleValueExtendedProperties/any(ep:"
                f"ep/id eq '{escaped_property}' and ep/value eq '{escaped_network_message_id}')"
            )

        params: dict[str, Any] = {
            "$filter": " and ".join(filters),
            "$top": max_messages_to_return,
            "$select": "id,internetMessageId,subject,receivedDateTime,from,toRecipients",
        }

        if return_most_recent_first:
            params["$orderby"] = "receivedDateTime desc"

        if network_message_id:
            escaped_property = self._escape_odata_literal(self.NETWORK_MESSAGE_ID_EXTENDED_PROPERTY)
            params["$expand"] = "singleValueExtendedProperties(" f"$filter=id eq '{escaped_property}'" ")"

        try:
            response = self.client.get(
                f"https://graph.microsoft.com/v1.0/users/{user_id_or_principal_name}/messages",
                params=params,
                timeout=60,
            )
            self.handle_response(response)
            payload = response.json()
        except GraphAPIException as exc:
            if network_message_id and "InefficientFilter" in str(exc):
                self.log(message="Fallback to client-side NetworkMessageId filtering", level="warning")
                payload = self._search_by_network_message_id_fallback(
                    user_id_or_principal_name, network_message_id, max_messages_to_return
                )
            else:
                raise

        if network_message_id and not payload.get("value"):
            self.log(message="No results with NetworkMessageId filter, retrying with fallback", level="warning")
            payload = self._search_by_network_message_id_fallback(
                user_id_or_principal_name,
                network_message_id,
                max_messages_to_return,
            )

        messages = payload.get("value", [])
        normalized_messages = cast(list[dict[str, Any]], self._snake_case_keys(messages))
        for raw_message, message in zip(messages, normalized_messages):
            raw_message_id = message.pop("id", None)
            if isinstance(raw_message_id, str):
                message["message_id"] = raw_message_id

            network_id = self._extract_network_message_id(raw_message)
            if network_id is not None:
                message["network_message_id"] = network_id

        has_more = bool(payload.get("@odata.nextLink"))
        total_results = len(normalized_messages)
        message_ids = [
            message["message_id"] for message in normalized_messages if isinstance(message.get("message_id"), str)
        ]

        if not normalized_messages:
            return {
                "user": user_id_or_principal_name,
                "query_type": query_type,
                "query_value": query_value,
                "message_ids": [],
                "messages": [],
                "total_results": 0,
                "returned_count": 0,
                "has_more": has_more,
            }

        return {
            "user": user_id_or_principal_name,
            "query_type": query_type,
            "query_value": query_value,
            "message_ids": message_ids,
            "messages": normalized_messages,
            "total_results": total_results,
            "returned_count": total_results,
            "has_more": has_more,
        }
