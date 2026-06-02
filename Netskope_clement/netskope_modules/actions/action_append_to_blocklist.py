from pydantic import Field

from netskope_modules.actions.action_base import NetskopeAction, NetskopeActionArguments


class AppendToBlocklistArguments(NetskopeActionArguments):
    url_list_id: str = Field(..., description="The ID of the URL list to modify")
    items: list[str] = Field(..., description="List of items to append to the blocklist (IPs, domains, or URLs)")
    type: str = Field("exact", description="Type of URL list (exact, regex, etc.)")

class AppendToBlocklistAction(NetskopeAction):
    """
    Append IP addresses, domains, or URLs to an existing Netskope blocklist.
    """

    def run(self, arguments: dict) -> dict:
        args = AppendToBlocklistArguments(**arguments)
        self.initialize_action_arguments(args)

        # Append items to the URL list
        append_payload = {
            "data": {
                "type": args.type,
                "urls": args.items
            }
        }

        append_response = self.execute_request(
            "PATCH", f"api/v2/policy/urllist/{args.url_list_id}/append", json=append_payload
        )

        # Deploy the changes
        deploy_response = self.deploy_blocklist_changes()

        return {
            "append_result": append_response,
            "deploy_result": deploy_response,
            "message": f"Successfully appended {len(args.items)} item(s) to blocklist",
        }
