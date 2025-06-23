import tkinter as tk
from tkinter import messagebox, simpledialog
import random
from game_logic import (
    Player, Sage, Monster, BossMonster,
    ITEM_TYPE_POTION, ITEM_TYPE_EQUIPMENT,
    HEALTH_POTION, MP_POTION, WOODEN_SWORD, IRON_SWORD,
    LEATHER_ARMOR, CHAINMAIL_ARMOR, LUCKY_CHARM, CRIT_RING,
    REVIVE_POTION, MAGIC_STAFF, MYSTIC_ROBE, MAGIC_RING,
    Party
)

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 650
FONT_NAME = "Helvetica"

class RPGGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Turn-Based RPG Game")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        self.stage = 1
        self.party = Party(members=[Player(), Sage()])
        self.party.gold = 200
        self.current_player_index = 0
        self.monsters = []
        self.player_defending = False

        self.setup_frames()
        self.create_widgets()
        self.start_stage()

    def setup_frames(self):
        self.main_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=10)
        self.main_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.player_frames = []
        for i, player in enumerate(self.party.members):
            frame = tk.LabelFrame(
                self.main_frame,
                text=f"Pemain - {player.name}",
                fg="#8a5cf6" if i == 0 else "#4ecdc4",
                bg="#2d2d44",
                font=(FONT_NAME, 14, "bold")
            )
            frame.grid(row=0, column=i, sticky="nsew", padx=10, pady=10)
            self.player_frames.append(frame)

        self.monster_frame = tk.LabelFrame(self.main_frame, text="Musuh", fg="#d44e4e", bg="#2d2d44",
                                           font=(FONT_NAME, 14, "bold"))
        self.monster_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        self.monster_frame.grid_columnconfigure((0, 1), weight=1)
        self.monster_frame.grid_rowconfigure(0, weight=1)

        self.status_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.status_frame.pack(fill="x", padx=20, pady=5)

        self.buttons_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.buttons_frame.pack(pady=5)

        self.upgrade_frame = tk.LabelFrame(self.root, text="Peningkatan", fg="#4ecdc4", bg="#2d2d44",
                                          font=(FONT_NAME, 12, "bold"))
        self.upgrade_frame.pack(fill="x", padx=20, pady=5)

        self.menu_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.menu_frame.pack(pady=10)

    def create_widgets(self):
        self.player_vars = []
        for i, player in enumerate(self.party.members):
            vars = {
                "name": tk.StringVar(),
                "hp": tk.StringVar(),
                "mp": tk.StringVar(),
                "stats": tk.StringVar(),
                "level": tk.StringVar(),
                "equipped": tk.StringVar()
            }
            frame = self.player_frames[i]
            tk.Label(frame, textvariable=vars["name"], font=(FONT_NAME, 16, 'bold'),
                     fg="#8a5cf6" if i == 0 else "#4ecdc4", bg="#2d2d44").pack(pady=(10, 5))
            tk.Label(frame, textvariable=vars["hp"], font=(FONT_NAME, 12),
                     fg="#ffa3a3", bg="#2d2d44").pack()
            tk.Label(frame, textvariable=vars["mp"], font=(FONT_NAME, 12),
                     fg="#4dc4ff", bg="#2d2d44").pack()
            tk.Label(frame, textvariable=vars["stats"], font=(FONT_NAME, 12),
                     fg="#b29cff", bg="#2d2d44").pack()
            tk.Label(frame, textvariable=vars["level"], font=(FONT_NAME, 12, "italic"),
                     fg="#dedede", bg="#2d2d44").pack(pady=5)
            tk.Label(frame, textvariable=vars["equipped"], font=(FONT_NAME, 11),
                     fg="#76ffc1", bg="#2d2d44", justify="left").pack(pady=5, padx=10, fill='x')
            self.player_vars.append(vars)

        self.monster_widgets = []
        for i in range(2):
            m_frame = tk.Frame(self.monster_frame, bg="#2d2d44", bd=2, relief="groove")
            m_frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            m_vars = {"name": tk.StringVar(), "hp": tk.StringVar(), "stats": tk.StringVar()}
            tk.Label(m_frame, textvariable=m_vars["name"], font=(FONT_NAME, 14, 'bold'), fg="#d44e4e", bg="#2d2d44").pack(
                pady=(10, 5))
            tk.Label(m_frame, textvariable=m_vars["hp"], font=(FONT_NAME, 12), fg="#ffa3a3", bg="#2d2d44").pack()
            tk.Label(m_frame, textvariable=m_vars["stats"], font=(FONT_NAME, 12), fg="#efa7a7", bg="#2d2d44").pack(
                pady=(0, 10))
            self.monster_widgets.append({"frame": m_frame, "vars": m_vars})

        self.status_var = tk.StringVar()
        tk.Label(self.status_frame, textvariable=self.status_var, font=(FONT_NAME, 12), fg="#E0E0E0", bg="#1a1a2e",
                 wraplength=1050).pack()

        self.gold_var = tk.StringVar()
        tk.Label(self.menu_frame, textvariable=self.gold_var, font=(FONT_NAME, 14, "bold"), fg="#ffaa00",
                 bg="#1a1a2e").grid(row=0, column=2, padx=20)

        self.action_buttons = {
            "attack": tk.Button(self.buttons_frame, text="Serang", command=self.player_attack_action,
                                font=(FONT_NAME, 12, "bold"), bg="#8a5cf6", fg="white", width=14, height=2),
            "special": tk.Button(self.buttons_frame, text="Spesial (15 MP)", command=self.player_special_attack_action,
                                 font=(FONT_NAME, 12, "bold"), bg="#4ecdc4", fg="white", width=16, height=2),
            "defend": tk.Button(self.buttons_frame, text="Bertahan", command=self.player_defend_action,
                                font=(FONT_NAME, 12, "bold"), bg="#ffa500", fg="black", width=14, height=2)
        }
        self.action_buttons["attack"].grid(row=0, column=0, padx=8)
        self.action_buttons["special"].grid(row=0, column=1, padx=8)
        self.action_buttons["defend"].grid(row=0, column=2, padx=8)

        self.upgrade_info_var = tk.StringVar()
        tk.Label(self.upgrade_frame, textvariable=self.upgrade_info_var, font=(FONT_NAME, 12), fg="#4ecdc4",
                 bg="#2d2d44").pack(pady=5)
        u_buttons_frame = tk.Frame(self.upgrade_frame, bg="#2d2d44")
        u_buttons_frame.pack(pady=5)
        self.upgrade_buttons = {
            "hp": tk.Button(u_buttons_frame, text="HP +10", command=lambda: self.upgrade_stat("hp"),
                            font=(FONT_NAME, 10, "bold"), width=12, bg="#7c4dff", fg="white"),
            "mp": tk.Button(u_buttons_frame, text="MP +5", command=lambda: self.upgrade_stat("mp"),
                            font=(FONT_NAME, 10, "bold"), width=12, bg="#7c4dff", fg="white"),
            "attack": tk.Button(u_buttons_frame, text="Serangan +5", command=lambda: self.upgrade_stat("attack"),
                                font=(FONT_NAME, 10, "bold"), width=12, bg="#7c4dff", fg="white"),
            "defense": tk.Button(u_buttons_frame, text="Pertahanan +5", command=lambda: self.upgrade_stat("defense"),
                                 font=(FONT_NAME, 10, "bold"), width=12, bg="#7c4dff", fg="white"),
            "evasion": tk.Button(u_buttons_frame, text="Hindaran +5%", command=lambda: self.upgrade_stat("evasion"),
                                 font=(FONT_NAME, 10, "bold"), width=12, bg="#7c4dff", fg="white")
        }
        for i, btn in enumerate(self.upgrade_buttons.values()):
            btn.grid(row=0, column=i, padx=5)

        unequip_frame = tk.Frame(self.upgrade_frame, bg="#2d2d44")
        unequip_frame.pack(pady=5)
        tk.Button(unequip_frame, text="Lepas Senjata", command=lambda: self.unequip_current_player_slot("weapon"),
                  font=(FONT_NAME, 10, "bold"), width=12, bg="#ff5555", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(unequip_frame, text="Lepas Zirah", command=lambda: self.unequip_current_player_slot("armor"),
                  font=(FONT_NAME, 10, "bold"), width=12, bg="#ff5555", fg="white").grid(row=0, column=1, padx=5)
        tk.Button(unequip_frame, text="Lepas Aksesori", command=lambda: self.unequip_current_player_slot("accessory"),
                  font=(FONT_NAME, 10, "bold"), width=12, bg="#ff5555", fg="white").grid(row=0, column=2, padx=5)

        tk.Button(self.menu_frame, text="Inventaris", command=self.open_inventory_window, font=(FONT_NAME, 12),
                  bg="#4078c0", fg="white", width=12).grid(row=0, column=0, padx=20)
        tk.Button(self.menu_frame, text="Toko", command=self.open_shop_window, font=(FONT_NAME, 12), bg="#28a745",
                  fg="white", width=12).grid(row=0, column=1, padx=20)

    def update_all_ui(self):
        for i, player in enumerate(self.party.members):
            p = player
            vars = self.player_vars[i]
            vars["name"].set(p.name)
            vars["hp"].set(f"HP: {p.hp} / {p.max_hp}")
            vars["mp"].set(f"MP: {p.mp} / {p.max_mp}")
            vars["stats"].set(f"Serangan: {p.attack_stat} | Pertahanan: {p.defense_stat} | Hindaran: {p.evasion_stat}%")
            vars["level"].set(f"Level: {p.level} | XP: {p.xp}/100")
            weapon = p.equipped_items.get('weapon')
            armor = p.equipped_items.get('armor')
            accessory = p.equipped_items.get('accessory')
            equipped_text = (
                f"Senjata: {weapon.name if weapon else 'Kosong'}\n"
                f"Zirah: {armor.name if armor else 'Kosong'}\n"
                f"Aksesori: {accessory.name if accessory else 'Kosong'}"
            )
            vars["equipped"].set(equipped_text)

        for i, m_widget in enumerate(self.monster_widgets):
            if i < len(self.monsters) and self.monsters[i].is_alive:
                m = self.monsters[i]
                m_widget["vars"]["name"].set(m.name)
                m_widget["vars"]["hp"].set(f"HP: {m.hp} / {m.max_hp}")
                m_widget["vars"]["stats"].set(f"ATK: {m.attack_stat} | DEF: {m.defense_stat}")
                m_widget["frame"].grid()
            else:
                m_widget["frame"].grid_remove()

        self.gold_var.set(f"Emas: {self.party.gold}")

        current_player = self.party.members[self.current_player_index]
        self.upgrade_info_var.set(f"Poin Peningkatan ({current_player.name}): {current_player.upgrade_points}")
        state = "normal" if current_player.upgrade_points > 0 else "disabled"
        for btn in self.upgrade_buttons.values():
            btn.config(state=state)

    def set_action_buttons_state(self, state):
        for btn in self.action_buttons.values():
            btn.config(state=state)

    def unequip_current_player_slot(self, slot):
        current_player = self.party.members[self.current_player_index]
        result = current_player.unequip_item(slot, party=self.party)
        self.status_var.set(result)
        self.update_all_ui()

    def start_stage(self):
        self.player_defending = False
        if self.stage % 3 == 0:
            boss_stage_num = self.stage // 3
            self.monsters = [BossMonster(f"Boss Tahap {boss_stage_num}", stage=boss_stage_num)]
            self.status_var.set(f"BOSS yang kuat muncul!")
        else:
            monster_count = 1 if self.stage == 1 else 2
            self.monsters = [Monster(f"Monster #{i + 1}", stage=self.stage) for i in range(monster_count)]
            self.status_var.set(f"{len(self.monsters)} monster liar muncul!")

        self.current_player_index = 0
        self.update_all_ui()
        self.set_action_buttons_state("normal")
        self.status_var.set(f"Giliran: {self.party.members[self.current_player_index].name}")

    def end_battle(self, won):
        self.set_action_buttons_state("disabled")
        if won:
            xp_earned = 50 * self.stage
            gold_earned = 75 * self.stage

            for p in self.party.members:
                p.gain_xp(xp_earned)

            self.party.add_gold(gold_earned)

            all_drops = sum([m.drop_loot() for m in self.monsters], [])
            for item in all_drops:
                self.party.add_item(item)

            drop_names = ", ".join(item.name for item in all_drops) if all_drops else "Tidak ada."
            self.status_var.set(f"Menang! Dapat {xp_earned} XP & {gold_earned} Emas.\nJarahan: {drop_names}\nBersiap untuk tahap selanjutnya...")
            self.stage += 1
            self.root.after(4000, self.start_stage)
        else:
            self.status_var.set("Permainan Berakhir! Anda telah dikalahkan.")
            messagebox.showinfo("Kalah", "Anda dikalahkan! Permainan akan diatur ulang.")
            self.reset_game()
        self.update_all_ui()

    def reset_game(self):
        self.stage = 1
        self.party = Party(members=[Player(), Sage()])
        self.party.gold = 200
        self.current_player_index = 0
        self.start_stage()

    def execute_player_turn(self, action, *args):
        while self.current_player_index < len(self.party.members) and not self.party.members[self.current_player_index].is_alive:
            self.current_player_index += 1

        if self.current_player_index >= len(self.party.members):
            self.status_var.set("Semua pemain telah mati. Permainan berakhir.")
            messagebox.showinfo("Game Over", "Semua pemain telah mati!")
            self.reset_game()
            return

        self.set_action_buttons_state("disabled")

        current_player = self.party.members[self.current_player_index]
        result = action(current_player, *args)
        self.status_var.set(result)
        self.update_all_ui()

        alive_monsters = [m for m in self.monsters if m.is_alive]
        if not alive_monsters:
            self.end_battle(won=True)
            return

        self.current_player_index += 1
        while self.current_player_index < len(self.party.members) and not self.party.members[self.current_player_index].is_alive:
            self.current_player_index += 1

        if self.current_player_index >= len(self.party.members):
            self.current_player_index = 0
            while self.current_player_index < len(self.party.members) and not self.party.members[self.current_player_index].is_alive:
                self.current_player_index += 1
            if self.current_player_index >= len(self.party.members):
                self.status_var.set("Semua pemain telah mati. Permainan berakhir.")
                messagebox.showinfo("Game Over", "Semua pemain telah mati!")
                self.reset_game()
                return
            self.root.after(1500, self.execute_monster_turn)
        else:
            self.status_var.set(f"Giliran: {self.party.members[self.current_player_index].name}")
            self.set_action_buttons_state("normal")
            self.update_all_ui()

    def player_attack_action(self):
        target = self.choose_target()
        if target:
            self.execute_player_turn(lambda player: player.attack(target))

    def player_special_attack_action(self):
        target = self.choose_target()
        if target:
            self.execute_player_turn(lambda player: player.special_attack(target))

    def player_defend_action(self):
        self.player_defending = True

        def defend_turn(player):
            return f"{player.name} bersiap untuk bertahan!"

        self.execute_player_turn(defend_turn)

    def execute_monster_turn(self):
        turn_results = []
        living_players = self.party.get_living_members()
        if not living_players:
            self.status_var.set("Semua pemain telah mati. Permainan berakhir.")
            messagebox.showinfo("Game Over", "Semua pemain telah mati!")
            self.reset_game()
            return

        for monster in self.monsters:
            if not monster.is_alive:
                continue

            target = random.choice(living_players)

            action = monster.special_attack if random.random() < 0.2 else monster.attack
            result = action(target)

            if self.player_defending and target == self.party.members[self.current_player_index]:
                result += " (Bertahan!)"

            turn_results.append(result)

            living_players = self.party.get_living_members()
            if not living_players:
                self.status_var.set("\\n".join(turn_results))
                self.update_all_ui()
                messagebox.showinfo("Game Over", "Semua pemain telah mati!")
                self.reset_game()
                return

        self.player_defending = False
        self.status_var.set("\\n".join(turn_results))
        self.update_all_ui()
        self.set_action_buttons_state("normal")
        self.status_var.set(f"Giliran: {self.party.members[self.current_player_index].name}")

    def choose_target(self):
        alive_monsters = [m for m in self.monsters if m.is_alive]
        if not alive_monsters:
            return None
        if len(alive_monsters) == 1:
            return alive_monsters[0]

        # Create a new window for monster selection with improved UI
        self.selected_monster = None  # Reset before selection
        target_win = tk.Toplevel(self.root)
        target_win.title("Pilih Target")
        target_win.transient(self.root)
        target_win.grab_set()
        target_win.geometry("320x300")
        target_win.configure(bg="#2d2d44")

        tk.Label(target_win, text="Pilih target monster:", font=(FONT_NAME, 14, "bold"), fg="white", bg="#2d2d44").pack(pady=15)

        button_frame = tk.Frame(target_win, bg="#2d2d44")
        button_frame.pack(pady=10, fill="both", expand=True)

        # Scrollbar for many monsters
        canvas = tk.Canvas(button_frame, bg="#2d2d44", highlightthickness=0)
        scrollbar = tk.Scrollbar(button_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2d2d44")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for monster in alive_monsters:
            btn = tk.Button(scrollable_frame,
                            text=f"{monster.name}\nHP: {monster.hp} / {monster.max_hp}",
                            font=(FONT_NAME, 12, "bold"),
                            fg="white",
                            bg="#8a5cf6",
                            activebackground="#6a3cd2",
                            width=25,
                            height=3,
                            relief="raised",
                            bd=3,
                            command=lambda m=monster: self.select_monster(m, target_win))
            btn.pack(pady=6, padx=10, fill="x", expand=True)

        # Cancel button
        cancel_btn = tk.Button(target_win, text="Batal", font=(FONT_NAME, 12, "bold"), bg="#ff5555", fg="white",
                               command=lambda: self.cancel_selection(target_win))
        cancel_btn.pack(pady=10, ipadx=10)

        self.root.wait_window(target_win)
        return self.selected_monster

    def select_monster(self, monster, window):
        self.selected_monster = monster
        window.destroy()

    def cancel_selection(self, window):
        self.selected_monster = None
        window.destroy()

    def upgrade_stat(self, stat):
        current_player = self.party.members[self.current_player_index]
        result = current_player.upgrade_stat(stat)
        self.status_var.set(result)
        self.update_all_ui()

    def open_inventory_window(self):
        win = tk.Toplevel(self.root)
        win.title("Inventaris")
        win.transient(self.root)
        win.grab_set()
        win.geometry("600x450")
        win.configure(bg="#2d2d44")

        listbox = tk.Listbox(win, font=(FONT_NAME, 12), width=70, height=15, bg="#3c3c54", fg="white",
                             selectbackground="#8a5cf6")
        listbox.pack(padx=12, pady=8)

        def refresh_list():
            listbox.delete(0, tk.END)
            inventory = self.party.inventory
            if not inventory:
                listbox.insert(tk.END, "<Inventaris kosong>")
                return
            for item, qty in inventory.items():
                listbox.insert(tk.END, f"{item.name} x{qty} - {item.description}")

        def choose_target_player():
            target_win = tk.Toplevel(win)
            target_win.title("Pilih Pemain")
            target_win.transient(win)
            target_win.grab_set()
            target_win.geometry("300x170")
            target_win.configure(bg="#2d2d44")

            tk.Label(target_win, text="Pilih pemain untuk memakai item ini:", font=(FONT_NAME, 12), fg="white",
                     bg="#2d2d44").pack(pady=10)

            selected = tk.StringVar()

            def select_hero():
                selected.set("Hero")
                target_win.destroy()

            def select_sage():
                selected.set("Sage")
                target_win.destroy()

            tk.Button(target_win, text="Hero", command=select_hero, font=(FONT_NAME, 12), bg="#8a5cf6", fg="white",
                      width=12).pack(pady=5)
            tk.Button(target_win, text="Sage", command=select_sage, font=(FONT_NAME, 12), bg="#4ecdc4", fg="white",
                      width=12).pack(pady=5)

            target_win.wait_window()
            return selected.get()

        def use_item():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Peringatan", "Silakan pilih item untuk digunakan.", parent=win)
                return

            item_text = listbox.get(selected_indices[0])
            item_name_to_find = item_text.split(" x")[0]

            # Temukan objek item inventaris berdasarkan nama
            item_to_use = None
            for item in self.party.inventory.keys():
                if item.name == item_name_to_find:
                    item_to_use = item
                    break

            if not item_to_use:
                messagebox.showerror("Error", "Item tidak ditemukan.", parent=win)
                return

            # Konfirmasi jumlah inventaris > 0 sebelum menggunakan
            if self.party.inventory.get(item_to_use, 0) <= 0:
                messagebox.showwarning("Gagal", f"Item tidak tersedia dalam inventaris.", parent=win)
                return

            target_name = choose_target_player()
            if not target_name:
                return

            target_player = next((p for p in self.party.members if p.name.lower() == target_name.lower()), None)
            if not target_player:
                messagebox.showerror("Error", "Pemain tidak ditemukan.", parent=win)
                return

            if item_to_use.item_type == ITEM_TYPE_POTION:
                result = target_player.use_potion(item_to_use, party=self.party)
                if "Menggunakan" in result or "dihidupkan kembali" in result:
                    self.party.remove_item(item_to_use, 1)
            elif item_to_use.item_type == ITEM_TYPE_EQUIPMENT:
                result = target_player.equip_item(item_to_use, self.party)
            else:
                messagebox.showinfo("Info", "Item tidak bisa digunakan.", parent=win)
                return

            messagebox.showinfo("Hasil", result, parent=win)
            self.update_all_ui()
            refresh_list()

        refresh_list()

        btn_frame = tk.Frame(win, bg="#2d2d44")
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Gunakan/Lengkapi", command=use_item, font=(FONT_NAME, 12), bg="#3D9970",
                  fg="white").pack(side="left", padx=6)
        tk.Button(btn_frame, text="Tutup", command=win.destroy, font=(FONT_NAME, 12), bg="#aaa", fg="black").pack(
            side="left", padx=6)

    def open_shop_window(self):
        shop_items = [
            HEALTH_POTION,
            MP_POTION,
            WOODEN_SWORD,
            IRON_SWORD,
            LUCKY_CHARM,
            CRIT_RING,
            CHAINMAIL_ARMOR,
            REVIVE_POTION,
            MAGIC_STAFF,
            MYSTIC_ROBE,
            MAGIC_RING,
        ]
        win = tk.Toplevel(self.root)
        win.title("Toko")
        win.transient(self.root)
        win.grab_set()
        win.geometry("500x400")
        win.configure(bg="#2d2d44")

        listbox = tk.Listbox(win, font=(FONT_NAME, 12), width=60, height=12, bg="#3c3c54", fg="white",
                             selectbackground="#28a745")
        listbox.pack(padx=12, pady=8)
        for item in shop_items:
            listbox.insert(tk.END, f"{item.name} ({item.price} Emas) - {item.description}")

        def buy_item():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Peringatan", "Silakan pilih item yang ingin dibeli.", parent=win)
                return

            item = shop_items[selected_indices[0]]

            if self.party.gold < item.price:
                messagebox.showwarning("Gagal", "Emas tidak cukup.", parent=win)
                return

            self.party.spend_gold(item.price)
            self.party.add_item(item, 1)
            messagebox.showinfo(
                "Berhasil",
                f"Item {item.name} berhasil dibeli dan ditambahkan ke inventaris bersama.",
                parent=win)
            self.update_all_ui()

        btn_frame = tk.Frame(win, bg="#2d2d44")
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Beli", command=buy_item, font=(FONT_NAME, 12), bg="#007b40", fg="white").pack(
            side="left", padx=6)
        tk.Button(btn_frame, text="Tutup", command=win.destroy, font=(FONT_NAME, 12), bg="#aaa", fg="black").pack(
            side="left", padx=6)

