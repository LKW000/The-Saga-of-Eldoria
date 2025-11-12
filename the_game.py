# main.py - The Saga of Eldoria: A Text-Based RPG

import random
import sys

# --- 1. Core Structure and Modularity Demand (OOP Classes) ---

class Character:
    """
    Base class for all characters (Player and Enemies) in the game.
    Handles stats, health, and basic combat state.
    """
    def __init__(self, name, strength, agility, magic, max_hp, ability_name):
        # Core attributes
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.strength = strength  # Physical damage multiplier
        self.agility = agility    # Affects hit/dodge chance and critical hit
        self.magic = magic        # Magical damage multiplier
        self.ability_name = ability_name # Unique class ability name

        # Combat state attributes
        self.is_defending = False
        self.temp_defense_buff = 0 # Used by Scroll of Protection
        self.inventory = {} # Dictionary to store items: {Item_name: Item_object}
        self.weapon_boost = 0 # Permanent stat boost from unique item

    def take_damage(self, damage):
        """Calculates and applies damage, considering defense state."""
        # Check for defense state
        if self.is_defending:
            damage = max(1, damage // 2) # Halve damage, but ensure at least 1 is taken
            print(f"**{self.name}** is defending and reduces the damage!")
            self.is_defending = False # Defense only lasts one turn

        # Check for temporary defense buff (e.g., Scroll of Protection)
        damage = max(1, damage - self.temp_defense_buff)
        if self.temp_defense_buff > 0:
            print(f"The protective aura absorbs {self.temp_defense_buff} damage!")
            self.temp_defense_buff = 0 # Temporary buff expires after one turn

        self.current_hp -= damage
        self.current_hp = max(0, self.current_hp)
        return damage

    def heal(self, amount):
        """Restores a fixed amount of HP."""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        print(f"{self.name} healed for {amount} HP. Current HP: {self.current_hp}/{self.max_hp}.")

    def get_stats(self):
        """Returns a formatted string of the character's current stats."""
        stats_str = (
            f"**{self.name} Stats**\n"
            f"  HP: {self.current_hp}/{self.max_hp}\n"
            f"  Strength: {self.strength + self.weapon_boost}\n" # Include permanent boost
            f"  Agility: {self.agility}\n"
            f"  Magic: {self.magic}\n"
            f"  Ability: {self.ability_name}\n"
            f"  Inventory: {', '.join(self.inventory.keys()) or 'Empty'}"
        )
        return stats_str

# --- 2. Character Creation Requirements (Player Subclasses) ---

class Warrior(Character):
    """A Warrior is a physical fighter with high Strength and a defensive ability."""
    def __init__(self, name):
        super().__init__(name, strength=14, agility=8, magic=5, max_hp=120, ability_name="Shield Bash")

class Mage(Character):
    """A Mage relies on high Magic power and a powerful, though sometimes unreliable, spell."""
    def __init__(self, name):
        super().__init__(name, strength=6, agility=9, magic=15, max_hp=90, ability_name="Arcane Bolt")

class Rogue(Character):
    """A Rogue is fast and relies on Agility for critical hits."""
    def __init__(self, name):
        super().__init__(name, strength=10, agility=13, magic=7, max_hp=100, ability_name="Sneak Attack")

# --- 5. Inventory and Item System (Item Class) ---

class Item:
    """Defines an item with a name, description, and an effect method."""
    def __init__(self, name, description, effect_func=None):
        self.name = name
        self.description = description
        self.effect = effect_func # A function that defines the item's use logic

    def use(self, target):
        """Execute the item's effect on a target (usually the player)."""
        if self.effect:
            self.effect(target)
            print(f"**{target.name}** used **{self.name}**! {self.description}")
            return True
        return False

# Item Effect Functions (Define logic outside the class for modularity)
def use_health_potion(player):
    """Restores a fixed amount of HP."""
    player.heal(40) # Fixed amount of HP restoration
    print("A warm glow spreads through you, mending your wounds.")

def use_scroll_of_protection(player):
    """Grants a temporary defense buff (lasts one combat turn)."""
    player.temp_defense_buff = 15 # Set the temporary defense value
    print("The scroll disintegrates, leaving a shimmering magical shield around you.")

def use_elven_blade(player):
    """A permanent boost to Strength. Only used once."""
    if not player.weapon_boost:
        player.weapon_boost = 5 # Permanent Strength boost
        player.strength += 5
        print("You equip the **Elven Blade**. A surge of power runs through you! **+5 Strength**.")
    else:
        print("You already have a legendary weapon and cannot equip another.")

# Initialize the required items
HEALTH_POTION = Item("Health Potion", "Restores 40 HP.", use_health_potion)
SCROLL_PROTECTION = Item("Scroll of Protection", "Grants +15 temporary defense for the next turn.", use_scroll_of_protection)
ELVEN_BLADE = Item("Elven Blade", "A legendary weapon granting a permanent +5 Strength boost.", use_elven_blade)
ARCANE_FOCUS = Item("Arcane Focus", "An ancient artifact granting a permanent +5 Magic boost.", lambda p: (setattr(p, 'magic', p.magic + 5), setattr(p, 'weapon_boost', 5), print("The **Arcane Focus** enhances your mind! **+5 Magic**.")) if not p.weapon_boost else print("You already have a legendary weapon and cannot equip another."))

# --- 4. Turn-Based Combat System (Combat Class) ---

class Combat:
    """Manages the turn-based combat sequence between a player and an enemy."""
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def _calculate_damage(self, attacker, defender, stat_multiplier, is_magic=False):
        """
        Core damage calculation logic, including random element (dice roll)
        and critical hit/dodge chance based on Agility.
        """
        # Base damage is a d6 multiplied by the relevant stat
        base_damage = random.randint(1, 6) * stat_multiplier

        # Agility Check: Critical Hit Chance (5% base + Agility/10)
        crit_chance = 5 + attacker.agility / 10 # Example: 5% + 1.4% = 6.4%
        is_crit = random.randint(1, 100) <= crit_chance
        if is_crit:
            base_damage *= 2
            print(">>> CRITICAL HIT! <<<")

        # Agility Check: Dodge Chance (Enemy Agility affects player's hit chance)
        dodge_chance = defender.agility / 5 # Example: 8/5 = 1.6% dodge chance
        if random.randint(1, 100) <= dodge_chance:
            print(f"**{defender.name}** expertly dodged the attack!")
            return 0 # No damage

        # Apply damage to the defender
        damage_taken = defender.take_damage(int(base_damage))
        damage_type = "Magic" if is_magic else "Physical"
        print(f"**{attacker.name}** strikes **{defender.name}** for {damage_taken} {damage_type} damage!")
        return damage_taken

    def _player_attack(self):
        """Handles the player's standard physical attack action."""
        # Use player's Strength, including any permanent weapon boost
        effective_strength = self.player.strength + self.player.weapon_boost
        self._calculate_damage(self.player, self.enemy, effective_strength, is_magic=False)

    def _player_defend(self):
        """Sets the player's defense state for the next enemy turn."""
        self.player.is_defending = True
        print(f"**{self.player.name}** braces for the incoming attack. Damage will be reduced next turn.")

    def _player_magic(self):
        """Handles the player's unique class ability."""
        # Check if the player has any temporary defense from scrolls to reset
        self.player.temp_defense_buff = 0

        ability = self.player.ability_name
        if ability == "Shield Bash":
            # Warrior: Guaranteed block + small counter-damage
            print(f"**{self.player.name}** prepares a **{ability}**!")
            self.player.is_defending = True # Guaranteed block/defense for the enemy's turn
            
            # Counter-attack: (d6 * Strength / 2)
            counter_damage = random.randint(1, 6) * (self.player.strength + self.player.weapon_boost) // 2
            damage_taken = self.enemy.take_damage(max(1, counter_damage))
            print(f"The shield bash strikes for {damage_taken} physical damage and leaves **{self.player.name}** ready to defend.")
        
        elif ability == "Arcane Bolt":
            # Mage: High-damage Magic attack with a low chance to miss (Agility-based miss)
            print(f"**{self.player.name}** channels a powerful **{ability}**!")
            # 10% chance to miss for the Arcane Bolt, regardless of enemy Agility
            if random.randint(1, 100) <= 10:
                print("The Arcane Bolt fizzles! It misses the target!")
                return
            
            # High-damage: (d6 * Magic * 1.5)
            effective_magic = int(self.player.magic * 1.5)
            self._calculate_damage(self.player, self.enemy, effective_magic, is_magic=True)

        elif ability == "Sneak Attack":
            # Rogue: High critical hit chance (20% base crit chance)
            print(f"**{self.player.name}** attempts a deadly **{ability}**!")
            base_damage = random.randint(1, 6) * (self.player.strength + self.player.weapon_boost)
            
            # High critical chance for this move
            is_crit = random.randint(1, 100) <= 20 + (self.player.agility / 10)
            if is_crit:
                base_damage *= 2
                print(">>> A DEADLY CRITICAL SNEAK ATTACK! <<<")
            
            damage_taken = self.enemy.take_damage(int(base_damage))
            print(f"The sneak attack hits **{self.enemy.name}** for {damage_taken} physical damage!")

    def _player_use_item(self):
        """Allows the player to use an item from their inventory."""
        if not self.player.inventory:
            print("Your inventory is empty, adventurer.")
            return

        while True:
            item_list = ', '.join(self.player.inventory.keys())
            print(f"\n--- Inventory: {item_list} ---")
            item_name = input("Use which item? (Type 'cancel' to return): ").strip().title()

            if item_name == 'Cancel':
                print("Action cancelled.")
                return False # Indicate that the turn was not spent

            if item_name in self.player.inventory:
                item = self.player.inventory[item_name]
                # Check if the item is a permanent boost item that has already been used
                if item_name in ("Elven Blade", "Arcane Focus") and self.player.weapon_boost:
                    print(f"The **{item_name}** has already been equipped. You cannot use it again in combat.")
                    continue # Allows player to try a different item

                if item.use(self.player):
                    # Remove consumable items (Health Potion, Scroll) from inventory
                    if item_name not in ("Elven Blade", "Arcane Focus"):
                        del self.player.inventory[item_name]
                    return True # Turn was successfully spent
                else:
                    print("This item cannot be used right now.")
                    continue
            else:
                print("A moment of confusion, adventurer. That command is not understood.")
                continue

    def _enemy_turn(self):
        """
        Simple enemy AI: 70% chance to standard attack, 30% chance to use a special move.
        """
        # Ensure the player is not currently defending from the previous turn's defense action
        self.player.is_defending = False 

        print(f"\n--- **{self.enemy.name}**'s Turn ---")
        
        # Enemy Logic: 70% Standard Attack, 30% Special Move
        if random.random() < 0.70:
            print(f"**{self.enemy.name}** launches a vicious standard attack!")
            self._calculate_damage(self.enemy, self.player, self.enemy.strength)
        else:
            self._enemy_special_move()

    def _enemy_special_move(self):
        """Defines special moves for different enemies."""
        enemy_name = self.enemy.name
        
        if enemy_name == "Minor Bandit":
            # Minor Bandit: Quick Strike (Higher hit chance, lower damage)
            print("The bandit attempts a swift, low-blow **Quick Strike**!")
            damage = random.randint(1, 4) * self.enemy.strength # Lower damage roll
            
            # Quick Strike: Ignores player's defense state for one attack
            is_defending_temp = self.player.is_defending
            self.player.is_defending = False 
            
            damage_taken = self.player.take_damage(damage)
            self.player.is_defending = is_defending_temp # Restore defense state if it was set
            
            print(f"The Quick Strike bypasses defenses and hits for {damage_taken} damage!")

        elif enemy_name == "Bandit King":
            # Bandit King: 'King's Roar' (AOE/Status effect) - reduces player's next damage
            print("The Bandit King lets out a terrifying **King's Roar**, shaking your resolve!")
            # Debuff: Player's Strength and Magic is temporarily reduced for their next attack
            self.player.temp_defense_buff = 5 # Used as a generic temporary debuff value here
            print(f"You are slightly disoriented. Your next attack will deal slightly less damage.")
            
            # He also attacks with a standard move after the roar (special boss mechanic)
            self._calculate_damage(self.enemy, self.player, self.enemy.strength)

        elif enemy_name == "Arch-Lich, Final Boss":
            # Arch-Lich: Arcane Drain (High Magic damage + small heal for Lich)
            print("The Arch-Lich whispers an ancient spell: **Arcane Drain**!")
            damage = random.randint(4, 10) * self.enemy.magic # Very high damage roll
            
            # Apply damage (magic type)
            damage_taken = self.player.take_damage(damage)
            print(f"The Arcane Drain hits you for {damage_taken} magic damage!")
            
            # Lich heals for 50% of damage dealt
            heal_amount = damage_taken // 2
            self.enemy.current_hp = min(self.enemy.max_hp, self.enemy.current_hp + heal_amount)
            print(f"The Arch-Lich drains your energy, healing itself for {heal_amount} HP.")
        
        # Default fallback for any other enemy
        else:
             print("The enemy hesitates and attacks normally.")
             self._calculate_damage(self.enemy, self.player, self.enemy.strength)


    def start_combat(self):
        """
        The main loop for the combat encounter. Continues until HP drops to 0.
        Returns True for player victory, False for player loss.
        """
        print(f"\n======================================")
        print(f"**A fierce battle begins against {self.enemy.name}!**")
        print(f"======================================")

        while self.player.current_hp > 0 and self.enemy.current_hp > 0:
            print("\n--------------------------------------")
            print(f"{self.player.name} HP: {self.player.current_hp}/{self.player.max_hp} | {self.enemy.name} HP: {self.enemy.current_hp}/{self.enemy.max_hp}")
            print("--------------------------------------")

            # --- Player Turn ---
            player_action = None
            action_spent = False

            while not action_spent:
                # Combat Action Options
                actions = {
                    "attack": self._player_attack,
                    "defend": self._player_defend,
                    "magic": self._player_magic,
                    "item": self._player_use_item,
                    "stats": lambda: print(self.player.get_stats())
                }
                
                prompt = f"Choose your action (Attack, Defend, Magic [{self.player.ability_name}], Item, Stats): "
                user_input = input(prompt).strip().lower()

                try:
                    # Execute the action
                    if user_input in actions:
                        if user_input == "item":
                            # Item use has internal input loop; only proceed if an item was successfully used
                            if actions[user_input]():
                                action_spent = True
                        elif user_input == "stats":
                            # Stats is a free action and doesn't end the turn
                            actions[user_input]()
                        else:
                            actions[user_input]()
                            action_spent = True
                    else:
                        raise ValueError("Invalid command.")
                except (ValueError, KeyError):
                    print("A moment of confusion, adventurer. That command is not understood.")

            # Player has fallen
            if self.player.current_hp <= 0:
                print("\n**You have fallen in battle.**")
                return False

            # Enemy has been defeated
            if self.enemy.current_hp <= 0:
                print(f"\n**VICTORY!** The {self.enemy.name} has been defeated!")
                return True

            # --- Enemy Turn (if still alive) ---
            self._enemy_turn()

        # Final check for victory/loss after the loop ends
        return self.player.current_hp > 0

# --- World Class/Module ---

class World:
    """Manages the story progression, stages, choices, and non-combat encounters."""
    def __init__(self, player):
        self.player = player
        self.stage = 1

    def _get_item(self, item, amount=1):
        """Adds an item to the player's inventory."""
        if item.name in self.player.inventory:
            # We don't track item amounts for this simple game, assume unique items or just one per stack
            # For this simple game, we'll just use the item object as the value
            pass 
        else:
            self.player.inventory[item.name] = item
        print(f"\n--- LOOT FOUND --- You acquired the **{item.name}**!")
        
    def _handle_choice(self, prompt, options):
        """Generic function for handling branching choices with input validation."""
        while True:
            print(f"\n**{prompt}**")
            for key, desc in options.items():
                print(f"  [{key.upper()}]: {desc}")
            
            choice = input("Your choice (A/B/C/...): ").strip().upper()
            
            if choice in options:
                return choice
            else:
                print("A moment of confusion, adventurer. That command is not understood.")
    
    def stage_1(self):
        """
        Stage 1: The Haunted Forest.
        Encounter: Minor Bandit. Choice Point 1: Injured Creature.
        """
        print("\n" + "="*50)
        print("STAGE 1: THE HAUNTED FOREST 🌲")
        print("You enter the dark, mist-shrouded forest. The air is cold and carries a faint scent of decay.")
        
        # --- Stage 1 Encounter ---
        bandit = Character("Minor Bandit", strength=8, agility=10, magic=5, max_hp=60, ability_name="Quick Strike")
        combat_result = Combat(self.player, bandit).start_combat()
        
        if not combat_result:
            return False # Player lost
        
        # Post-combat loot
        self._get_item(HEALTH_POTION)
        
        # --- Choice Point 1: Injured Creature ---
        print("\nAs you continue, you find a small, injured creature whimpering beneath a root. It looks frightened.")
        choice_prompt = "Do you help the injured creature?"
        choice_options = {
            "A": "Heal it and offer comfort (Risking time and resources).",
            "B": "Ignore it and continue on the path (Safest choice)."
        }
        choice = self._handle_choice(choice_prompt, choice_options)
        
        if choice == "A":
            # Option A: Heal it (gives a permanent, small stat boost)
            stat_boost = random.choice(['strength', 'agility', 'magic'])
            
            if stat_boost == 'strength':
                self.player.strength += 1
                print(f"The creature lets out a happy chirp and disappears. You feel a surge of gratitude: **+1 Strength**.")
            elif stat_boost == 'agility':
                self.player.agility += 1
                print(f"The creature licks your hand. You feel lighter on your feet: **+1 Agility**.")
            elif stat_boost == 'magic':
                self.player.magic += 1
                print(f"A strange, warm energy settles in your chest: **+1 Magic**.")
        else:
            # Option B: Ignore it (no penalty)
            print("You shrug and walk past, focusing on your mission.")
            
        self.stage = 2
        return True

    def stage_2(self):
        """
        Stage 2: The Bandit's Lair.
        Encounter: Bandit King (Boss). Choice Point 2: Hidden Passage.
        """
        print("\n" + "="*50)
        print("STAGE 2: THE BANDIT'S LAIR ⛰️")
        print("You track the bandits to a hidden cave. The air is stale and filled with the stench of unwashed bodies.")
        
        # --- Stage 2 Encounter: Boss Fight ---
        bandit_king = Character("Bandit King", strength=12, agility=9, magic=7, max_hp=150, ability_name="King's Roar")
        combat_result = Combat(self.player, bandit_king).start_combat()
        
        if not combat_result:
            return False # Player lost
        
        # Post-combat loot
        self._get_item(SCROLL_PROTECTION)
        self._get_item(HEALTH_POTION)
        
        # --- Choice Point 2: Hidden Passage ---
        print("\nAfter defeating the Bandit King, you notice a cleverly concealed passage behind his throne.")
        choice_prompt = "Do you explore the hidden passage?"
        choice_options = {
            "A": "Enter the dark, hidden passage (Risk for reward).",
            "B": "Continue on the main, safer path."
        }
        choice = self._handle_choice(choice_prompt, choice_options)
        
        # A unique powerful item based on the player's class is found
        if choice == "A":
            print("\n-=- Entering the passage -=-")
            if isinstance(self.player, Warrior) or isinstance(self.player, Rogue):
                self._get_item(ELVEN_BLADE) # Permanent +5 Strength weapon
            elif isinstance(self.player, Mage):
                self._get_item(ARCANE_FOCUS) # Permanent +5 Magic artifact
            
            print("The passage collapses behind you. You must now find your own way out, but you have gained a powerful artifact.")
        else:
            # Option B: Continue on the main path (safer, less risk)
            print("You ignore the passage and continue to the exit, saving your strength.")
            
        self.stage = 3
        return True

    def stage_3(self):
        """
        Stage 3: The Enchanted Castle.
        Final Encounter: Arch-Lich. Choice Point 3: Final Ending Choice.
        """
        print("\n" + "="*50)
        print("STAGE 3: THE ENCHANTED CASTLE 🏰")
        print("You arrive at the crumbling, magically warded castle. In the central courtyard, you find the source of Eldoria's torment.")
        
        # --- Final Encounter Setup ---
        final_boss = Character("Arch-Lich, Final Boss", strength=10, agility=15, magic=18, max_hp=200, ability_name="Arcane Drain")
        
        print(f"\n--- Confrontation ---")
        print(f"Before you stands the terrifying **{final_boss.name}**, radiating raw, corrupting magic.")
        
        # --- Choice Point 3: Final Critical Choice ---
        choice_prompt = "The Arch-Lich turns its hollow gaze upon you. What is your final action?"
        choice_options = {
            "A": "Draw your weapon and charge! (FIGHT: Standard Combat)",
            "B": "Attempt to bargain or reason with the creature. (DIPLOMACY: Stat Check)",
            "C": "Accept its power and betray your cause. (CORRUPTION: Dark Ending)"
        }
        final_choice = self._handle_choice(choice_prompt, choice_options)
        
        if final_choice == "A":
            # A. Fight the creature: Leads to Ending 1 (Heroic Victory) or Loss.
            print("\n**HEROIC PATH CHOSEN!** You enter the battle to save Eldoria!")
            combat_result = Combat(self.player, final_boss).start_combat()
            
            if combat_result:
                self.end_game(1) # Ending 1: Heroic Victory
            else:
                return False # Loss state
        
        elif final_choice == "B":
            # B. Attempt to bargain/befriend: Leads to Ending 2 (Diplomatic Alliance) or Loss.
            print("\n**DIPLOMATIC PATH CHOSEN!** You attempt to breach the Lich's magical defenses with words.")
            
            # Stat Check: Requires high Magic (15 or more) or a specific item (Arcane Focus)
            if self.player.magic >= 15 or self.player.weapon_boost == 5: # Assuming Arcane Focus was equipped
                print("The Lich pauses, a flicker of ancient memory in its eyes. Your words and power resonate...")
                self.end_game(2) # Ending 2: Diplomatic Alliance
            else:
                print("The Lich cackles! 'Your mind is too weak to penetrate my veil!'")
                print("A wave of psychic force overwhelms you, your quest ending abruptly.")
                return False # Loss state (non-combat)

        elif final_choice == "C":
            # C. Betray a past ally/act selfishly: Leads to Ending 3 (The Dark Lord).
            print("\n**CORRUPTION PATH CHOSEN!** You feel the seductive pull of the Lich's power.")
            
            # Desperation Trigger Check: Requires less than 50% HP
            if self.player.current_hp < self.player.max_hp / 2:
                print("Weakened and desperate, you accept the Lich's dark gift.")
                self.end_game(3) # Ending 3: The Dark Lord
            else:
                print("The Lich scoffs. 'You are not desperate enough. Your will is too strong to be fully molded.'")
                print("It crushes your mind, deeming you an unsuitable vessel.")
                return False # Loss state (non-combat)
        
        return True

    def end_game(self, ending_number):
        """Displays the appropriate final ending and exits the game."""
        print("\n" + "#"*50)
        if ending_number == 1:
            print("ENDING 1: HEROIC VICTORY! 🌟")
            print(f"**{self.player.name}**, with blade and spell, you have slain the Arch-Lich and banished the darkness! Eldoria is saved. Your name will be sung forevermore.")
        elif ending_number == 2:
            print("ENDING 2: DIPLOMATIC ALLIANCE 🤝")
            print(f"**{self.player.name}**, you convinced the Lich to cease its destructive magic and instead turn its power toward benign creation. Eldoria enters an era of uneasy, but safe, peace.")
        elif ending_number == 3:
            print("ENDING 3: THE DARK LORD 🌑")
            print(f"**{self.player.name}**... no, you are now the **Arch-Vessel**. You inherit the Lich's dark power, turning Eldoria's pain into your own corrupt empire. The Saga of Eldoria ends, and the Age of Shadow begins.")
        
        print("#"*50)
        sys.exit() # Exit the game after an ending

# --- Main Game Execution ---

def player_setup():
    """Handles the initial player creation (name and class selection)."""
    print("Welcome to The Saga of Eldoria!")
    name = input("Enter your hero's name: ").strip()
    
    player_class = None
    while player_class is None:
        print("\nChoose your class:")
        print("  [W]arrior: High STR, moderate AGI, low MAG. Ability: Shield Bash.")
        print("  [M]age: Low STR, moderate AGI, high MAG. Ability: Arcane Bolt.")
        print("  [R]ogue: Moderate STR, high AGI, low MAG. Ability: Sneak Attack.")
        
        choice = input("Enter W, M, or R: ").strip().upper()
        
        if choice == 'W':
            player_class = Warrior(name)
        elif choice == 'M':
            player_class = Mage(name)
        elif choice == 'R':
            player_class = Rogue(name)
        else:
            print("A moment of confusion, adventurer. That command is not understood.")
            
    print(f"\nWelcome, **{player_class.name}** the **{player_class.__class__.__name__}**!")
    print(player_class.get_stats())
    
    # Starting inventory
    player_class.inventory["Health Potion"] = HEALTH_POTION
    player_class.inventory["Scroll of Protection"] = SCROLL_PROTECTION
    
    return player_class

def game_loop(player):
    """Contains the main narrative flow and stage progression."""
    world = World(player)
    
    # Main game stages loop
    while world.stage <= 3:
        success = False
        if world.stage == 1:
            success = world.stage_1()
        elif world.stage == 2:
            success = world.stage_2()
        elif world.stage == 3:
            success = world.stage_3()
            
        # Check for loss state from combat or choice
        if not success:
            # --- Health Check: Loss State ---
            if player.current_hp <= 0:
                print("\n" + "="*50)
                print("FATALITY: Your strength fails you. The darkness consumes your last breath.")
                print(f"{player.name}'s Saga ends here.")
                print("="*50)
            # Loss state from a choice/bargain failure
            else:
                print("\n" + "="*50)
                print("FATE SEALED: A critical error in judgment has ended your journey.")
                print(f"{player.name}'s Saga ends here.")
                print("="*50)
            break # Exit the loop and end the game

# --- Entry Point ---
if __name__ == "__main__":
    try:
        player_character = player_setup()
        game_loop(player_character)
    except SystemExit:
        # Catch the SystemExit from world.end_game() to exit gracefully
        pass
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("The game must close.")

# End of main.py