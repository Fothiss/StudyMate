# Spec Delta

## Purpose

Lets a user upload study materials and retrieve exactly their own materials, so later generation features always have a well-defined, owned source document to work from.

## ADDED Requirements

### Requirement: Material Upload

The system SHALL accept a study material file together with a non-empty title, persist the file in internal storage and create a record owned by the authenticated user.

#### Scenario: Successful upload

- **WHEN** an authenticated user posts a `.pdf`, `.docx` or `.pptx` file with a non-empty title
- **THEN** the system responds with `201` and a body containing `id`, `title`, `filename` and `created_at`

#### Scenario: Unsupported file type

- **WHEN** the uploaded file has an extension other than `.pdf`, `.docx` or `.pptx`
- **THEN** the system responds with `415` and neither a file nor a record is stored

#### Scenario: File larger than the limit

- **WHEN** the uploaded file exceeds the configured size limit
- **THEN** the system responds with `413` and neither a file nor a record is stored

#### Scenario: Empty title

- **WHEN** the title is missing or empty
- **THEN** the system responds with `422` and neither a file nor a record is stored

### Requirement: Material Listing

The system SHALL return only the materials owned by the current user, ordered newest first.

#### Scenario: Only own materials are listed

- **WHEN** two different users both have materials and one of them lists materials
- **THEN** the response contains only the materials of the requesting user

#### Scenario: Empty listing

- **WHEN** the current user has no materials
- **THEN** the system responds with `200` and an empty array

### Requirement: Material Card

The system SHALL return a single material only when it belongs to the current user and SHALL respond `404` otherwise, without revealing that another user's material exists.

#### Scenario: Own material

- **WHEN** the current user requests a material identifier they own
- **THEN** the system responds with `200` and that material

#### Scenario: Another user's material

- **WHEN** the requested material belongs to a different user
- **THEN** the system responds with `404`

#### Scenario: Unknown material

- **WHEN** the requested identifier does not exist
- **THEN** the system responds with `404`

### Requirement: Storage Isolation

The system SHALL store each material file under a directory unique to that material and MUST NOT let client-supplied names place a file outside that directory.

#### Scenario: Duplicate filenames do not collide

- **WHEN** two materials are uploaded with the same original filename
- **THEN** both files are stored and neither overwrites the other

#### Scenario: Path traversal attempt

- **WHEN** the uploaded filename contains `..` or path separators
- **THEN** the file is written inside that material's own directory and no file is written elsewhere

#### Scenario: Original filename preserved

- **WHEN** any material is stored
- **THEN** its card still reports the original filename the user uploaded
