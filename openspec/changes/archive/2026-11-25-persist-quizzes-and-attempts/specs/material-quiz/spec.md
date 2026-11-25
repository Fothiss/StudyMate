# Spec Delta

## MODIFIED Requirements

### Requirement: Quiz Generation

The system SHALL generate a quiz for a material owned by the current user from its extracted text, using the configured language model, SHALL take the numbers of multiple-choice and open questions from the request, and SHALL store the generated quiz with its questions so it can be taken and read back later.

#### Scenario: Successful generation

- **WHEN** an authenticated user requests a quiz for a material they own that has extracted text
- **THEN** the system responds with `200` and a body containing a non-empty summary, a non-empty list of questions and a test identifier

#### Scenario: Generated quiz is stored

- **WHEN** a quiz is generated successfully
- **THEN** the system stores the quiz together with its questions, answer options and reference answers, and the stored quiz belongs to the requesting user

#### Scenario: Requested counts are used

- **WHEN** the request asks for a given number of multiple-choice questions and a given number of open questions
- **THEN** the system instructs the language model to produce exactly that composition and the returned quiz contains only those two kinds of questions

#### Scenario: Nothing requested

- **WHEN** the request asks for zero multiple-choice questions and zero open questions
- **THEN** the system responds with `422` and no quiz is generated or stored

#### Scenario: Another user's material

- **WHEN** the requested material belongs to a different user
- **THEN** the system responds with `404`

#### Scenario: Unknown material

- **WHEN** the requested material identifier does not exist
- **THEN** the system responds with `404`

#### Scenario: Material without text

- **WHEN** the requested material has no extracted text
- **THEN** the system responds with `422`

#### Scenario: Language model unavailable

- **WHEN** the language model cannot be reached or returns an error
- **THEN** the system responds with `502`, returns no quiz and stores no partial test

#### Scenario: Repeated requests store separate tests

- **WHEN** the same material is requested twice in a row
- **THEN** the system generates and stores two separate tests and returns a different test identifier each time

## REMOVED Requirements

### Requirement: Transient Quiz

**Reason**: The generated quiz is now stored so that attempts, evaluation results and progress can be kept and read back; a transient quiz made all three impossible.

**Migration**: Clients that relied on generation not storing anything keep the same request and response shape, but now also receive a test identifier and can submit answers against it. Stored tests are read through the attempt endpoints of the `quiz-attempts` capability.
