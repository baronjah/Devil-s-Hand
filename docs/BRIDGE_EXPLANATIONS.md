# Bridge Explanations — Devil's Hand Ecosystem

This document serves as the "Source of Truth" for how different dimensions and services are wired together.

## 1. Claude's Dimension (The Phone Interfaces)
*   **Port 8080 (Phone AI):** 
    *   *What:* A direct chat interface for mobile.
    *   *Where:* `D:\AI_COORDINATION\phone_ai.py`
    *   *Purpose:* Fast, choice-based interaction. It captures the user's initial "messy" prompts.
*   **Port 8003 (Timer Game):**
    *   *What:* An SSE-based decision loop.
    *   *Where:* `D:\AI_COORDINATION\game.py`
    *   *Purpose:* Creating tension and immediate story progression. It drives the "Train Loop" pace.
*   **Port 8002 (Brain Graph):**
    *   *What:* A graph-based context database.
    *   *Where:* `D:\AI_COORDINATION\brain.py`
    *   *Purpose:* Storing the "Neural Network" of the conversation history.

## 2. Gemini's Dimension (The Ecosystem Core)
*   **Port 8010 (Devil's Hand):**
    *   *What:* The unified backend and orchestrator.
    *   *Where:* `D:\devil_s_hand\devils_hand_main.py`
    *   *Purpose:* Monitoring the filesystem (Paranoia), versioning (VersionTracker), and visualizing the world (Godot).

## 3. The Bridge Rules
*   **Verification:** Before using any service, the Hand checks the port status. 
*   **Creation:** If a required script or folder is not found in a dimension, the `DimensionExplorer` is triggered to "Reconstruct" it from the `SwissKnifeSchema`.
*   **Branching:** If a script exists (e.g., `NeuralHandshake.gd`) but we need it to behave differently for a specific story beat, we do NOT overwrite it. Instead, we create a **Special Case Branch** (e.g., `NeuralHandshake.special_case_001.gd`) and link it in the `VersionTracker`.

## 4. Visual Skill Contract
*   Every Python script that modifies a file is a **Skill**.
*   **Simulation Mode:** The visual logic is played at "Play Mode" speed (readable).
*   **Production Mode:** The animation is sped up for a smooth, powerful feel.
