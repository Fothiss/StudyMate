# material-quiz Specification

## Purpose

Lets a user obtain a short summary and multiple-choice questions generated from the text of their own uploaded material, so they can test their knowledge without writing questions by hand.

## Requirements

### Requirement: Quiz Generation

The system SHALL generate a quiz for a material owned by the current user from its extracted text, using the configured language model, and SHALL take the numbers of multiple-choice and open questions to produce from the request.

#### Scenario: Successful generation

- **WHEN** an authenticated user requests a quiz for a material they own that has extracted text
- **THEN** the system responds with `200` and a body containing a non-empty summary and a non-empty list of questions

#### Scenario: Requested counts are used

- **WHEN** the request asks for a given number of multiple-choice questions and a given number of open questions
- **THEN** the system instructs the language model to produce exactly that composition and the returned quiz contains only those two kinds of questions

#### Scenario: Nothing requested

- **WHEN** the request asks for zero multiple-choice questions and zero open questions
- **THEN** the system responds with `422` and no quiz

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

The system MUST validate the language model response before returning it: the quiz has at least one question, every multiple-choice question offers at least two options with a correct answer index pointing at an existing option, and every open question carries a non-empty reference answer.

#### Scenario: Valid quiz returned

- **WHEN** the language model returns a summary and questions whose kinds and answer data are well formed
- **THEN** the system responds with `200` and every question carries its kind and the data that kind requires

#### Scenario: Malformed quiz rejected

- **WHEN** the language model returns no questions, a multiple-choice question with fewer than two options, an out-of-range answer index, or an open question without a reference answer
- **THEN** the system responds with `502` and does not return the malformed quiz

### Requirement: Transient Quiz

The system SHALL NOT persist generated quizzes; each request generates a new quiz from the material text.

#### Scenario: Repeated requests

- **WHEN** the same material is requested twice in a row
- **THEN** the system responds with a newly generated quiz each time and stores nothing

### Requirement: Quiz Answer Evaluation

The system SHALL evaluate a user's answers to the open questions of a generated quiz against the material text using the configured language model, and SHALL return a score and written feedback for each answer, without persisting the answers or the evaluation.

#### Scenario: Successful evaluation

- **WHEN** an authenticated user submits answers to open questions of a material they own
- **THEN** the system responds with `200` and a score and feedback for every submitted answer

#### Scenario: Empty answer

- **WHEN** a submitted answer is empty or blank
- **THEN** the system scores that answer zero and still returns feedback for it

#### Scenario: Another user's material

- **WHEN** the answers are submitted for a material that belongs to a different user
- **THEN** the system responds with `404`

#### Scenario: Unknown material

- **WHEN** the answers are submitted for a material identifier that does not exist
- **THEN** the system responds with `404`

#### Scenario: Language model unavailable

- **WHEN** the language model cannot be reached or returns an error
- **THEN** the system responds with `502` and no partial evaluation

#### Scenario: Malformed evaluation rejected

- **WHEN** the language model returns a score outside the allowed range or omits an answer
- **THEN** the system responds with `502` and does not return the malformed evaluation

#### Scenario: Nothing is stored

- **WHEN** the same answers are evaluated twice
- **THEN** the system evaluates them afresh each time and stores neither the answers nor the results
