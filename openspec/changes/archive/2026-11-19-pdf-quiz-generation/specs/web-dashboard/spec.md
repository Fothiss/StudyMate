# Spec Delta

## MODIFIED Requirements

### Requirement: Material Upload From Dashboard

The client SHALL let an authenticated user upload a `.pdf` file together with a title directly from the dashboard.

#### Scenario: Successful upload

- **WHEN** the user submits a supported file and a non-empty title
- **THEN** the material is accepted and appears in the materials block

#### Scenario: Unsupported file type

- **WHEN** the API answers `415`
- **THEN** the block shows a readable message naming the accepted format and the list is unchanged

#### Scenario: File too large

- **WHEN** the API answers `413`
- **THEN** the block shows a readable message naming the size limit and the list is unchanged

#### Scenario: Material rejected by the API

- **WHEN** the API answers `422` because the PDF has no text layer or exceeds the token limit
- **THEN** the block shows a readable message and the list is unchanged

#### Scenario: Empty title

- **WHEN** the title is empty
- **THEN** the client reports it next to the field and sends no request

#### Scenario: Original filename is shown

- **WHEN** a material is listed
- **THEN** the original filename the user uploaded is displayed with it

## REMOVED Requirements

### Requirement: Unavailable Sections Explained

**Reason**: Секция «Тесты» перестала быть заглушкой: по материалу теперь генерируются вопросы, поэтому требование о недоступности относится только к «Результатам».

**Migration**: Правило о «Результатах» переехало в требование `Results Section Explained`, работающая секция «Тесты» описана в `Quiz Generation From Dashboard`. Других потребителей у этого требования нет.

## ADDED Requirements

### Requirement: Results Section Explained

The client SHALL present the results section as unavailable and SHALL NOT offer controls in it that cannot work.

#### Scenario: Results section

- **WHEN** the dashboard renders
- **THEN** the results section explains that results appear after a first completed test and contains no actionable control

### Requirement: Quiz Generation From Dashboard

The client SHALL let an authenticated user generate a quiz for one of their materials from the dashboard and SHALL display the summary and questions returned by the API.

#### Scenario: Material selection

- **WHEN** the user owns materials
- **THEN** each material can be chosen as the quiz source and the most recent one is chosen by default

#### Scenario: Generation pending

- **WHEN** a generation request is in flight
- **THEN** the trigger is disabled and a waiting indication is shown instead of an empty result

#### Scenario: Quiz displayed

- **WHEN** the API answers `200`
- **THEN** the block shows the summary points and every question with all of its options

#### Scenario: Correct answer identifiable

- **WHEN** a generated question is displayed
- **THEN** its correct option is visually distinguishable from the others

#### Scenario: No materials to work with

- **WHEN** the user owns no materials
- **THEN** the block explains that a material must be uploaded first and offers no generation control

#### Scenario: Generation fails

- **WHEN** the API answers `502` or the request fails
- **THEN** the block shows a readable message and no partial quiz

#### Scenario: Material cannot produce a quiz

- **WHEN** the API answers `422`
- **THEN** the block shows a readable message and no partial quiz
