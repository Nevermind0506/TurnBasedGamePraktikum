import tkinter as tk
from tkinter import messagebox, simpledialog
from abc import ABC, abstractmethod
import random

# Constants for UI sizing and fonts
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FONT_NAME = "Helvetica"
FONT_SIZE = 12

# Item Types
ITEM_TYPE_POTION = "potion"
ITEM_TYPE_EQUIPMENT = "equipment"

# Define items available in the game (potions & equipments)
class Item:
    def __init__(self, name, item_type, stat_bonus=None, heal_amount=0, mp_restore=0, price=0, description=""):
        self.name = name
        self.item_type = item_type
        self.stat_bonus = stat_bonus or {}
        self.heal_amount = heal_amount
        self.mp_restore = mp_restore
        self.price = price
        self.description = description

    def __str__(self):
        if self.item_type == ITEM_TYPE_POTION:
            effects = []
            if self.heal_amount > 0:
                effects.append(f"Heals {self.heal_amount} HP")
            if self.mp_restore > 0:
                effects.append(f"Restores {self.mp_restore} MP")
            return f"{self.name} (Potion): {', '.join(effects)}"
        elif self.item_type == ITEM_TYPE_EQUIPMENT:
            parts = [f"{k.capitalize()} +{v}" for k, v in self.stat_bonus.items()]
            return f"{self.name} (Equipment): {' | '.join(parts)}"
        else:
            return self.name

# Default potions and equipment
HEALTH_POTION = Item("Health Potion", ITEM_TYPE_POTION, heal_amount=50, price=30,
                     description="Restores 50 HP")
MP_POTION = Item("Mana Potion", ITEM_TYPE_POTION, mp_restore=30, price=25,
                 description="Restores 30 MP")

WOODEN_SWORD = Item("Wooden Sword", ITEM_TYPE_EQUIPMENT, stat_bonus={"attack": 5}, price=100,
                    description="Basic sword, +5 Attack")
IRON_SWORD = Item("Iron Sword", ITEM_TYPE_EQUIPMENT, stat_bonus={"attack": 10}, price=250,
                  description="Steel sword, +10 Attack")
LEATHER_ARMOR = Item("Leather Armor", ITEM_TYPE_EQUIPMENT, stat_bonus={"defense": 5}, price=120,
                     description="Basic armor, +5 Defense")
CHAINMAIL_ARMOR = Item("Chainmail Armor", ITEM_TYPE_EQUIPMENT, stat_bonus={"defense": 12}, price=300,
                       description="Strong armor, +12 Defense")
LUCKY_CHARM = Item("Lucky Charm", ITEM_TYPE_EQUIPMENT, stat_bonus={"evasion": 5}, price=180,
                   description="+5% Evasion")
CRIT_RING = Item("Critical Ring", ITEM_TYPE_EQUIPMENT, stat_bonus={"critical_damage": 10}, price=200,
                 description="+10% Critical Damage Bonus")

class Character(ABC):
    def __init__(self, name, max_hp, max_mp, attack, defense, evasion):
        self._name = name
        self._max_hp = max_hp
        self._hp = max_hp
        self._max_mp = max_mp
        self._mp = max_mp
        self._base_attack = attack
        self._base_defense = defense
        self._base_evasion = evasion  # Percentage (0-100)
        self._alive = True

    @property
    def name(self):
        return self._name

    @property
    def hp(self):
        return self._hp

    @property
    def max_hp(self):
        return self._max_hp

    @property
    def mp(self):
        return self._mp

    @property
    def max_mp(self):
        return self._max_mp

    @property
    def base_attack(self):
        return self._base_attack

    @property
    def base_defense(self):
        return self._base_defense

    @property
    def base_evasion(self):
        return self._base_evasion

    @property
    def is_alive(self):
        return self._alive

    def take_damage(self, damage):
        if damage < 0:
            damage = 0
        self._hp -= damage
        if self._hp <= 0:
            self._hp = 0
            self._alive = False

    def heal(self, amount):
        self._hp += amount
        if self._hp > self._max_hp:
            self._hp = self._max_hp

    def restore_mp(self, amount):
        self._mp += amount
        if self._mp > self._max_mp:
            self._mp = self._max_mp

    def reduce_mp(self, amount):
        self._mp -= amount
        if self._mp < 0:
            self._mp = 0

    def try_evade(self, target_evasion):
        chance = random.randint(1, 100)
        return chance <= target_evasion

    @abstractmethod
    def attack(self, target):
        pass

    @abstractmethod
    def special_attack(self, target):
        pass

