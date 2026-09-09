# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Added

- Enrich action outputs:
  - action `Delete a message`:
    - `user`: The echo of the user identifier used for this action
  - action `Forward a message`:
    - `comment`: The optional comment included in the forwarded message
    - `recipients`: The recipient email addresses used by the action
    - `user`: The echo of the user identifier used for this action
  - action `Get a message`:
    - `user`: The echo of the user identifier used for this action
  - action `Search messages`:
    - `has_more`: The indicator that is true when Graph indicates additional pages may exist
    - `message_ids`: The list of Microsoft Graph message item IDs extracted from returned messages
    - `network_message_id`: The NetworkMessageId extracted from Graph extended properties when available
    - `query_type`: The identifier type used for the search
    - `query_value`: The search identifier value, or concatenated values when both identifiers are provided
    - `returned_count`: The alias of total_results for explicit count-based playbook conditions
    - `total_results`: The number of messages returned in this response
    - `user`: The echo of the user identifier used for this action, reusable in downstream playbook nodes
  - action `Send a message`:
    - `bcc`: The list of BCC recipient email addresses used by the action
    - `cc`: The list of CC recipient email addresses used by the action
    - `content_type`: The content type of the message body used by the action
    - `from`: The mailbox owner email address used in the From header
    - `importance`: The importance level of the message used by the action
    - `recipients`: The recipient email addresses used by the action
    - `save_to_sent_items`: The setting that controls whether the message is saved in Sent Items
    - `sender`: The sender email address used by the action
    - `subject`: The subject of the message used by the action
    - `user`: The echo of the user identifier used for this action
  - action `Update a message`:
    - `action`: The action technical identifier
    - `bcc`: The updated list of BCC recipient email addresses used by the action
    - `cc`: The updated list of CC recipient email addresses used by the action
    - `importance`: The importance level of the message used by the action
    - `original_from`: The original mailbox owner email address provided in the input From header
    - `original_subject`: The original subject provided in the input
    - `recipients`: The updated list of recipient email addresses used by the action
    - `sender`: The updated sender email address used by the action
    - `status`: The execution status
    - `user`: The echo of the user identifier used for this action

### Changed

- Refactor playbook and workflow tests to use `Search messages` as the source of message selection for Foreach-based flows
- Improve `Search messages` fallback behavior for `email_local_id` with paginated scanning via `@odata.nextLink`
- Update `Search messages` input names to `max_messages_to_return` and `return_most_recent_first`
- Remove legacy `item_index` input from `Search messages` to keep a list-only selection model

### Fixed

- Fix false-negative lookups for `email_local_id` by bounding and paginating client-side fallback scanning (`FALLBACK_PAGE_SIZE=50`, `FALLBACK_MAX_MESSAGES_SCANNED=1000`)

### Removed

- Remove action `Resolve a message`
