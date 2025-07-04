import random
from abc import ABC, abstractmethod

# Jenis item
ITEM_TYPE_POTION = "potion"
ITEM_TYPE_EQUIPMENT = "equipment"

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
            efek = []
            if self.heal_amount > 0:
                efek.append(f"Menyembuhkan {self.heal_amount} HP")
            if self.mp_restore > 0:
                efek.append(f"Memulihkan {self.mp_restore} MP")
            return f"{self.name} (Ramuan): {', '.join(efek)}"
        elif self.item_type == ITEM_TYPE_EQUIPMENT:
            bagian = [f"{k.capitalize()} +{v}" for k, v in self.stat_bonus.items()]
            return f"{self.name} (Perlengkapan): {' | '.join(bagian)}"
        else:
            return self.name

# Definisi semua item yang tersedia
HEALTH_POTION = Item("Ramuan Kesehatan", ITEM_TYPE_POTION, heal_amount=50, price=30, description="Memulihkan 50 HP")
MP_POTION = Item("Ramuan Mana", ITEM_TYPE_POTION, mp_restore=30, price=25, description="Memulihkan 30 MP")
REVIVE_POTION = Item("Ramuan Kebangkitan", ITEM_TYPE_POTION, price=150, description="Menghidupkan kembali karakter yang mati dengan 50% HP dan MP")

WOODEN_SWORD = Item("Pedang Kayu", ITEM_TYPE_EQUIPMENT, stat_bonus={"attack": 5}, price=100, description="Pedang dasar, +5 Serangan")
IRON_SWORD = Item("Pedang Besi", ITEM_TYPE_EQUIPMENT, stat_bonus={"attack": 10}, price=250, description="Pedang baja, +10 Serangan")

LEATHER_ARMOR = Item("Baju Zirah Kulit", ITEM_TYPE_EQUIPMENT, stat_bonus={"defense": 5}, price=120, description="Baju zirah dasar, +5 Pertahanan")
CHAINMAIL_ARMOR = Item("Baju Zirah Rantai", ITEM_TYPE_EQUIPMENT, stat_bonus={"defense": 12}, price=300, description="Baju zirah kuat, +12 Pertahanan")

LUCKY_CHARM = Item("Jimat Keberuntungan", ITEM_TYPE_EQUIPMENT, stat_bonus={"evasion": 5}, price=180, description="+5% Menghindar")
CRIT_RING = Item("Cincin Kritis", ITEM_TYPE_EQUIPMENT, stat_bonus={"critical_damage": 10}, price=200, description="+10% Bonus Kerusakan Kritis")

MAGIC_STAFF = Item("Tongkat Sihir", ITEM_TYPE_EQUIPMENT, stat_bonus={"attack": 7, "mp": 20}, price=200, description="Tongkat sihir, +7 Serangan & +20 MP")
MYSTIC_ROBE = Item("Jubah Mistis", ITEM_TYPE_EQUIPMENT, stat_bonus={"defense": 3, "mp": 15}, price=250, description="Jubah penyihir, +3 Pertahanan & +15 MP")
MAGIC_RING = Item("Cincin Sihir", ITEM_TYPE_EQUIPMENT, stat_bonus={"evasion": 4, "mp": 10}, price=150, description="Cincin sihir, +4% Hindaran & +10 MP")

# Kelas untuk mengatur party (kelompok karakter)
class Party:
    def __init__(self, members=None):
        self.members = members if members else []
        self.inventory = {}
        self.gold = 0

    def add_gold(self, amount):
        self.gold += amount

    def spend_gold(self, amount):
        if self.gold < amount:
            return False
        self.gold -= amount
        return True

    def add_item(self, item, quantity=1):
        self.inventory[item] = self.inventory.get(item, 0) + quantity

    def remove_item(self, item, quantity=1):
        jumlah_sekarang = self.inventory.get(item, 0)
        if jumlah_sekarang < quantity:
            return False
        self.inventory[item] = jumlah_sekarang - quantity
        if self.inventory[item] <= 0:
            del self.inventory[item]
        return True

    def total_members(self):
        return len(self.members)

    def is_item_equipped_by_any(self, item, excluding_member=None):
        """
        Memeriksa apakah item tertentu dilengkapi oleh anggota party mana pun,
        opsional tidak termasuk anggota tertentu.
        """
        for member in self.members:
            if member == excluding_member:
                continue
            if item in member.equipped_items.values():
                return True
        return False

    def count_item_equipped(self, item):
        """
        Menghitung berapa banyak item spesifik (berdasarkan objek) yang
        saat ini dilengkapi oleh semua anggota party.
        """
        count = 0
        for member in self.members:
            for equipped_item in member.equipped_items.values():
                if equipped_item == item:
                    count += 1
        return count

    def get_living_members(self):
        return [member for member in self.members if member.is_alive]