class Player(Character):
    def __init__(self, name="Hero"):
        super().__init__(name, max_hp=100, max_mp=50, attack=20, defense=10, evasion=10)
        self.inventory = {}
        self.equipped_items = {"weapon": None, "armor": None, "accessory": None}
        self.xp = 0
        self.level = 1
        self.upgrade_points = 0
        self.gold = 100

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= 100:
            self.xp -= 100
            self.level += 1
            self.upgrade_points += 3
            self._max_hp += 10
            self._hp = self._max_hp
            self._max_mp += 5
            self._mp = self._max_mp
            self._base_attack += 3
            self._base_defense += 2
            self._base_evasion = min(self._base_evasion + 1, 100)

    def total_attack(self):
        bonus = 0
        weapon = self.equipped_items.get("weapon")
        if weapon and weapon.item_type == ITEM_TYPE_EQUIPMENT:
            bonus += weapon.stat_bonus.get("attack", 0)
        return self._base_attack + bonus

    def total_defense(self):
        bonus = 0
        armor = self.equipped_items.get("armor")
        if armor and armor.item_type == ITEM_TYPE_EQUIPMENT:
            bonus += armor.stat_bonus.get("defense", 0)
        return self._base_defense + bonus

    def total_evasion(self):
        bonus = 0
        accessory = self.equipped_items.get("accessory")
        if accessory and accessory.item_type == ITEM_TYPE_EQUIPMENT:
            bonus += accessory.stat_bonus.get("evasion", 0)
        combined = self._base_evasion + bonus
        return min(combined, 100)

    def total_critical_damage_bonus(self):
        bonus = 0
        for slot in ["weapon", "armor", "accessory"]:
            item = self.equipped_items.get(slot)
            if item and item.item_type == ITEM_TYPE_EQUIPMENT:
                bonus += item.stat_bonus.get("critical_damage", 0)
        return bonus

    @property
    def attack_stat(self):
        return self.total_attack()

    @property
    def defense_stat(self):
        return self.total_defense()

    @property
    def evasion_stat(self):
        return self.total_evasion()

    def add_item(self, item, quantity=1):
        if item in self.inventory:
            self.inventory[item] += quantity
        else:
            self.inventory[item] = quantity

    def remove_item(self, item, quantity=1):
        if item in self.inventory:
            self.inventory[item] -= quantity
            if self.inventory[item] <= 0:
                del self.inventory[item]

    def attack(self, target):
        if target.try_evade(target.base_evasion):
            return f"{self.name}'s attack missed!"
        damage = self.attack_stat - target.defense_stat
        damage = max(damage, 1)
        # Critical hit calc
        crit_chance = 0.2  # Base 20% crit chance
        if random.random() < crit_chance:
            crit_multiplier = 2 + (self.total_critical_damage_bonus() / 100)
            damage = int(damage * crit_multiplier)
            target.take_damage(damage)
            return f"Critical hit! {self.name} deals {damage} damage!"
        target.take_damage(damage)
        return f"{self.name} attacks for {damage} damage!"

    def special_attack(self, target):
        mp_cost = 15
        if self._mp < mp_cost:
            return f"Not enough MP for special attack!"
        self.reduce_mp(mp_cost)
        if target.try_evade(target.base_evasion):
            return f"{self.name}'s special attack missed!"
        damage = (self.attack_stat * 2) - target.defense_stat
        damage = max(damage, 1)
        # Critical hit calc for special: same crit chance
        crit_chance = 0.2
        if random.random() < crit_chance:
            crit_multiplier = 2 + (self.total_critical_damage_bonus() / 100)
            damage = int(damage * crit_multiplier)
            target.take_damage(damage)
            return f"Critical hit! {self.name} uses SPECIAL ATTACK for {damage} damage!"
        target.take_damage(damage)
        return f"{self.name} uses SPECIAL ATTACK for {damage} damage!"

    def upgrade_stat(self, stat):
        if self.upgrade_points <= 0:
            return "No upgrade points available."
        if stat == "attack":
            self._base_attack += 2
        elif stat == "defense":
            self._base_defense += 2
        elif stat == "evasion":
            self._base_evasion = min(self._base_evasion + 3, 100)
        elif stat == "mp":
            self._max_mp += 5
            self._mp += 5
        elif stat == "hp":
            self._max_hp += 10
            self._hp += 10
        else:
            return "Invalid stat."
        self.upgrade_points -= 1
        return f"{stat.capitalize()} upgraded! Upgrade points left: {self.upgrade_points}"

    def equip_item(self, item):
        if item.item_type != ITEM_TYPE_EQUIPMENT:
            return "Cannot equip this item"
        if "attack" in item.stat_bonus:
            slot = "weapon"
        elif "defense" in item.stat_bonus:
            slot = "armor"
        elif "evasion" in item.stat_bonus or "critical_damage" in item.stat_bonus:
            # Detect accessory for evasion or crit dmg
            slot = "accessory"
        else:
            return "Unknown item slot"
        self.equipped_items[slot] = item
        return f"Equipped {item.name} in slot {slot}."

    def unequip_item(self, slot):
        if slot in self.equipped_items and self.equipped_items[slot] is not None:
            item = self.equipped_items[slot]
            self.equipped_items[slot] = None
            return f"Unequipped {item.name} from {slot}."
        else:
            return "No item equipped in that slot."

    def use_potion(self, item):
        if item.item_type != ITEM_TYPE_POTION:
            return "Cannot use this item."
        if item not in self.inventory:
            return f"No {item.name} left in inventory."
        if item.heal_amount > 0:
            self.heal(item.heal_amount)
        if item.mp_restore > 0:
            self.restore_mp(item.mp_restore)
        self.remove_item(item, quantity=1)
        return f"Used {item.name}."

