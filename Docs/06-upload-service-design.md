# Upload Service – Internal Design

## Core Flow

1. Receive upload request
2. Validate file
3. Generate document_id
4. Store file
5. Persist metadata
6. Publish DocumentUploaded event
7. Return response immediately

---

## Internal Modules