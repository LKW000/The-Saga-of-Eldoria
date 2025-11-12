# The Saga of Eldoria: A Text-Based RPG

"The Saga of Eldoria" is a complete, self-contained, object-oriented text-based role-playing game (RPG) written purely in Python. It features a turn-based combat system, branching narrative choices, an inventory system, and three distinct endings.

## 🚀 How to Run the Game

1.  **Save the Code:** Save the entire Python code block (the contents of `main.py`) as a file named `main.py`.
2.  **Run from Terminal:** Open your terminal or command prompt, navigate to the directory where you saved `main.py`, and run the following command:
    ```bash
    python main.py
    ```
3.  **Play:** Follow the on-screen prompts for character creation and combat decisions.

## ⚙️ Core Structure and Modularity (OOP)

The game is built using Object-Oriented Programming (OOP) principles to ensure modularity and clean separation of game logic.

| Class/Module | Responsibility |
| :--- | :--- |
| **`Character`** | Base class for player and enemies. Manages core stats (Strength, Agility, Magic), health, and damage calculation. |
| **`Warrior`, `Mage`, `Rogue`** | Player subclasses extending `Character` with unique stat distributions and special abilities. |
| **`Item`** | Defines collectible items, their description, and the `use()` logic for applying effects. |
| **`Combat`** | Manages the turn-based battle flow, damage calculation, critical hits, dodging, and player/enemy actions. |
| **`World`** | Manages the linear story progression through distinct stages, handles narrative text, and processes non-combat branching choices. |

## 🧙 Character Classes & Stats

Players choose from three distinct classes, each with a unique ability:

* **Warrior:** High **Strength** (Physical Damage). Ability: **"Shield Bash"** (Guaranteed block + counter-damage).
* **Mage:** High **Magic** (Ability/Spell Power). Ability: **"Arcane Bolt"** (High-damage Magic attack with a low miss chance).
* **Rogue:** High **Agility** (Crit/Dodge Chance). Ability: **"Sneak Attack"** (High critical hit chance).

**Stat Effects:**
* **Strength:** Multiplies physical damage (`Attack` action).
* **Magic:** Multiplies ability damage (`Magic` action).
* **Agility:** Increases the base chance for a critical hit and affects the enemy's dodge chance.

## ⚔️ Combat System

Combat is turn-based and involves random elements (simulated dice rolls, `random.randint(1, 6)`) multiplied by the relevant character stat.

| Player Action | Description |
| :--- | :--- |
| **Attack** | Standard physical damage, scaled by **Strength**. |
| **Defend** | Reduces incoming damage by 50% for the next enemy turn. |
| **Magic** | Uses the player's unique class ability, scaled by **Magic**. |
| **Item** | Opens the inventory for using consumables. |

## 🗺️ Story and Endings

The game progresses through three main stages with critical choice points that affect the player's stats, inventory, and ultimately, the final outcome.

| Stage | Main Encounter | Key Choice |
| :--- | :--- | :--- |
| **1: Haunted Forest** | Minor Bandit | **Heal/Ignore** injured creature (Leads to a permanent, small stat boost). |
| **2: Bandit's Lair** | Bandit King (Boss) | **Explore/Ignore** hidden passage (Leads to a unique, permanent weapon/artifact). |
| **3: Enchanted Castle** | Arch-Lich (Final Boss) | **Fight/Bargain/Betray** (Leads to one of three distinct endings). |

**Distinct Endings:**
1.  **Heroic Victory:** Defeat the Final Boss in standard combat.
2.  **Diplomatic Alliance:** Successfully bargain with the boss (requires a **Magic** stat check or having the *Arcane Focus* item).
3.  **The Dark Lord:** Betray your quest and accept the boss's power (requires a **low HP/desperation** trigger).

## 🛡️ Error and Edge Case Handling

The game includes robust input handling to prevent crashes from invalid user input.

* **Invalid Input:** Any non-existent command or choice prompts the user with: `"A moment of confusion, adventurer. That command is not understood."`
* **Health Check:** Player death (`HP <= 0`) is explicitly checked after every damage instance, leading to a unique loss message.