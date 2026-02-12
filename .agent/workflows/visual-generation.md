---
description: Generates high-fidelity images for Ohm-Yura using a two-stage prompt engineering process (Visual Prompt Maker -> Visual Maker).
---

# Visual Generation Workflow (Ink & Rust Edition)

This workflow combines the `visual-prompt-maker` (for stylized asset prompts) and `visual-maker-protocol` (for art direction) to generate **game-ready assets**.

## Step 1: Analyze Request & Asset Type
1.  **Identify Asset Class:** Is the user asking for an **ICON** (UI), a **SPRITE** (Character/Object), or a **BACKGROUND** (Concept/World)?
2.  **Check Visual DNA:** Ensure the requested subject fits the "Ohm-Yura" world (Decayed tech, retro-futurism, rust).
3.  **Consult `visual-maker-protocol.md`:** Inject the "Master Style String" (Mignola/Eastward/Ashley Wood keywords).

## Step 2: Prompt Engineering
1.  **Construct 3 Variations** based on the Asset Class (as defined in `visual-prompt-maker.md`):
    *   **Game Icon:** Simplified, discernible at small sizes, thick lines.
    *   **Sprite/Character:** Clear silhouette, neutral background for easy cutting.
    *   **Concept Art:** Full composition, atmospheric richness.
2.  **Color Theory Check:** Verify that the prompt includes the "Ohm Palette" (Teal/Orange/Black/Cyan) instructions.
3.  **Negative Prompting:** *Crucial Step*. Ensure "3D", "Photorealistic", and "Render" are explicitly excluded in the prompt or negative prompt field.

## Step 3: User Selection & Generation
1.  Present the table to the user.
2.  Ask relevant clarifying questions:
    *   "Should lines be thicker for small screens?"
    *   "Is this strictly 2D or should it simulate depth?"
3.  **Call `generate_image`** with the selected prompt.

## Step 4: Quality Check (The "Hand-Drawn" Test)
1.  **Review the Output:**
    *   Does it look like a drawing/painting? (Pass)
    *   Does it look like a 3D model? (Fail -> Retry with stronger "2D" weights).
    *   Are the shadows "spotted blacks"? (Pass).
2.  **Context Check:** Does it feel like it belongs in the world of Ohm-Yura?
