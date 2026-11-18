# Spec Delta

## Purpose

Exposes an unauthenticated availability probe so the deployment environment and developers can tell whether the service is up before any account exists.

## ADDED Requirements

### Requirement: Health Probe

The system SHALL expose a health endpoint that reports service availability without requiring authentication.

#### Scenario: Probe without a token

- **WHEN** `GET /health` is called without an `Authorization` header
- **THEN** the system responds with `200` and a body containing `status` equal to `ok`

#### Scenario: Reachable on an empty database

- **WHEN** the service has just started and no accounts or materials exist
- **THEN** `GET /health` still responds with `200`
