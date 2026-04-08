# Product Notes

Business rules and constraints from product conversations. **Check this before making product decisions.**

## Dataset Requests

Customers may request datasets with multiple focus areas (e.g., "clips of nature and dish-washing"). For now, we return all clips that match **both** requested categories. This is an AND filter, not OR.

Future iteration may support more complex filtering, but the current behavior is intentional.

## Delivery IDs Are Internal

`delivery_id` values in the [[Project Requirements|metadata files]] are hashed IDs of the source videos. These are **internal identifiers and must not be exposed to end users** in any UI surface.

When displaying clips or videos to customers:
- Use human-readable names, indices, or generated labels
- `delivery_id` may be used internally for grouping and data joins
- API responses to external/customer-facing endpoints should omit or alias `delivery_id`

GTM and Engineering users may see delivery IDs in internal tools if useful, but customer-facing views must not show them.

## See Also

- [[Project Requirements]]
- [[Data Model Overview]]
- [[GCSClient]]
