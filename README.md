# 🚀 NexusAI

> **An AI-Powered Study Operating System for Software Engineering Students**

NexusAI is a production-grade AI study platform built with **Python** and **Streamlit** that transforms scattered learning into a structured, intelligent workflow.

Unlike a traditional chatbot, NexusAI functions as a **Study Operating System**, combining AI tutoring, mission planning, gap analysis, productivity tracking, and technical interview preparation into one unified workspace.

---

# 🌟 Vision

Learning software engineering involves far more than solving coding problems.

Students need to:

* Know what to study
* Identify weak concepts
* Plan their day
* Stay focused
* Practice interviews
* Track long-term improvement

NexusAI unifies all of these into one intelligent platform.

---

# ✨ Current Features

## 🏠 Command Center

The Command Center acts as the central dashboard of NexusAI.

It provides:

* Active Mission
* AI Recommendations
* Study Overview
* Navigation Hub
* Daily Intelligence
* Learning Status

The application uses a **state-driven routing architecture**, allowing each module to behave like a dedicated application while sharing the same AI Brain.

---

## 🧠 AI Brain

The AI Brain synchronizes learning across the platform.

Current responsibilities include:

* Current Learning Focus
* Recommended Topic
* Current Module
* Last Activity
* Mission Synchronization

Every major module communicates with the AI Brain, enabling context-aware recommendations throughout the application.

---

## 💬 Study Chat

An AI-powered study assistant designed specifically for software engineering students.

Capabilities include:

* Context-aware conversations
* DSA guidance
* Java and Python assistance
* Algorithm explanations
* Debugging support
* Scaler curriculum support
* Career guidance

The assistant follows structured teaching principles:

* First Principles
* Brute Force → Optimal
* Intuition before Implementation
* Verification Questions
* Honest Feedback

---

## 🎯 GapFinder

GapFinder identifies weak concepts through deliberate practice.

Features:

* AI-generated DSA problems
* Topic selection
* Weak topic recommendations
* Strict evaluation
* Gap logging
* Progress tracking
* AI-powered recommendations
* Automatic synchronization with the AI Brain

Topics currently supported:

* Prefix Sum
* Sliding Window
* Contribution Technique
* Bit Manipulation
* 2D Matrices
* Strings

---

## ⚡ FlowState

FlowState is the productivity engine of NexusAI.

Capabilities include:

* AI Daily Planner
* Priority Management
* Mission Integration
* Deep Work Sessions
* Focus Timer
* Mid-Day Replanning
* End-of-Day Review
* Productivity Analytics

The module automatically synchronizes with:

* AI Brain
* Mission Engine
* Daily Logs

---

## 🎤 Mock Interview

A production-style technical interview simulator.

Features:

### Interview Setup

* Company Type
* Target Role
* Difficulty
* Interview Topic

### Live Interview

* AI-generated questions
* Interview Timer
* Coding Workspace

### Candidate Workspace

Candidates submit:

* Clarification Questions
* Brute Force Solution
* Optimal Solution
* Time Complexity
* Space Complexity
* Final Code

### AI Evaluation

Evaluation categories include:

* Problem Understanding
* Communication
* Algorithm Selection
* Optimization
* Complexity Analysis
* Code Quality
* Edge Cases
* Hiring Decision

Final verdicts:

* Strong Hire
* Hire
* Lean Hire
* Lean No Hire
* No Hire

Interview history and analytics are automatically stored.

---

## 🎯 Mission Engine

The Mission Engine generates daily learning objectives.

Features:

* AI-driven mission generation
* Progress tracking
* Mission lifecycle
* Active Mission
* Completed Missions
* Automatic synchronization with AI Brain

---

# 🏗 Architecture

NexusAI follows a modular production architecture.

```
Command Center
        │
        ▼
    AI Brain
        │
 ┌──────┼───────────────┐
 │      │               │
 ▼      ▼               ▼
Study  GapFinder    FlowState
Chat
 │      │               │
 └──────┼───────────────┘
        │
        ▼
Mock Interview
        │
        ▼
JSON Persistence
```

---

# 🧩 Recent Architecture Improvements

The project recently underwent a major production refactor.

## ✅ State-Driven Routing

Navigation is now controlled through application state rather than rendering every page simultaneously.

Benefits:

* Cleaner architecture
* Faster rendering
* Better module isolation

---

## ✅ Centralized Session Initialization

All `st.session_state` initialization has been consolidated into a single initialization function.

Benefits:

* Reduced duplication
* Easier maintenance
* Fewer runtime errors

---

## ✅ Unified Timer Engine

A shared timer system powers:

* FlowState
* GapFinder
* Mission Engine
* Mock Interview

Benefits:

* Consistent behavior
* Reduced duplicate code
* Easier future expansion

---

## ✅ Centralized Database Layer

Database save operations are now abstracted through helper functions.

Benefits:

* Cleaner code
* Consistent persistence
* Reduced duplication

---

## ✅ Modular Rendering

Each feature renders independently.

Benefits:

* Better state isolation
* Improved scalability
* Easier debugging

---

# 💾 Persistence

NexusAI stores:

* Missions
* Day Logs
* Gap Logs
* Interview History
* AI Brain State
* Learning Progress

Data is synchronized through a centralized persistence layer.

---

# 🛠 Tech Stack

Frontend

* Streamlit

Backend

* Python

AI

* Groq API
* Llama 3.1 8B Instant

Persistence

* JSONBin

Architecture

* State-Driven Routing
* Centralized Session Management
* Unified Timer Engine
* Centralized Database API

---

# 📈 Current Development Status

| Module         | Status       |
| -------------- | ------------ |
| Command Center | ✅ Production |
| AI Brain v1    | ✅ Production |
| Study Chat     | ✅ Production |
| GapFinder      | ✅ Production |
| FlowState      | ✅ Production |
| Mock Interview | ✅ Production |
| Mission Engine | ✅ Production |
| Dashboard v2   | 🚧 Next      |
| AI Brain v2    | 📅 Planned   |
| Placement OS   | 📅 Planned   |

---

# 🚀 Roadmap

## Phase 1 ✅

* Command Center
* Study Chat
* GapFinder
* FlowState
* Mock Interview
* Mission Engine

---

## Phase 2 🚧

Dashboard v2

* Learning Analytics
* Progress Visualization
* Productivity Dashboard
* Mission Insights
* AI Recommendations

---

## Phase 3

AI Brain v2

* Mastery Scores
* Revision Queue
* Learning Momentum
* Interview Readiness
* Confidence Score
* Adaptive Recommendations

---

## Phase 4

Placement OS

* Company Tracker
* Resume Manager
* Application Tracker
* Interview Pipeline
* Offer Tracker
* Career Roadmap

---

# 🎯 Project Goal

NexusAI is designed to become a complete AI-powered learning and career operating system for software engineering students.

Rather than replacing existing learning platforms, NexusAI acts as the intelligent layer that connects learning, planning, revision, productivity, and interview preparation into one unified experience.

---

# 👨‍💻 Author

**Shivang**

Built as a personal AI-powered Software Engineering Study Operating System with the vision of evolving into a production-grade adaptive learning platform.
