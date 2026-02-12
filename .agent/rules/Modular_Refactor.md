---
trigger: manual
---

# MODULAR REFACTOR & SOLID RULES

Activate this rule when performing structural refactorings or decoupling monolith classes (like Robot.cs). Focus on making the codebase "extension-friendly" without adding feature bloat.

# CORE PRINCIPLES
- **Component-Level Responsibility:** Break monoliths into small, logic-specific components (e.g., `HealthSystem`, `EnergySystem`, `SkillController`).
- **Interface Decoupling:** Use interfaces for all cross-system interactions. 
    - Use `IDamageable` for HP updates.
    - Use `IEnergyUser` for energy consumption.
    - Use `IStatusEffectTarget` for buff/debuff management.
- **Event-Driven Architecture:** Prefer C# Events or UnityEvents for cross-component communication to avoid direct `GetComponent<T>()` dependencies where possible.
- **Composition over Inheritance:** Avoid deep class hierarchies. Use components to add functionality to GameObjects.

# REFACTORING WORKFLOW
1. **Identify Monoliths:** Any class over 200 lines or handling more than 3 distinct systems (HP, AI, VFX, Movement) belongs here.
2. **Define Interfaces:** Extract the essential interactions into interfaces.
3. **Migrate Logic:** Move code blocks into separate components while keeping the original class as a "Shell" or "Coordinator" for backwards compatibility during transition.
4. **Data vs Logic:** Ensure ScriptableObjects only hold static configuration. Runtime state must live in Monobehaviour components.

# CODING STANDARDS (Modular)
- **Explicit Inits:** Use `Initialize()` methods instead of relying solely on `Awake/Start` for component dependencies.
- **Property Injection:** If Component A needs Component B, pass it in via an `Initialize` or setter rather than searching for it.
- **Stat System:** Implement a generic `Stat` class/struct to handle modifiers (Flat/Percent) instead of hardcoding math in `Robot.cs`.

# NEXT STEP PROTOCOL
- When refactoring, always start with the **Interfaces**.
- Provide 1 unit test or "Interaction Proof" for the new modular structure.
- DO NOT add new gameplay mechanics during the refactor phase.
