# material-quiz Specification

## Purpose

Lets a user obtain a short summary and multiple-choice questions generated from the text of their own uploaded material, so they can test their knowledge without writing questions by hand.

## Requirements

### Requirement: Quiz Generation

The system SHALL generate a quiz for a material owned by the current user from its extracted text using the configured language model, take the requested numbers of multiple-choice and open questions, store the quiz, and SHALL respond with its identifier and questions without revealing correct options or reference answers.

#### Scenario: Successful generation

- **WHEN** an authenticated user requests a quiz for a material they own that has extracted text
- **THEN** the system responds with `200` and a body containing a non-empty summary, a non-empty list of questions and a test identifier

#### Scenario: Correct answers are withheld

- **WHEN** a generated quiz is returned to the client before the test is submitted
- **THEN** the response carries no correct option, no index of the correct option and no reference answer for any question

#### Scenario: Generated quiz is stored

- **WHEN** a quiz is generated successfully
- **THEN** the system stores the quiz with its questions, answer options and reference answers, and the stored quiz belongs to the requesting user

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

### Requirement: Generated Quiz Structure

The system MUST validate the language model response before storing it: the quiz has at least one question, every multiple-choice question offers at least two options with a correct answer index pointing at an existing option, and every open question carries a non-empty reference answer, and the validated answer data SHALL be stored with the quiz and SHALL NOT be returned to the client.

#### Scenario: Valid quiz returned

- **WHEN** the language model returns a summary and questions whose kinds and answer data are well formed
- **THEN** the system responds with `200`, stores the correct option index of every multiple-choice question and the reference answer of every open question, and returns every question with its kind and the options needed to answer it

#### Scenario: Malformed quiz rejected

- **WHEN** the language model returns no questions, a multiple-choice question with fewer than two options, an out-of-range answer index, or an open question without a reference answer
- **THEN** the system responds with `502` and does not return the malformed quiz
