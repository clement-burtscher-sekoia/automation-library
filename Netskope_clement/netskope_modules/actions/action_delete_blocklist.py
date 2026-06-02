from pydantic import Field

from netskope_modules.actions.action_base import NetskopeAction, NetskopeActionArguments


class DeleteBlocklistArguments(NetskopeActionArguments):
    blocklist_id: str = Field(..., description="The ID of the blocklist")


class DeleteBlocklistAction(NetskopeAction):
    """
    Mark a Netskope blocklist as pending deletion and deploy the change.
    """

    def run(self, arguments: dict) -> dict:
        args = DeleteBlocklistArguments(**arguments)
        self.initialize_action_arguments(args)

        blocklist_id = args.blocklist_id
        delete_response = self.execute_request("DELETE", f"api/v2/policy/urllist/{blocklist_id}")

        # Deploy the deletion
        deploy_response = self.deploy_blocklist_changes()

        return {
            "delete_result": delete_response,
            "deploy_result": deploy_response,
            "message": f"Successfully deleted blocklist {blocklist_id}",
        }
