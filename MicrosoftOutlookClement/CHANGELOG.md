# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Added

- Enrich action outputs:
  - action `Delete a message`:
    - `user`: the echo of the user identifier used for this action
  - action `Forward a message`:
    - `comment`: the optional comment included in the forwarded message
    - `recipients`: the recipient email addresses used by the action
    - `user`: the echo of the user identifier used for this action
  - action `Get a message`:
    - `user`: the echo of the user identifier used for this action
  - action `Search messages`:
    - `has_more`: the indicator that is true when Graph indicates additional pages may exist
    - `message_id`: the selected Microsoft Graph message item ID, or null when no result is found
    - `network_message_id`: the NetworkMessageId extracted from Graph extended properties when available
    - `query_type`: the identifier type used for the search
    - `query_value`: the search identifier value, or concatenated values when both identifiers are provided
    - `returned_count`: the alias of total_results for explicit count-based playbook conditions
    - `selected_index`: the selected index in the returned messages list, or null when no result is found
    - `selected_message`: the selected message object, or null when no result is found
    - `total_results`: the number of messages returned in this response
    - `user`: the echo of the user identifier used for this action, reusable in downstream playbook nodes
  - action `Send a message`:
    - `bcc`: the list of BCC recipient email addresses used by the action
    - `cc`: the list of CC recipient email addresses used by the action
    - `content_type`: the content type of the message body used by the action
    - `from`: the mailbox owner email address used in the From header
    - `importance`: the importance level of the message used by the action
    - `recipients`: the recipient email addresses used by the action
    - `save_to_sent_items`: the setting that controls whether the message is saved in Sent Items
    - `sender`: the sender email address used by the action
    - `subject`: the subject of the message used by the action
    - `user`: the echo of the user identifier used for this action
  - action `Update a message`:
    - `action`: the action technical identifier
    - `bcc`: the updated list of BCC recipient email addresses used by the action
    - `cc`: the updated list of CC recipient email addresses used by the action
    - `importance`: the importance level of the message used by the action
    - `original_from`: the original mailbox owner email address provided in the input From header
    - `original_subject`: the original subject provided in the input
    - `recipients`: the updated list of recipient email addresses used by the action
    - `sender`: the updated sender email address used by the action
    - `status`: the execution status
    - `user`: the echo of the user identifier used for this action

### Changed

- Refactor playbook and workflow tests to use `Search messages` as the source of message selection for Foreach-based flows
- Improve `Search messages` fallback behavior for `email_local_id` with paginated scanning via `@odata.nextLink`

### Fixed

- Fix false-negative lookups for `email_local_id` by bounding and paginating client-side fallback scanning (`FALLBACK_PAGE_SIZE=50`, `FALLBACK_MAX_MESSAGES_SCANNED=1000`)

### Removed

- Remove action `Resolve a message`