# Kelas dasar karakter (abstract)
class Character(ABC):
    def __init__(self, name, max_hp, max_mp, attack, defense, evasion):
        self._name = name
        self._max_hp = max_hp
        self._hp = max_hp
        self._max_mp = max_mp
        self._mp = max_mp
        self._base_attack = attack
        self._base_defense = defense
        self._base_evasion = evasion
        self._alive = True
        self.equipped_items = {"weapon": None, "armor": None, "accessory": None}

    # Properti dasar karakter
    @property
    def name(self): return self._name
    @property
    def hp(self): return self._hp
    @property
    def max_hp(self): return self._max_hp
    @property
    def mp(self): return self._mp
    @property
    def max_mp(self): return self._max_mp
    @property
    def attack_stat(self):
        bonus = sum(item.stat_bonus.get("attack", 0) for item in self.equipped_items.values() if item)
        return self._base_attack + bonus
    @property
    def defense_stat(self):
        bonus = sum(item.stat_bonus.get("defense", 0) for item in self.equipped_items.values() if item)
        return self._base_defense + bonus
    @property
    def evasion_stat(self):
        bonus = sum(item.stat_bonus.get("evasion", 0) for item in self.equipped_items.values() if item)
        return min(100, self._base_evasion + bonus)
    @property
    def is_alive(self): return self._alive

    # Fungsi menerima kerusakan
    def take_damage(self, damage):
        self._hp -= max(0, damage)
        if self._hp <= 0:
            self._hp = 0
            self._alive = False

    # Fungsi menyembuhkan karakter
    def heal(self, amount):
        if not self._alive:
            return
        self._hp = min(self._max_hp, self._hp + amount)

    # Fungsi memulihkan MP
    def restore_mp(self, amount):
        self._mp = min(self._max_mp, self._mp + amount)

    # Fungsi mengurangi MP
    def reduce_mp(self, amount):
        self._mp = max(0, self._mp - amount)

    # Cek apakah karakter menghindar dari serangan
    def try_evade(self):
        return random.randint(1, 100) <= self.evasion_stat

    @abstractmethod
    def attack(self, target): pass
    @abstractmethod
    def special_attack(self, target): pass

