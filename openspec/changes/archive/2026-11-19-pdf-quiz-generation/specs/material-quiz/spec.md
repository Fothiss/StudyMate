# Spec Delta

## Purpose

Lets a user obtain a short summary and multiple-choice questions generated from the text of their own uploaded material, so they can test their knowledge without writing questions by hand.

## ADDED Requirements

### Requirement: Quiz Generation

The system SHALL generate a summary and questions from the extracted text of a material owned by the current user, using the configured language model.

#### Scenario: Successful generation

- **WHEN** an authenticated user requests a quiz for a material they own that has extracted text
- **THEN** the system responds with `200` and a body containing a non-empty summary and a non-empty list of questions

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
- **THEN** the system responds with `502` and no partial quiz

### Requirement: Generated Quiz Structure

The system MUST validate the language model response before returning it: the quiz has at least one question, each question has at least two options, and its correct answer index points at an existing option.

#### Scenario: Valid quiz returned

- **WHEN** the language model returns a summary and questions with in-range answer indexes
- **THEN** the system responds with `200` and every question carries its options and correct answer index

#### Scenario: Malformed quiz rejected

- **WHEN** the language model returns no questions, a question with fewer than two options, or an out-of-range answer index
- **THEN** the system responds with `502` and does not return the malformed quiz

### Requirement: Transient Quiz

The system SHALL NOT persist generated quizzes; each request generates a new quiz from the material text.

#### Scenario: Repeated requests

- **WHEN** the same material is requested twice in a row
- **THEN** the system responds with a newly generated quiz each time and stores nothing
