# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture and Structure

This repository appears to contain a Python application, likely containerized using Docker, for energy analysis.

- **`app.py`**: Contains the core application logic for the energy analysis.
- **`requirements.txt`**: Lists the Python dependencies needed for the application.
- **`Dockerfile`**: Defines the environment and steps to build the application container.
- **`docker-compose.yml`**: Defines the services required to run the application, including dependencies.

## Development Workflow

The recommended workflow revolves around Docker Compose for environment setup and Docker for application execution.

### Environment Setup

To set up the development and production environment, use Docker Compose:
- To build and start the services (including the application):
  `docker-compose up --build`

### Running the Application

To run the application and interact with it:
- To run the application in detached mode using the defined services:
  `docker-compose up -d`

### Running a Single Test

Since no explicit testing framework files were found, assume standard Python testing practices. If tests are implemented in the project, they are likely discoverable via a standard runner:
- To run all tests (if a test command exists, e.g., `pytest`):
  `pytest`