# Kelas karakter pemain
class Player(Character):
    def __init__(self, name="Hero"):
        super().__init__(name, max_hp=100, max_mp=50, attack=20, defense=10, evasion=10)
        self.xp = 0
        self.level = 1
        self.upgrade_points = 0

    # Tambah XP dan naik level
    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= 100:
            self.xp -= 100
            self.level += 1
            self.upgrade_points += 3
            self._max_hp += 10
            self.heal(10)
            self._max_mp += 10
            self.restore_mp(10)
            self._base_attack += 5
            self._base_defense += 5
            self._base_evasion = min(100, self._base_evasion + 5)

    # Hitung total bonus kerusakan kritis
    def total_critical_damage_bonus(self):
        return sum(item.stat_bonus.get("critical_damage", 0) for item in self.equipped_items.values() if item)

    # Serangan biasa
    def attack(self, target):
        if target.try_evade():
            return f"Serangan {self.name} meleset!"
        damage = max(1, self.attack_stat - target.defense_stat)
        if random.random() < 0.2:
            crit_multiplier = 2 + (self.total_critical_damage_bonus() / 100)
            damage = int(damage * crit_multiplier)
            target.take_damage(damage)
            if not target.is_alive:
                return self.handle_monster_defeat(target, damage, crit=True)
            return f"Serangan Kritis! {self.name} memberikan {damage} kerusakan!"
        target.take_damage(damage)
        if not target.is_alive:
            return self.handle_monster_defeat(target, damage)
        return f"{self.name} menyerang dan memberikan {damage} kerusakan!"

    # Penanganan ketika monster dikalahkan
    def handle_monster_defeat(self, monster, damage, crit=False):
        self.heal(50)
        self.restore_mp(30)
        self.gain_xp(50)
        loot = monster.drop_loot()
        loot_str = ', '.join(item.name for item in loot) if loot else "tidak ada loot"
        return f"{self.name} mengalahkan {monster.name}! Mendapatkan {loot_str}. Regenerasi 50 HP, 30 MP, dan 50 XP."

    # Serangan spesial
    def special_attack(self, target):
        mp_cost = 15
        if self._mp < mp_cost:
            return "MP tidak cukup untuk serangan spesial!"
        self.reduce_mp(mp_cost)
        if target.try_evade():
            return f"Serangan spesial {self.name} meleset!"
        damage = max(1, (self.attack_stat * 2) - target.defense_stat)
        target.take_damage(damage)
        if not target.is_alive:
            return self.handle_monster_defeat(target, damage)
        return f"{self.name} menggunakan SERANGAN SPESIAL dan memberikan {damage} kerusakan!"

    # Peningkatan statistik karakter
    def upgrade_stat(self, stat):
        if self.upgrade_points <= 0:
            return "Tidak ada poin peningkatan yang tersedia."
        if stat == "attack":
            self._base_attack += 5
        elif stat == "defense":
            self._base_defense += 5
        elif stat == "evasion":
            self._base_evasion = min(100, self._base_evasion + 5)
        elif stat == "mp":
            self._max_mp += 5
            self.restore_mp(5)
        elif stat == "hp":
            self._max_hp += 10
            self.heal(10)
        else:
            return "Stat tidak valid."
        self.upgrade_points -= 1
        return f"{stat.capitalize()} ditingkatkan! Poin tersisa: {self.upgrade_points}"

    # Melengkapi item ke karakter
    def equip_item(self, item, party):
        # Memastikan item adalah tipe perlengkapan
        if item.item_type != ITEM_TYPE_EQUIPMENT:
            return "Tidak dapat melengkapi item ini."

        # Memastikan item spesifik ini belum dilengkapi oleh karakter ini
        if item in self.equipped_items.values():
            return f"{item.name} sudah dilengkapi oleh {self.name}."

        # Memeriksa ketersediaan item di inventaris partai (yang belum dilengkapi)
        # Jika kuantitas item di inventaris adalah 0, berarti tidak ada item yang tersedia untuk dilengkapi.
        inventory_qty = party.inventory.get(item, 0)
        if inventory_qty == 0:
            return f"{item.name} tidak tersedia di inventaris."

        # Menentukan slot item berdasarkan bonus statistik
        if "attack" in item.stat_bonus:
            slot = "weapon"
        elif "defense" in item.stat_bonus:
            slot = "armor"
        else: # Item yang tidak memiliki bonus serangan atau pertahanan akan masuk slot aksesori
            slot = "accessory"

        # Melepas item lama dari slot jika ada dan mengembalikannya ke inventaris partai
        if self.equipped_items[slot] is not None:
            party.add_item(self.equipped_items[slot], 1)

        # Melengkapi item baru ke karakter
        self.equipped_items[slot] = item
        # Mengurangi item dari inventaris partai karena sudah dilengkapi
        party.remove_item(item, 1)
        return f"Melengkapi {item.name} di slot {slot}."

    # Melepas perlengkapan dari slot
    def unequip_item(self, slot, party=None):
        if slot not in self.equipped_items:
            return "Slot tidak valid."
        if self.equipped_items[slot] is None:
            return f"Tidak ada item yang terpasang di slot {slot}."
        removed_item = self.equipped_items[slot]
        self.equipped_items[slot] = None
        if party is not None:
            party.add_item(removed_item, 1) # Tambahkan item yang dilepas kembali ke inventaris party
        return f"Item {removed_item.name} dilepas dari slot {slot}."

    # Menggunakan ramuan
    def use_potion(self, item, party=None):
        if item.item_type != ITEM_TYPE_POTION:
            return "Item ini bukan ramuan."
        # Logika khusus untuk ramuan kebangkitan
        if item.name == "Ramuan Kebangkitan" and not self.is_alive:
            self._alive = True
            self._hp = self._max_hp // 2
            self._mp = self._max_mp // 2
            return f"{self.name} dihidupkan kembali dengan 50% HP dan MP!"
        # Menggunakan ramuan penyembuh HP
        if item.heal_amount > 0:
            self.heal(item.heal_amount)
        # Menggunakan ramuan pemulih MP
        if item.mp_restore > 0:
            self.restore_mp(item.mp_restore)
        return f"Menggunakan {item.name}."