class Monster(Character):
    def __init__(self, name, stage):
        base_hp = 50 + (stage * 10)
        base_mp = 30 + (stage * 5)
        base_attack = 15 + (stage * 5)
        base_defense = 8 + (stage * 3)
        base_evasion = min(10 + (stage * 2), 50)
        super().__init__(name, base_hp, base_mp, base_attack, base_defense, base_evasion)

    @property
    def defense_stat(self):
        return self._base_defense

    def attack(self, target):
        if target.try_evade(target.evasion_stat):
            return f"{self._name}'s attack missed!"
        damage = self._base_attack - target.defense_stat
        damage = max(damage, 1)
        target.take_damage(damage)
        return f"{self._name} attacks for {damage} damage!"

    def special_attack(self, target):
        chance = random.randint(1, 100)
        if chance <= 25:
            if target.try_evade(target.evasion_stat):
                return f"{self._name}'s special attack missed!"
            damage = (self._base_attack * 1.5) - target.defense_stat
            damage = max(damage, 1)
            target.take_damage(damage)
            return f"{self._name} uses SPECIAL ATTACK for {int(damage)} damage!"
        else:
            return self.attack(target)

    def drop_loot(self):
        drops = []
        roll = random.randint(1, 100)
        if roll <= 30:
            loot_table = [
                HEALTH_POTION,
                MP_POTION,
                WOODEN_SWORD,
                LEATHER_ARMOR,
                LUCKY_CHARM,
                CRIT_RING
            ]
            item = random.choice(loot_table)
            drops.append(item)
        return drops

class BossMonster(Monster):
    def __init__(self, name, stage):
        base_hp = 120 + (stage * 30)
        base_mp = 80 + (stage * 15)
        base_attack = 30 + (stage * 15)
        base_defense = 20 + (stage * 10)
        base_evasion = min(30 + (stage * 5), 70)
        super().__init__(name, stage)
        self._max_hp = base_hp
        self._hp = base_hp
        self._max_mp = base_mp
        self._mp = base_mp
        self._base_attack = base_attack
        self._base_defense = base_defense
        self._base_evasion = base_evasion

    def special_attack(self, target):
        mp_cost = 20
        if self._mp < mp_cost:
            return self.attack(target)
        self.reduce_mp(mp_cost)
        damage = (self._base_attack * 3) - target.defense_stat
        damage = max(damage, 1)
        target.take_damage(damage)
        return f"{self._name} uses BOSS SPECIAL ATTACK for {damage} damage!"

    def drop_loot(self):
        loot_table = [IRON_SWORD, CHAINMAIL_ARMOR, LUCKY_CHARM, HEALTH_POTION, MP_POTION, CRIT_RING]
        drops = [random.choice(loot_table)]
        if random.randint(1, 100) <= 50:
            drops.append(random.choice(loot_table))
        return drops

class RPGGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Turn-Based RPG Game")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")  # Dark Tech Blue background

        self.stage = 1
        self.player = Player()
        self.monsters = []  # list of monsters this stage
        self.active_monster_index = 0  # which monster player targets / turn from monsters
        self.is_player_turn = True
        self.in_battle = False
        self.game_over = False
        self.player_defending = False

        # Setup UI frames
        self.setup_frames()

        # Setup player and monster UI
        self.create_player_ui()
        self.create_monster_ui()
        self.create_action_buttons()
        self.create_upgrade_buttons()
        self.create_menu_buttons()
        self.create_gold_label()

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.root, textvariable=self.status_var, font=(FONT_NAME, FONT_SIZE),
                                     fg="#E0E0E0", bg="#1a1a2e", wraplength=850, justify="center")
        self.status_label.pack(pady=12)

        self.shop_items = []
        self.start_stage()

    def setup_frames(self):
        self.main_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.player_frame = tk.LabelFrame(self.main_frame, text="Player", fg="#8a5cf6", bg="#2d2d44",
                                          font=(FONT_NAME, 14, "bold"))
        self.player_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.monster_frame = tk.LabelFrame(self.main_frame, text="Enemy", fg="#d44e4e", bg="#2d2d44",
                                           font=(FONT_NAME, 14, "bold"))
        self.monster_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.monster_frame.columnconfigure(0, weight=1)
        self.monster_frame.columnconfigure(1, weight=1)

        self.buttons_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.buttons_frame.pack(padx=20, pady=10)

        self.upgrade_frame = tk.LabelFrame(self.root, text="Upgrades", fg="#4ecdc4", bg="#2d2d44",
                                           font=(FONT_NAME, 12, "bold"))
        self.upgrade_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.menu_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.menu_frame.pack(pady=8)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

    def create_player_ui(self):
        self.player_name_label = tk.Label(self.player_frame, text=self.player.name, font=(FONT_NAME, 16, 'bold'),
                                          fg="#8a5cf6", bg="#2d2d44")
        self.player_name_label.pack(pady=(10, 5))

        self.player_hp_var = tk.StringVar()
        self.player_hp_label = tk.Label(self.player_frame, textvariable=self.player_hp_var, fg="#ffa3a3",
                                        bg="#2d2d44", font=(FONT_NAME, 12))
        self.player_hp_label.pack()

        self.player_mp_var = tk.StringVar()
        self.player_mp_label = tk.Label(self.player_frame, textvariable=self.player_mp_var, fg="#4dc4ff",
                                        bg="#2d2d44", font=(FONT_NAME, 12))
        self.player_mp_label.pack()

        self.player_attack_var = tk.StringVar()
        self.player_attack_label = tk.Label(self.player_frame, textvariable=self.player_attack_var, fg="#b29cff",
                                            bg="#2d2d44", font=(FONT_NAME, 12))
        self.player_attack_label.pack()

        self.player_defense_var = tk.StringVar()
        self.player_defense_label = tk.Label(self.player_frame, textvariable=self.player_defense_var, fg="#b29cff",
                                             bg="#2d2d44", font=(FONT_NAME, 12))
        self.player_defense_label.pack()

        self.player_evasion_var = tk.StringVar()
        self.player_evasion_label = tk.Label(self.player_frame, textvariable=self.player_evasion_var, fg="#b29cff",
                                             bg="#2d2d44", font=(FONT_NAME, 12))
        self.player_evasion_label.pack()

        self.player_level_var = tk.StringVar()
        self.player_level_label = tk.Label(self.player_frame, textvariable=self.player_level_var, fg="#dedede",
                                           bg="#2d2d44", font=(FONT_NAME, 12, "italic"))
        self.player_level_label.pack(pady=(8, 5))

        self.equipped_items_var = tk.StringVar()
        self.equipped_items_label = tk.Label(self.player_frame, textvariable=self.equipped_items_var, fg="#76ffc1",
                                             bg="#2d2d44", font=(FONT_NAME, 11))
        self.equipped_items_label.pack(pady=(2, 10))

        self.update_player_ui()

    def create_monster_ui(self):
        # Create UI for up to 2 monsters side by side
        self.monster_labels = []
        self.monster_hp_vars = []
        self.monster_mp_vars = []
        self.monster_attack_vars = []
        self.monster_defense_vars = []
        self.monster_evasion_vars = []

        for i in range(2):
            frame = tk.Frame(self.monster_frame, bg="#2d2d44", bd=2, relief="groove")
            frame.grid(row=0, column=i, sticky="nsew", padx=8, pady=8)
            self.monster_frame.columnconfigure(i, weight=1)

            name_var = tk.StringVar()
            hp_var = tk.StringVar()
            mp_var = tk.StringVar()
            att_var = tk.StringVar()
            def_var = tk.StringVar()
            eva_var = tk.StringVar()

            lbl_name = tk.Label(frame, textvariable=name_var, font=(FONT_NAME, 16, 'bold'),
                                fg="#d44e4e", bg="#2d2d44")
            lbl_name.pack(pady=(10, 5))

            lbl_hp = tk.Label(frame, textvariable=hp_var, fg="#ffa3a3",
                              bg="#2d2d44", font=(FONT_NAME, 12))
            lbl_hp.pack()

            lbl_mp = tk.Label(frame, textvariable=mp_var, fg="#4dc4ff",
                              bg="#2d2d44", font=(FONT_NAME, 12))
            lbl_mp.pack()

            lbl_att = tk.Label(frame, textvariable=att_var, fg="#efa7a7",
                               bg="#2d2d44", font=(FONT_NAME, 12))
            lbl_att.pack()

            lbl_def = tk.Label(frame, textvariable=def_var, fg="#efa7a7",
                               bg="#2d2d44", font=(FONT_NAME, 12))
            lbl_def.pack()

            lbl_eva = tk.Label(frame, textvariable=eva_var, fg="#efa7a7",
                               bg="#2d2d44", font=(FONT_NAME, 12))
            lbl_eva.pack(pady=(0, 10))

            self.monster_labels.append(name_var)
            self.monster_hp_vars.append(hp_var)
            self.monster_mp_vars.append(mp_var)
            self.monster_attack_vars.append(att_var)
            self.monster_defense_vars.append(def_var)
            self.monster_evasion_vars.append(eva_var)

    def create_action_buttons(self):
        self.button_attack = tk.Button(self.buttons_frame, text="Attack", command=self.player_attack_action,
                                       font=(FONT_NAME, 12, "bold"), bg="#8a5cf6", fg="white", width=14, height=2)
        self.button_attack.grid(row=0, column=0, padx=8, pady=8)

        self.button_special = tk.Button(self.buttons_frame, text="Special Attack (MP 15)", command=self.player_special_attack_action,
                                        font=(FONT_NAME, 12, "bold"), bg="#4ecdc4", fg="white", width=18, height=2)
        self.button_special.grid(row=0, column=1, padx=8, pady=8)

        self.button_defend = tk.Button(self.buttons_frame, text="Defend", command=self.player_defend_action,
                                       font=(FONT_NAME, 12, "bold"), bg="#ffa500", fg="black", width=14, height=2)
        self.button_defend.grid(row=0, column=2, padx=8, pady=8)

        self.update_action_buttons(state="disabled")

    def create_upgrade_buttons(self):
        self.upgrade_info_var = tk.StringVar()
        self.upgrade_info_label = tk.Label(self.upgrade_frame, textvariable=self.upgrade_info_var,
                                           font=(FONT_NAME, 12), fg="#4ecdc4", bg="#2d2d44")
        self.upgrade_info_label.pack(side="top", pady=6)

        self.upgrade_buttons_frame = tk.Frame(self.upgrade_frame, bg="#2d2d44")
        self.upgrade_buttons_frame.pack(pady=6)

        btn_width = 12
        self.upgrade_attack_button = tk.Button(self.upgrade_buttons_frame, text="Attack +2", command=lambda: self.upgrade_stat("attack"),
                                               font=(FONT_NAME, 10, "bold"), width=btn_width, bg="#7c4dff", fg="white")
        self.upgrade_defense_button = tk.Button(self.upgrade_buttons_frame, text="Defense +2", command=lambda: self.upgrade_stat("defense"),
                                                font=(FONT_NAME, 10, "bold"), width=btn_width, bg="#7c4dff", fg="white")
        self.upgrade_evasion_button = tk.Button(self.upgrade_buttons_frame, text="Evasion +3%", command=lambda: self.upgrade_stat("evasion"),
                                                font=(FONT_NAME, 10, "bold"), width=btn_width, bg="#7c4dff", fg="white")
        self.upgrade_mp_button = tk.Button(self.upgrade_buttons_frame, text="MP +5", command=lambda: self.upgrade_stat("mp"),
                                           font=(FONT_NAME, 10, "bold"), width=btn_width, bg="#7c4dff", fg="white")
        self.upgrade_hp_button = tk.Button(self.upgrade_buttons_frame, text="HP +10", command=lambda: self.upgrade_stat("hp"),
                                           font=(FONT_NAME, 10, "bold"), width=btn_width, bg="#7c4dff", fg="white")

        self.upgrade_attack_button.grid(row=0, column=0, padx=6, pady=4)
        self.upgrade_defense_button.grid(row=0, column=1, padx=6, pady=4)
        self.upgrade_evasion_button.grid(row=0, column=2, padx=6, pady=4)
        self.upgrade_mp_button.grid(row=0, column=3, padx=6, pady=4)
        self.upgrade_hp_button.grid(row=0, column=4, padx=6, pady=4)

        self.update_upgrade_ui()

    def create_menu_buttons(self):
        self.inventory_button = tk.Button(self.menu_frame, text="Inventory", command=self.open_inventory_window,
                                          font=(FONT_NAME, 12), bg="#4078c0", fg="white", width=12)
        self.inventory_button.grid(row=0, column=0, padx=20)

        self.shop_button = tk.Button(self.menu_frame, text="Shop", command=self.open_shop_window,
                                     font=(FONT_NAME, 12), bg="#28a745", fg="white", width=12)
        self.shop_button.grid(row=0, column=1, padx=20)

    def create_gold_label(self):
        self.gold_var = tk.StringVar()
        self.gold_label = tk.Label(self.root, textvariable=self.gold_var, font=(FONT_NAME, 14, "bold"),
                                   fg="#ffaa00", bg="#1a1a2e")
        self.gold_label.pack(pady=(2, 0))
        self.update_gold_label()

    def update_gold_label(self):
        self.gold_var.set(f"Gold: {self.player.gold}")

    def update_player_ui(self):
        self.player_hp_var.set(f"HP: {self.player.hp} / {self.player.max_hp}")
        self.player_mp_var.set(f"MP: {self.player.mp} / {self.player.max_mp}")
        self.player_attack_var.set(f"Attack: {self.player.attack_stat}")
        self.player_defense_var.set(f"Defense: {self.player.defense_stat}")
        self.player_evasion_var.set(f"Evasion: {self.player.evasion_stat}%")
        self.player_level_var.set(f"Level: {self.player.level} | XP: {self.player.xp}/100 | Upgrade Points: {self.player.upgrade_points}")
        weapon = self.player.equipped_items["weapon"].name if self.player.equipped_items["weapon"] else "None"
        armor = self.player.equipped_items["armor"].name if self.player.equipped_items["armor"] else "None"
        accessory = self.player.equipped_items["accessory"].name if self.player.equipped_items["accessory"] else "None"
        self.equipped_items_var.set(f"Weapon: {weapon} | Armor: {armor} | Accessory: {accessory}")

    def update_monster_ui(self):
        for i in range(2):
            if i < len(self.monsters):
                m = self.monsters[i]
                self.monster_labels[i].set(m.name)
                self.monster_hp_vars[i].set(f"HP: {m.hp} / {m.max_hp}")
                self.monster_mp_vars[i].set(f"MP: {m.mp} / {m.max_mp}")
                self.monster_attack_vars[i].set(f"Attack: {m._base_attack}")
                self.monster_defense_vars[i].set(f"Defense: {m._base_defense}")
                self.monster_evasion_vars[i].set(f"Evasion: {m._base_evasion}%")
            else:
                self.monster_labels[i].set("")
                self.monster_hp_vars[i].set("")
                self.monster_mp_vars[i].set("")
                self.monster_attack_vars[i].set("")
                self.monster_defense_vars[i].set("")
                self.monster_evasion_vars[i].set("")

    def update_action_buttons(self, state):
        self.button_attack.configure(state=state)
        self.button_special.configure(state=state)
        self.button_defend.configure(state=state)

    def update_upgrade_ui(self):
        self.upgrade_info_var.set(f"Upgrade Points Available: {self.player.upgrade_points}")
        state = "normal" if self.player.upgrade_points > 0 else "disabled"
        self.upgrade_attack_button.configure(state=state)
        self.upgrade_defense_button.configure(state=state)
        self.upgrade_evasion_button.configure(state=state)
        self.upgrade_mp_button.configure(state=state)
        self.upgrade_hp_button.configure(state=state)

    def generate_shop_items(self):
        # Different potential shop items subsets
        sets = [
            [HEALTH_POTION, MP_POTION, WOODEN_SWORD],
            [HEALTH_POTION, IRON_SWORD, LEATHER_ARMOR],
            [MP_POTION, CHAINMAIL_ARMOR, LUCKY_CHARM],
            [HEALTH_POTION, MP_POTION, IRON_SWORD, LUCKY_CHARM, CRIT_RING],
        ]
        # Choose random set each stage
        return random.choice(sets)

    def start_stage(self):
        self.player_defending = False
        if self.stage % 3 == 0:
            # Boss stage
            boss_stage = self.stage // 3
            self.monsters = [BossMonster(f"Boss Stage {self.stage}", stage=boss_stage)]
            self.status_var.set(f"A powerful BOSS appeared at Stage {self.stage}!")
        else:
            # Normal stage with two monsters
            self.monsters = [Monster(f"Monster 1 Stage {self.stage}", stage=self.stage),
                             Monster(f"Monster 2 Stage {self.stage}", stage=self.stage)]
            self.status_var.set(f"Two wild monsters appeared at Stage {self.stage}!")
        self.active_monster_index = 0  # Player targets first monster initially
        self.update_monster_ui()
        self.update_player_ui()
        self.is_player_turn = True
        self.in_battle = True
        self.game_over = False
        self.update_action_buttons(state="normal")
        self.shop_items = self.generate_shop_items()

    def end_battle(self, won):
        self.in_battle = False
        self.update_action_buttons(state="disabled")
        if won:
            gold_earned = 50 + self.stage * 20
            self.player.gold += gold_earned
            self.update_gold_label()

            xp_earned = 50 + self.stage * 10
            self.player.gain_xp(xp_earned)

            drops = []
            for m in self.monsters:
                drops.extend(m.drop_loot())

            loot_text = ""
            if drops:
                for item in drops:
                    self.player.add_item(item, 1)
                loot_names = ", ".join([item.name for item in drops])
                loot_text = f"You found loot: {loot_names}!"
            else:
                loot_text = "No loot dropped this time."
            self.update_player_ui()
            self.update_upgrade_ui()
            self.status_var.set(f"You defeated the enemies! Gained {xp_earned} XP and {gold_earned} Gold! {loot_text} Prepare for next stage...")
            self.stage += 1
            self.root.after(4000, self.start_stage)
        else:
            self.status_var.set("Game Over! You were defeated.")
            messagebox.showinfo("Game Over", "You have been defeated! Game will reset.")
            self.reset_game()

    def reset_game(self):
        self.stage = 1
        self.player = Player()
        self.monsters = []
        self.active_monster_index = 0
        self.is_player_turn = True
        self.in_battle = False
        self.game_over = False
        self.player_defending = False
        self.update_player_ui()
        self.update_monster_ui()
        self.update_upgrade_ui()
        self.update_gold_label()
        self.status_var.set("Game Reset. Starting from Stage 1...")
        self.root.after(2000, self.start_stage)

    def player_attack_action(self):
        if not self.in_battle or not self.is_player_turn:
            return
        target = self.get_current_target_monster()
        if not target:
            self.status_var.set("No valid target to attack.")
            return
        result = self.player.attack(target)
        self.status_var.set(result)
        self.update_monster_ui()
        self.update_player_ui()
        self.check_battle_status()

    def player_special_attack_action(self):
        if not self.in_battle or not self.is_player_turn:
            return
        target = self.get_current_target_monster()
        if not target:
            self.status_var.set("No valid target to attack.")
            return
        result = self.player.special_attack(target)
        self.status_var.set(result)
        self.update_monster_ui()
        self.update_player_ui()
        self.check_battle_status()

    def player_defend_action(self):
        if not self.in_battle or not self.is_player_turn:
            return
        self.status_var.set("Player is defending and will take reduced damage next attack!")
        self.player_defending = True
        self.next_turn()

    def upgrade_stat(self, stat):
        result = self.player.upgrade_stat(stat)
        self.status_var.set(result)
        self.update_player_ui()
        self.update_upgrade_ui()

    def check_battle_status(self):
        alive_monsters = [m for m in self.monsters if m.is_alive]
        if not alive_monsters:
            self.end_battle(won=True)
            return
        # If the current targeted monster is dead, switch target to another alive monster if any
        if not self.monsters[self.active_monster_index].is_alive:
            for idx, m in enumerate(self.monsters):
                if m.is_alive:
                    self.active_monster_index = idx
                    break
            else:
                # No alive monster found, end battle
                self.end_battle(won=True)
                return
        self.next_turn()

    def next_turn(self):
        # Switch between player and monster turns
        if self.is_player_turn:
            # Player turn over, monsters' turn begins
            self.is_player_turn = False
            self.update_action_buttons(state="disabled")
            self.active_monster_index = 0
            self.root.after(1500, self.monster_turn)
        else:
            # Monster turn is done or no monsters left, player's turn
            self.is_player_turn = True
            self.update_action_buttons(state="normal")

    def monster_turn(self):
        # If no monsters alive end battle
        alive_monsters = [m for m in self.monsters if m.is_alive]
        if not alive_monsters:
            self.end_battle(won=True)
            return
        if self.active_monster_index >= len(self.monsters):
            # All monsters have acted, return to player turn
            self.is_player_turn = True
            self.update_action_buttons(state="normal")
            return

        current_monster = self.monsters[self.active_monster_index]
        if not current_monster.is_alive:
            self.active_monster_index += 1
            self.root.after(500, self.monster_turn)
            return

        action_choice = random.choices(["attack", "special"], weights=[80, 20])[0]
        if action_choice == "attack":
            result = current_monster.attack(self.player)
        else:
            result = current_monster.special_attack(self.player)

        if self.player_defending:
            heal_amount = int(current_monster._base_attack // 2)
            self.player.heal(heal_amount)
            result += " Player defended and reduced damage!"
            self.player_defending = False

        self.status_var.set(result)
        self.update_player_ui()

        if not self.player.is_alive:
            self.end_battle(won=False)
            return

        self.active_monster_index += 1
        self.root.after(1500, self.monster_turn)

    def get_current_target_monster(self):
        if not self.monsters:
            return None
        # If only one monster alive or only one monster exists, target that
        alive_monsters = [m for m in self.monsters if m.is_alive]
        if len(alive_monsters) == 1:
            return alive_monsters[0]

        # Multiple monsters alive - ask player which to target
        alive_indexes = [idx for idx, m in enumerate(self.monsters) if m.is_alive]
        # GUI prompt for target selection: a simple dialog
        target_names = [self.monsters[i].name for i in alive_indexes]
        choice = simpledialog.askstring("Choose Target",
                                        f"Multiple enemies alive. Select target by number:\n" +
                                        "\n".join(f"{i+1}. {name}" for i, name in enumerate(target_names)))
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(target_names):
                return self.monsters[alive_indexes[choice_idx]]
        except:
            pass
        # Default to first alive monster if invalid input
        return self.monsters[alive_indexes[0]] if alive_indexes else None

    # Inventory and Shop Windows --------------------------------------------------
    def open_inventory_window(self):
        if hasattr(self, "inventory_window") and self.inventory_window.winfo_exists():
            self.inventory_window.lift()
            return
        self.inventory_window = tk.Toplevel(self.root)
        self.inventory_window.title("Inventory")
        self.inventory_window.geometry("450x350")
        self.inventory_window.configure(bg="#2d2d44")

        tk.Label(self.inventory_window, text="Your Items", font=(FONT_NAME, 14, "bold"), bg="#2d2d44", fg="#b2cdfa").pack(pady=(8, 6))

        self.inventory_listbox = tk.Listbox(self.inventory_window, font=(FONT_NAME, 12), width=40, height=12)
        self.inventory_listbox.pack(padx=12, pady=8)

        buttons_frame = tk.Frame(self.inventory_window, bg="#2d2d44")
        buttons_frame.pack(pady=6)

        self.use_button = tk.Button(buttons_frame, text="Use / Equip", command=self.use_selected_inventory_item,
                                    font=(FONT_NAME, 12), width=12, bg="#3D9970", fg="white")
        self.use_button.pack(side="left", padx=6)

        self.close_inv_button = tk.Button(buttons_frame, text="Close", command=self.inventory_window.destroy,
                                          font=(FONT_NAME, 12), width=12, bg="#aaa", fg="black")
        self.close_inv_button.pack(side="left", padx=6)

        self.refresh_inventory_list()

    def refresh_inventory_list(self):
        self.inventory_listbox.delete(0, tk.END)
        if not self.player.inventory:
            self.inventory_listbox.insert(tk.END, "<Inventory is empty>")
            self.use_button.configure(state="disabled")
            return
        for item, qty in self.player.inventory.items():
            line = f"{item.name} x{qty} - {item.description}"
            self.inventory_listbox.insert(tk.END, line)
        self.use_button.configure(state="normal")

    def use_selected_inventory_item(self):
        selection = self.inventory_listbox.curselection()
        if not selection:
            messagebox.showinfo("Select Item", "Please select an item to use or equip.")
            return
        index = selection[0]
        if index >= len(self.player.inventory):
            return
        item = list(self.player.inventory.keys())[index]

        if item.item_type == ITEM_TYPE_POTION:
            result = self.player.use_potion(item)
            messagebox.showinfo("Item Used", result)
            self.update_player_ui()
        elif item.item_type == ITEM_TYPE_EQUIPMENT:
            result = self.player.equip_item(item)
            messagebox.showinfo("Equip Item", result)
            self.update_player_ui()
        else:
            messagebox.showinfo("Invalid Item", "This item cannot be used or equipped.")
            return
        self.refresh_inventory_list()

    def open_shop_window(self):
        if hasattr(self, "shop_window") and self.shop_window.winfo_exists():
            self.shop_window.lift()
            return
        self.shop_window = tk.Toplevel(self.root)
        self.shop_window.title("Potion Shop")
        self.shop_window.geometry("450x350")
        self.shop_window.configure(bg="#2d2d44")

        tk.Label(self.shop_window, text="Welcome to the Shop", font=(FONT_NAME, 14, "bold"), bg="#2d2d44", fg="#ffd54f").pack(pady=(8, 6))

        self.shop_listbox = tk.Listbox(self.shop_window, font=(FONT_NAME, 12), width=40, height=12)
        self.shop_listbox.pack(padx=12, pady=8)

        self.shop_items = self.generate_shop_items()
        for item in self.shop_items:
            line = f"{item.name} - Price: {item.price} Gold - {item.description}"
            self.shop_listbox.insert(tk.END, line)

        shop_buttons_frame = tk.Frame(self.shop_window, bg="#2d2d44")
        shop_buttons_frame.pack(pady=6)

        self.buy_button = tk.Button(shop_buttons_frame, text="Buy", command=self.buy_selected_shop_item,
                                    font=(FONT_NAME, 12), width=12, bg="#007b40", fg="white")
        self.buy_button.pack(side="left", padx=6)

        self.close_shop_button = tk.Button(shop_buttons_frame, text="Close", command=self.shop_window.destroy,
                                           font=(FONT_NAME, 12), width=12, bg="#aaa", fg="black")
        self.close_shop_button.pack(side="left", padx=6)

    def buy_selected_shop_item(self):
        selection = self.shop_listbox.curselection()
        if not selection:
            messagebox.showinfo("Select Item", "Please select an item to buy.")
            return
        index = selection[0]
        if index >= len(self.shop_items):
            return
        item = self.shop_items[index]
        if self.player.gold >= item.price:
            self.player.gold -= item.price
            self.player.add_item(item, 1)
            self.update_gold_label()
            messagebox.showinfo("Purchase Successful", f"You bought 1x {item.name}.")
        else:
            messagebox.showwarning("Insufficient Gold", "You do not have enough gold to buy this item.")

def main():
    root = tk.Tk()
    game = RPGGameUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()



#tes berubahan