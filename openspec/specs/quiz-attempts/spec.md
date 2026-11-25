# quiz-attempts Specification

## Purpose

Lets a user submit answers to a stored quiz, keeps every attempt with its answers and scores, and returns the attempt history so progress over a material can be read back later.

## Requirements

### Requirement: Attempt Creation

The system SHALL create an attempt for a stored test that belongs to the current user, and SHALL persist exactly one answer per question of that test whether or not the user answered it.

#### Scenario: Attempt is created

- **WHEN** an authenticated user submits answers for a test they own
- **THEN** the system responds with `201` and an identifier of the created attempt, and stores one answer row for every question of the test

#### Scenario: Unanswered questions are stored

- **WHEN** the submission omits an answer for some questions of the test
- **THEN** the attempt is still created and each omitted question is stored as unanswered rather than rejected

#### Scenario: Another user's test

- **WHEN** the submitted test belongs to a different user
- **THEN** the system responds with `404` and stores no attempt

#### Scenario: Unknown test

- **WHEN** the submitted test identifier does not exist
- **THEN** the system responds with `404` and stores no attempt

#### Scenario: Repeated submissions create separate attempts

- **WHEN** the same test is submitted twice
- **THEN** the system stores two independent attempts and neither replaces the other

### Requirement: Multiple-Choice Grading

The system SHALL grade every multiple-choice question of an attempt against the correct option stored with that question, without calling the language model, and SHALL count a question without an answer as incorrect.

#### Scenario: Correct and incorrect answers

- **WHEN** an attempt contains multiple-choice answers, some matching the stored correct option and some not
- **THEN** each answer is recorded as correct or incorrect according to the stored option and the attempt reports how many were correct out of how many multiple-choice questions it holds

#### Scenario: Unanswered question counts as incorrect

- **WHEN** a multiple-choice question is left unanswered at submission
- **THEN** it is recorded as incorrect and included in the total

#### Scenario: Grading needs no model

- **WHEN** the language model is unreachable or not configured
- **THEN** creating an attempt and grading its multiple-choice questions still succeeds

#### Scenario: Test without multiple-choice questions

- **WHEN** the submitted test contains only open questions
- **THEN** the attempt is created with a multiple-choice total of zero and no grade is invented

### Requirement: Open Answer Evaluation

The system SHALL evaluate the open answers stored in an attempt against the material text and the reference answers stored with those questions, and SHALL persist a score and written feedback for each evaluated answer.

#### Scenario: Evaluation succeeds

- **WHEN** an authenticated user asks to check an attempt containing answered open questions
- **THEN** the system responds with `200` and a score and feedback for every open question of the attempt, and keeps both with the attempt

#### Scenario: Empty answer is not sent to the model

- **WHEN** an open question of the attempt has no answer
- **THEN** the system scores it zero with explanatory feedback and sends nothing about it to the language model

#### Scenario: Language model unavailable

- **WHEN** the language model cannot be reached or returns an error
- **THEN** the system responds with `502` and the attempt keeps the answers already stored, with no partial evaluation written

#### Scenario: Malformed evaluation rejected

- **WHEN** the language model returns a score outside the allowed range or omits an answer
- **THEN** the system responds with `502` and writes no evaluation

#### Scenario: Repeated check overwrites

- **WHEN** the check is requested twice for the same attempt
- **THEN** the answers are evaluated afresh and the stored scores and feedback are replaced by the new ones

#### Scenario: Another user's attempt

- **WHEN** the requested attempt belongs to a different user
- **THEN** the system responds with `404`

### Requirement: Attempt History

The system SHALL list the attempts owned by the current user newest first and SHALL return a single attempt together with its questions, the answers given, the correct options and any stored feedback.

#### Scenario: History is listed

- **WHEN** the user owns several attempts
- **THEN** the response contains only that user's attempts, newest first, each naming its test, material and multiple-choice score

#### Scenario: Empty history

- **WHEN** the current user has no attempts
- **THEN** the system responds with `200` and an empty array

#### Scenario: Attempt detail

- **WHEN** the user requests an attempt they own
- **THEN** the response shows every question of its test with the answer given, the correct option for multiple-choice questions and the stored score and feedback for open ones

#### Scenario: Another user's attempt

- **WHEN** the requested attempt belongs to a different user
- **THEN** the system responds with `404` without revealing that the attempt exists

#### Scenario: Unknown attempt

- **WHEN** the requested attempt identifier does not exist
- **THEN** the system responds with `404`