# Kelas turunan dari Player: Sage (ahli sihir)
class Sage(Player):
    def __init__(self, name="Sage"):
        super().__init__(name)
        # Sesuaikan statistik awal untuk Sage
        self._max_hp = 80
        self._hp = 80
        self._max_mp = 100
        self._mp = 100
        self._base_attack = 15
        self._base_defense = 8
        self._base_evasion = 12

    # Serangan spesial untuk karakter Sage
    def special_attack(self, target):
        mp_cost = 20
        if self._mp < mp_cost:
            return "MP tidak cukup untuk serangan spesial!"
        self.reduce_mp(mp_cost)
        if target.try_evade():
            return f"Serangan spesial {self.name} meleset!"
        damage = max(1, (self.attack_stat * 2.5) - target.defense_stat)
        target.take_damage(damage)
        if not target.is_alive:
            return self.handle_monster_defeat(target, damage)
        return f"{self.name} menggunakan SERANGAN SAGE SPESIAL dan memberikan {damage} kerusakan!"

# Kelas musuh biasa (monster)
class Monster(Character):
    def __init__(self, name, stage):
        # Statistik dasar monster berdasarkan level tahap (stage)
        base_hp = 50 + (stage * 10)
        base_mp = 30 + (stage * 5)
        base_attack = 15 + (stage * 5)
        base_defense = 8 + (stage * 3)
        base_evasion = min(50, 10 + (stage * 2))  # Hindaran maksimum 50%
        super().__init__(name, base_hp, base_mp, base_attack, base_defense, base_evasion)

    # Serangan biasa monster ke target
    def attack(self, target):
        if target.try_evade():
            return f"Serangan {self._name} meleset!"
        damage = max(1, self.attack_stat - target.defense_stat)
        target.take_damage(damage)
        return f"{self._name} menyerang dan memberikan {damage} kerusakan!"

    # Serangan spesial monster, dengan peluang 25%
    def special_attack(self, target):
        if random.random() > 0.25: # 25% kemungkinan serangan spesial
            return self.attack(target)
        if target.try_evade():
            return f"Serangan spesial {self._name} meleset!"
        damage = max(1, int(self.attack_stat * 1.5) - target.defense_stat)
        target.take_damage(damage)
        return f"{self._name} menggunakan SERANGAN SPESIAL dan memberikan {damage} kerusakan!"

    # Drop loot saat monster dikalahkan
    def drop_loot(self):
        if random.random() <= 0.5:  # 50% kemungkinan drop
            loot_table = [HEALTH_POTION, MP_POTION, WOODEN_SWORD, LEATHER_ARMOR, LUCKY_CHARM, CRIT_RING]
            return [random.choice(loot_table)]
        return []

# Kelas monster boss, lebih kuat dari monster biasa
class BossMonster(Monster):
    def __init__(self, name, stage):
        # Statistik dasar bos yang jauh lebih tinggi
        base_hp = 120 + (stage * 30)
        base_mp = 80 + (stage * 15)
        base_attack = 30 + (stage * 15)
        base_defense = 20 + (stage * 10)
        base_evasion = min(70, 30 + (stage * 5))  # Hindaran maksimum 70%
        Character.__init__(self, name, base_hp, base_mp, base_attack, base_defense, base_evasion)

    # Serangan spesial boss, sangat kuat
    def special_attack(self, target):
        mp_cost = 20
        if self._mp < mp_cost:
            return self.attack(target)
        self.reduce_mp(mp_cost)
        damage = max(1, (self.attack_stat * 3) - target.defense_stat)
        target.take_damage(damage)
        return f"{self._name} menggunakan SERANGAN SPESIAL BOSS dan memberikan {damage} kerusakan!"

    # Loot lebih banyak dan lebih berharga
    def drop_loot(self):
        loot_table = [
            IRON_SWORD,
            CHAINMAIL_ARMOR,
            LUCKY_CHARM,
            HEALTH_POTION,
            MP_POTION,
            CRIT_RING,
            REVIVE_POTION
        ]
        drops = [random.choice(loot_table)]
        if random.random() <= 0.7:  # 70% kemungkinan dapat drop tambahan
            drops.append(random.choice(loot_table))
        return drops
