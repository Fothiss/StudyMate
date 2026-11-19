# Spec Delta

## MODIFIED Requirements

### Requirement: Material Upload

The system SHALL accept a PDF study material together with a non-empty title, persist the file in internal storage and create a record owned by the authenticated user.

#### Scenario: Successful upload

- **WHEN** an authenticated user posts a `.pdf` file with a non-empty title
- **THEN** the system responds with `201` and a body containing `id`, `title`, `filename` and `created_at`

#### Scenario: Unsupported file type

- **WHEN** the uploaded file has an extension other than `.pdf`, including `.docx` and `.pptx`
- **THEN** the system responds with `415` and neither a file nor a record is stored

#### Scenario: File larger than the limit

- **WHEN** the uploaded file exceeds the configured size limit
- **THEN** the system responds with `413` and neither a file nor a record is stored

#### Scenario: Empty title

- **WHEN** the title is missing or empty
- **THEN** the system responds with `422` and neither a file nor a record is stored

## ADDED Requirements

### Requirement: Material Text Extraction

The system SHALL extract the PDF text layer during upload and keep it with the material record, and SHALL reject the upload when the extracted text is empty or exceeds the configured token limit.

#### Scenario: Text layer extracted

- **WHEN** an authenticated user uploads a PDF that has a text layer
- **THEN** the system responds with `201` and the stored material keeps its extracted text

#### Scenario: No text layer

- **WHEN** the uploaded PDF has no text layer, for example a scan
- **THEN** the system responds with `422` and neither a file nor a record is stored

#### Scenario: Text above the token limit

- **WHEN** the extracted text exceeds the configured limit of 30 000 tokens
- **THEN** the system responds with `422` and neither a file nor a record is stored
