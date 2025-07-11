# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**podbot** is a podcast generation tool that automates podcast creation. The tool will consist of a web frontend, where users will come and signup for the service. Upon signing up, they will get a custom podcast RSS feed creator for them, with a single episode in the feed, which is a very short podcast welcoming them to podbot, and describing what it will do for them. Signing up with also require OAuth authentication with Google Docs and Google Caledar. Maybe in the future we'll add Gmail and other sources of information.

Immediately after signing up, and every morning (very early) it will generate a podcast for that user. It will start with a summary of the day, based on the user's calendar. If there is a reasonably small number of meetings, it can give details on all the meetings for the day. If there are a lot of meetings, it should do more of a summary, describing when they get started, the nature of the meetings, whether there's breaks, if there's travel to new locations, and anything notable about the day's schedule. This calendar module can be it's own item on the podcast feed.

Next it will take a look at all the documents shared with the user from the previous day, prioritizing those that are included as attachments (or links) in calendar entries. It should summarize the overall set of documents. This is a new item in the podcast feed.

Then each document, can be described in podcast form, in a longer form.

Eventually we may want to have these be custom modules tweaked by the user, reordered etc, but we can start simply for now. Each of these may need it's own rich prompt to pass to an AI model to get the kind of podcast we want, and maybe eventually there will be ways for the user to tweak those prompts (but that can be future work).


## Current State

The repository is in its initial state with:
- Basic project structure established
- MIT License 
- Minimal README describing the project purpose
- No source code, dependencies, or build configuration yet

## Development Setup

- Python-based implementation for audio processing and AI integration. We'll use OpenAI for LLM calls to generate the podcast scripts. We'll then also use OpenAI's audio libraries to generate the podcast audio.
- Python can generally be used for the offline batch processing, creating the podcasts for each user.
- Node.js/TypeScript for web-based interfaces and API development
- Google Cloud, possibly Firebase (if it makes sense), is where we'll deploy.

## Architecture Notes

The codebase will likely need to handle:
- Audio processing and generation
- Content creation and scripting
- Podcast metadata management
- Export and distribution workflows

## Development Commands

```bash
# Start development environment
make dev

# Install dependencies
make install

# Run tests
make test

# Build application
make build

# Set up environment file
make setup-env

# Docker commands
make docker-up
make docker-down
make docker-build
```

## Development Environment

The project uses Docker Compose for local development with:
- FastAPI backend on port 8000
- Next.js frontend on port 3000
- PostgreSQL database on port 5432

## Core Architecture

### Backend Structure
- `backend/main.py`: FastAPI application entry point
- `backend/models.py`: SQLAlchemy database models
- `backend/database.py`: Database configuration and session management
- `backend/config.py`: Application configuration using Pydantic settings

### Frontend Structure
- `frontend/app/`: Next.js 13+ app directory structure
- `frontend/app/page.tsx`: Landing page component
- `frontend/app/layout.tsx`: Root layout with global styles

### Key Integration Points
- Google OAuth for Calendar and Docs access
- OpenAI API for content generation and TTS
- PostgreSQL for user data and podcast metadata
- RSS feed generation for podcast distribution

## Environment Configuration

Required environment variables:
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`: Google OAuth credentials
- `OPENAI_API_KEY`: OpenAI API key
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: PostgreSQL connection string