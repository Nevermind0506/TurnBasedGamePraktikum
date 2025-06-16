import tkinter as tk
from tk_game_ui import RPGGameUI
from abc import ABC, abstractmethod
import random

# Tipe Item
ITEM_TYPE_POTION = "potion"
ITEM_TYPE_EQUIPMENT = "equipment"

# Mendefinisikan item yang tersedia dalam permainan (ramuan & perlengkapan)
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
                effects.append(f"Menyembuhkan {self.heal_amount} HP")
            if self.mp_restore > 0:
                effects.append(f"Memulihkan {self.mp_restore} MP")
            return f"{self.name} (Ramuan): {', '.join(effects)}"
        elif self.item_type == ITEM_TYPE_EQUIPMENT:
            parts = [f"{k.capitalize()} +{v}" for k, v in self.stat_bonus.items()]
            return f"{self.name} (Perlengkapan): {' | '.join(parts)}"
        else:
            return self.name

# Ramuan dan perlengkapan default
HEALTH_POTION = Item("Ramuan Kesehatan", ITEM_TYPE_POTION, heal_amount=50, price=30,
                      description="Memulihkan 50 HP")
MP_POTION = Item("Ramuan Mana", ITEM_TYPE_POTION, mp_restore=30, price=25,
                 description="Memulihkan 30 MP")

WOODEN_SWORD = Item("Pedang Kayu", ITEM_TYPE_EQUIPMENT, stat_bonus={"attack": 5}, price=100,
                    description="Pedang dasar, +5 Serangan")
IRON_SWORD = Item("Pedang Besi", ITEM_TYPE_EQUIPMENT, stat_bonus={"attack": 10}, price=250,
                  description="Pedang baja, +10 Serangan")
LEATHER_ARMOR = Item("Baju Zirah Kulit", ITEM_TYPE_EQUIPMENT, stat_bonus={"defense": 5}, price=120,
                       description="Baju zirah dasar, +5 Pertahanan")
CHAINMAIL_ARMOR = Item("Baju Zirah Rantai", ITEM_TYPE_EQUIPMENT, stat_bonus={"defense": 12}, price=300,
                       description="Baju zirah kuat, +12 Pertahanan")
LUCKY_CHARM = Item("Jimat Keberuntungan", ITEM_TYPE_EQUIPMENT, stat_bonus={"evasion": 5}, price=180,
                   description="+5% Menghindar")
CRIT_RING = Item("Cincin Kritis", ITEM_TYPE_EQUIPMENT, stat_bonus={"critical_damage": 10}, price=200,
               description="+10% Bonus Kerusakan Kritis")

class Character(ABC):
    def __init__(self, name, max_hp, max_mp, attack, defense, evasion):
        self._name = name
        self._max_hp = max_hp
        self._hp = max_hp
        self._max_mp = max_mp
        self._mp = max_mp
        self._base_attack = attack
        self._base_defense = defense
        self._base_evasion = evasion  # Persentase (0-100)
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
            return f"Serangan {self.name} meleset!"
        damage = self.attack_stat - target.defense_stat
        damage = max(damage, 1)
        # Perhitungan serangan kritis
        crit_chance = 0.2  # Peluang kritis dasar 20%
        if random.random() < crit_chance:
            crit_multiplier = 2 + (self.total_critical_damage_bonus() / 100)
            damage = int(damage * crit_multiplier)
            target.take_damage(damage)
            return f"Serangan Kritis! {self.name} memberikan {damage} kerusakan!"
        target.take_damage(damage)
        return f"{self.name} menyerang dan memberikan {damage} kerusakan!"

    def special_attack(self, target):
        mp_cost = 15
        if self._mp < mp_cost:
            return f"MP tidak cukup untuk serangan spesial!"
        self.reduce_mp(mp_cost)
        if target.try_evade(target.base_evasion):
            return f"Serangan spesial {self.name} meleset!"
        damage = (self.attack_stat * 2) - target.defense_stat
        damage = max(damage, 1)
        # Perhitungan serangan kritis untuk spesial: peluang kritis yang sama
        crit_chance = 0.2
        if random.random() < crit_chance:
            crit_multiplier = 2 + (self.total_critical_damage_bonus() / 100)
            damage = int(damage * crit_multiplier)
            target.take_damage(damage)
            return f"Serangan Kritis! {self.name} menggunakan SERANGAN SPESIAL dan memberikan {damage} kerusakan!"
        target.take_damage(damage)
        return f"{self.name} menggunakan SERANGAN SPESIAL dan memberikan {damage} kerusakan!"

    def upgrade_stat(self, stat):
        if self.upgrade_points <= 0:
            return "Tidak ada poin peningkatan yang tersedia."
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
            return "Stat tidak valid."
        self.upgrade_points -= 1
        return f"{stat.capitalize()} ditingkatkan! Poin peningkatan tersisa: {self.upgrade_points}"

    def equip_item(self, item):
        if item.item_type != ITEM_TYPE_EQUIPMENT:
            return "Tidak dapat melengkapi item ini"
        if "attack" in item.stat_bonus:
            slot = "weapon"
        elif "defense" in item.stat_bonus:
            slot = "armor"
        elif "evasion" in item.stat_bonus or "critical_damage" in item.stat_bonus:
            # Mendeteksi aksesori untuk menghindar atau kerusakan kritis
            slot = "accessory"
        else:
            return "Slot item tidak diketahui"
        self.equipped_items[slot] = item
        return f"Melengkapi {item.name} di slot {slot}."

    def unequip_item(self, slot):
        if slot in self.equipped_items and self.equipped_items[slot] is not None:
            item = self.equipped_items[slot]
            self.equipped_items[slot] = None
            return f"Melepas {item.name} dari {slot}."
        else:
            return "Tidak ada item yang terpasang di slot itu."

    def use_potion(self, item):
        if item.item_type != ITEM_TYPE_POTION:
            return "Tidak dapat menggunakan item ini."
        if item not in self.inventory:
            return f"Tidak ada {item.name} tersisa di inventaris."
        if item.heal_amount > 0:
            self.heal(item.heal_amount)
        if item.mp_restore > 0:
            self.restore_mp(item.mp_restore)
        self.remove_item(item, quantity=1)
        return f"Menggunakan {item.name}."

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
            return f"Serangan {self._name} meleset!"
        damage = self._base_attack - target.defense_stat
        damage = max(damage, 1)
        target.take_damage(damage)
        return f"{self._name} menyerang dan memberikan {damage} kerusakan!"

    def special_attack(self, target):
        chance = random.randint(1, 100)
        if chance <= 25:
            if target.try_evade(target.evasion_stat):
                return f"Serangan spesial {self._name} meleset!"
            damage = (self._base_attack * 1.5) - target.defense_stat
            damage = max(damage, 1)
            target.take_damage(damage)
            return f"{self._name} menggunakan SERANGAN SPESIAL dan memberikan {int(damage)} kerusakan!"
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
        return f"{self._name} menggunakan SERANGAN SPESIAL BOSS dan memberikan {damage} kerusakan!"

    def drop_loot(self):
        loot_table = [IRON_SWORD, CHAINMAIL_ARMOR, LUCKY_CHARM, HEALTH_POTION, MP_POTION, CRIT_RING]
        drops = [random.choice(loot_table)]
        if random.randint(1, 100) <= 50:
            drops.append(random.choice(loot_table))
        return drops

def main():
    """Fungsi utama untuk menginisialisasi dan menjalankan permainan."""
    root = tk.Tk()
    game = RPGGameUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()