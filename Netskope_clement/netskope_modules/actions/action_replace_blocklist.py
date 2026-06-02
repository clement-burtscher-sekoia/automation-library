from typing import Literal

from pydantic import Field

from netskope_modules.actions.action_base import NetskopeAction, NetskopeActionArguments


class ReplaceBlocklistArguments(NetskopeActionArguments):
    blocklist_id: str = Field(..., description="The ID of the blocklist")
    blocklist_name: str = Field(..., description="The name of the blocklist")
    blocklist_type: Literal["exact", "regex"] = Field("exact", description="Type of blocklist (exact, regex)")
    items: list[str] = Field(..., description="List of items in the blocklist (IPs, domains, or URLs)")
    sort_items: bool = Field(True, description="Sort items alphabetically")


class ReplaceBlocklistAction(NetskopeAction):
    """
    Replace an entire Netskope blocklist with new items.
    """

    def run(self, arguments: dict) -> dict:
        args = ReplaceBlocklistArguments(**arguments)
        self.initialize_action_arguments(args)
        normalized_items = self.normalize_urls(args.items, sort_items=args.sort_items)

        # Replace the entire blocklist
        replace_payload = {
            "data": {"type": args.blocklist_type, "urls": normalized_items},
            "name": args.blocklist_name,
        }

        replace_response = self.execute_request(
            "PATCH", f"api/v2/policy/urllist/{args.blocklist_id}/replace", json=replace_payload
        )

        # Deploy the changes
        deploy_response = self.deploy_blocklist_changes()

        return {
            "replace_result": replace_response,
            "deploy_result": deploy_response,
            "message": f"Successfully replaced blocklist with {len(normalized_items)} item(s)",
        }
