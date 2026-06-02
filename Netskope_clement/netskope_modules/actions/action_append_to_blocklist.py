from typing import Literal

from pydantic import Field

from netskope_modules.actions.action_base import NetskopeAction, NetskopeActionArguments


class AppendToBlocklistArguments(NetskopeActionArguments):
    blocklist_id: str = Field(..., description="The ID of the blocklist")
    items: list[str] = Field(..., description="List of items in the blocklist (IPs, domains, or URLs)")
    sort_items: bool = Field(True, description="Sort items alphabetically")
    type: Literal["exact", "regex"] = Field("exact", description="Type of blocklist (exact, regex)")


class AppendToBlocklistAction(NetskopeAction):
    """
    Append IP addresses, domains, or URLs to an existing Netskope blocklist.
    """

    def run(self, arguments: dict) -> dict:
        args = AppendToBlocklistArguments(**arguments)
        self.initialize_action_arguments(args)

        current_blocklist = self.get_blocklist(args.blocklist_id)
        existing_urls = set(self.extract_urls(current_blocklist))
        normalized_items = self.normalize_urls(args.items, sort_items=args.sort_items)
        items_to_append = [item for item in normalized_items if item not in existing_urls]

        if not items_to_append:
            return {
                "append_result": current_blocklist,
                "deploy_result": [],
                "message": "No new item(s) to append: all provided values already exist in blocklist",
            }

        # Append items to the blocklist
        append_payload = {
            "data": {
                "type": args.type,
                "urls": items_to_append,
            }
        }

        append_response = self.execute_request(
            "PATCH", f"api/v2/policy/urllist/{args.blocklist_id}/append", json=append_payload
        )

        # Deploy the changes
        deploy_response = self.deploy_blocklist_changes()

        return {
            "append_result": append_response,
            "deploy_result": deploy_response,
            "message": f"Successfully appended {len(items_to_append)} item(s) to blocklist",
        }
