from pydantic import Field

from netskope_modules.actions.action_base import NetskopeAction, NetskopeActionArguments


class GetBlocklistArguments(NetskopeActionArguments):
    blocklist_id: str = Field(..., description="The ID of the blocklist")


class GetBlocklistAction(NetskopeAction):
    """
    Retrieve an existing Netskope blocklist.
    """

    def run(self, arguments: dict) -> dict:
        args = GetBlocklistArguments(**arguments)
        self.initialize_action_arguments(args)

        blocklist = self.get_blocklist(args.blocklist_id)

        return {
            "blocklist": blocklist,
            "items": self.extract_urls(blocklist),
            "message": f"Successfully fetched blocklist {args.blocklist_id}",
        }
