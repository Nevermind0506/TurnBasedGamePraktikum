import tkinter as tk
from tkinter import messagebox, simpledialog
import random
from main import (
    Player, Monster, BossMonster,
    ITEM_TYPE_POTION, ITEM_TYPE_EQUIPMENT,
    HEALTH_POTION, MP_POTION, WOODEN_SWORD, IRON_SWORD,
    LEATHER_ARMOR, CHAINMAIL_ARMOR, LUCKY_CHARM, CRIT_RING
)

# Konstanta untuk ukuran UI dan font
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FONT_NAME = "Helvetica"
FONT_SIZE = 12

class RPGGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Turn-Based RPG Game")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")  # Latar belakang Biru Teknologi Gelap

        self.stage = 1
        self.player = Player()
        self.monsters = []  # daftar monster tahap ini
        self.active_monster_index = 0  # monster mana yang menjadi target pemain / giliran dari monster
        self.is_player_turn = True
        self.in_battle = False
        self.game_over = False
        self.player_defending = False

        # Mengatur frame UI
        self.setup_frames()

        # Mengatur UI pemain dan monster
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

        self.player_frame = tk.LabelFrame(self.main_frame, text="Pemain", fg="#8a5cf6", bg="#2d2d44",
                                          font=(FONT_NAME, 14, "bold"))
        self.player_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.monster_frame = tk.LabelFrame(self.main_frame, text="Musuh", fg="#d44e4e", bg="#2d2d44",
                                           font=(FONT_NAME, 14, "bold"))
        self.monster_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.monster_frame.columnconfigure(0, weight=1)
        self.monster_frame.columnconfigure(1, weight=1)

        self.buttons_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.buttons_frame.pack(padx=20, pady=10)

        self.upgrade_frame = tk.LabelFrame(self.root, text="Peningkatan", fg="#4ecdc4", bg="#2d2d44",
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
        # Membuat UI untuk hingga 2 monster berdampingan
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
        self.button_attack = tk.Button(self.buttons_frame, text="Serang", command=self.player_attack_action,
                                       font=(FONT_NAME, 12, "bold"), bg="#8a5cf6", fg="white", width=14, height=2)
        self.button_attack.grid(row=0, column=0, padx=8, pady=8)

        self.button_special = tk.Button(self.buttons_frame, text="Serangan Spesial (MP 15)", command=self.player_special_attack_action,
                                        font=(FONT_NAME, 12, "bold"), bg="#4ecdc4", fg="white", width=18, height=2)
        self.button_special.grid(row=0, column=1, padx=8, pady=8)

        self.button_defend = tk.Button(self.buttons_frame, text="Bertahan", command=self.player_defend_action,
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
        self.upgrade_attack_button = tk.Button(self.upgrade_buttons_frame, text="Serangan +2", command=lambda: self.upgrade_stat("attack"),
                                               font=(FONT_NAME, 10, "bold"), width=btn_width, bg="#7c4dff", fg="white")
        self.upgrade_defense_button = tk.Button(self.upgrade_buttons_frame, text="Pertahanan +2", command=lambda: self.upgrade_stat("defense"),
                                                font=(FONT_NAME, 10, "bold"), width=btn_width, bg="#7c4dff", fg="white")
        self.upgrade_evasion_button = tk.Button(self.upgrade_buttons_frame, text="Menghindar +3%", command=lambda: self.upgrade_stat("evasion"),
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
        self.inventory_button = tk.Button(self.menu_frame, text="Inventaris", command=self.open_inventory_window,
                                          font=(FONT_NAME, 12), bg="#4078c0", fg="white", width=12)
        self.inventory_button.grid(row=0, column=0, padx=20)

        self.shop_button = tk.Button(self.menu_frame, text="Toko", command=self.open_shop_window,
                                     font=(FONT_NAME, 12), bg="#28a745", fg="white", width=12)
        self.shop_button.grid(row=0, column=1, padx=20)

    def create_gold_label(self):
        self.gold_var = tk.StringVar()
        self.gold_label = tk.Label(self.root, textvariable=self.gold_var, font=(FONT_NAME, 14, "bold"),
                                   fg="#ffaa00", bg="#1a1a2e")
        self.gold_label.pack(pady=(2, 0))
        self.update_gold_label()

    def update_gold_label(self):
        self.gold_var.set(f"Emas: {self.player.gold}")

    def update_player_ui(self):
        self.player_hp_var.set(f"HP: {self.player.hp} / {self.player.max_hp}")
        self.player_mp_var.set(f"MP: {self.player.mp} / {self.player.max_mp}")
        self.player_attack_var.set(f"Serangan: {self.player.attack_stat}")
        self.player_defense_var.set(f"Pertahanan: {self.player.defense_stat}")
        self.player_evasion_var.set(f"Menghindar: {self.player.evasion_stat}%")
        self.player_level_var.set(f"Level: {self.player.level} | XP: {self.player.xp}/100 | Poin Peningkatan: {self.player.upgrade_points}")
        weapon = self.player.equipped_items["weapon"].name if self.player.equipped_items["weapon"] else "Kosong"
        armor = self.player.equipped_items["armor"].name if self.player.equipped_items["armor"] else "Kosong"
        accessory = self.player.equipped_items["accessory"].name if self.player.equipped_items["accessory"] else "Kosong"
        self.equipped_items_var.set(f"Senjata: {weapon} | Baju Zirah: {armor} | Aksesori: {accessory}")

    def update_monster_ui(self):
        for i in range(2):
            if i < len(self.monsters):
                m = self.monsters[i]
                self.monster_labels[i].set(m.name)
                self.monster_hp_vars[i].set(f"HP: {m.hp} / {m.max_hp}")
                self.monster_mp_vars[i].set(f"MP: {m.mp} / {m.max_mp}")
                self.monster_attack_vars[i].set(f"Serangan: {m._base_attack}")
                self.monster_defense_vars[i].set(f"Pertahanan: {m._base_defense}")
                self.monster_evasion_vars[i].set(f"Menghindar: {m._base_evasion}%")
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
        self.upgrade_info_var.set(f"Poin Peningkatan Tersedia: {self.player.upgrade_points}")
        state = "normal" if self.player.upgrade_points > 0 else "disabled"
        self.upgrade_attack_button.configure(state=state)
        self.upgrade_defense_button.configure(state=state)
        self.upgrade_evasion_button.configure(state=state)
        self.upgrade_mp_button.configure(state=state)
        self.upgrade_hp_button.configure(state=state)

    def generate_shop_items(self):
        # Subset item toko potensial yang berbeda
        sets = [
            [HEALTH_POTION, MP_POTION, WOODEN_SWORD],
            [HEALTH_POTION, IRON_SWORD, LEATHER_ARMOR],
            [MP_POTION, CHAINMAIL_ARMOR, LUCKY_CHARM],
            [HEALTH_POTION, MP_POTION, IRON_SWORD, LUCKY_CHARM, CRIT_RING],
        ]
        # Pilih set acak setiap tahap
        return random.choice(sets)

    def start_stage(self):
        self.player_defending = False
        if self.stage % 3 == 0:
            # Tahap bos
            boss_stage = self.stage // 3
            self.monsters = [BossMonster(f"Boss Tahap {self.stage}", stage=boss_stage)]
            self.status_var.set(f"BOSS yang kuat muncul di Tahap {self.stage}!")
        else:
            # Tahap normal dengan dua monster
            self.monsters = [Monster(f"Monster 1 Tahap {self.stage}", stage=self.stage),
                             Monster(f"Monster 2 Tahap {self.stage}", stage=self.stage)]
            self.status_var.set(f"Dua monster liar muncul di Tahap {self.stage}!")
        self.active_monster_index = 0  # Pemain menargetkan monster pertama pada awalnya
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
                loot_text = f"Anda menemukan jarahan: {loot_names}!"
            else:
                loot_text = "Tidak ada jarahan yang jatuh kali ini."
            self.update_player_ui()
            self.update_upgrade_ui()
            self.status_var.set(f"Anda mengalahkan musuh! Memperoleh {xp_earned} XP dan {gold_earned} Emas! {loot_text} Bersiap untuk tahap selanjutnya...")
            self.stage += 1
            self.root.after(4000, self.start_stage)
        else:
            self.status_var.set("Permainan Berakhir! Anda dikalahkan.")
            messagebox.showinfo("Permainan Berakhir", "Anda telah dikalahkan! Permainan akan diatur ulang.")
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
        self.status_var.set("Permainan Diatur Ulang. Memulai dari Tahap 1...")
        self.root.after(2000, self.start_stage)

    def player_attack_action(self):
        if not self.in_battle or not self.is_player_turn:
            return
        target = self.get_current_target_monster()
        if not target:
            self.status_var.set("Tidak ada target yang valid untuk diserang.")
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
            self.status_var.set("Tidak ada target yang valid untuk diserang.")
            return
        result = self.player.special_attack(target)
        self.status_var.set(result)
        self.update_monster_ui()
        self.update_player_ui()
        self.check_battle_status()

    def player_defend_action(self):
        if not self.in_battle or not self.is_player_turn:
            return
        self.status_var.set("Pemain bertahan dan akan menerima kerusakan yang lebih sedikit pada serangan berikutnya!")
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
        # Jika monster yang ditargetkan saat ini mati, alihkan target ke monster lain yang masih hidup jika ada
        if not self.monsters[self.active_monster_index].is_alive:
            for idx, m in enumerate(self.monsters):
                if m.is_alive:
                    self.active_monster_index = idx
                    break
            else:
                # Tidak ada monster yang hidup ditemukan, akhiri pertempuran
                self.end_battle(won=True)
                return
        self.next_turn()

    def next_turn(self):
        # Beralih antara giliran pemain dan monster
        if self.is_player_turn:
            # Giliran pemain selesai, giliran monster dimulai
            self.is_player_turn = False
            self.update_action_buttons(state="disabled")
            self.active_monster_index = 0
            self.root.after(1500, self.monster_turn)
        else:
            # Giliran monster selesai atau tidak ada monster tersisa, giliran pemain
            self.is_player_turn = True
            self.update_action_buttons(state="normal")

    def monster_turn(self):
        # Jika tidak ada monster yang hidup, akhiri pertempuran
        alive_monsters = [m for m in self.monsters if m.is_alive]
        if not alive_monsters:
            self.end_battle(won=True)
            return
        if self.active_monster_index >= len(self.monsters):
            # Semua monster telah bertindak, kembali ke giliran pemain
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
            result += " Pemain bertahan dan mengurangi kerusakan!"
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
        # Jika hanya ada satu monster yang hidup atau hanya ada satu monster, targetkan itu
        alive_monsters = [m for m in self.monsters if m.is_alive]
        if len(alive_monsters) == 1:
            return alive_monsters[0]

        # Beberapa monster hidup - tanyakan kepada pemain mana yang akan ditargetkan
        alive_indexes = [idx for idx, m in enumerate(self.monsters) if m.is_alive]
        # Prompt GUI untuk pemilihan target: dialog sederhana
        target_names = [self.monsters[i].name for i in alive_indexes]
        choice = simpledialog.askstring("Pilih Target",
                                        f"Beberapa musuh hidup. Pilih target berdasarkan nomor:\n" +
                                        "\n".join(f"{i+1}. {name}" for i, name in enumerate(target_names)))
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(target_names):
                return self.monsters[alive_indexes[choice_idx]]
        except:
            pass
        # Default ke monster hidup pertama jika input tidak valid
        return self.monsters[alive_indexes[0]] if alive_indexes else None

    # Jendela Inventaris dan Toko --------------------------------------------------
    def open_inventory_window(self):
        if hasattr(self, "inventory_window") and self.inventory_window.winfo_exists():
            self.inventory_window.lift()
            return
        self.inventory_window = tk.Toplevel(self.root)
        self.inventory_window.title("Inventaris")
        self.inventory_window.geometry("450x350")
        self.inventory_window.configure(bg="#2d2d44")

        tk.Label(self.inventory_window, text="Item Anda", font=(FONT_NAME, 14, "bold"), bg="#2d2d44", fg="#b2cdfa").pack(pady=(8, 6))

        self.inventory_listbox = tk.Listbox(self.inventory_window, font=(FONT_NAME, 12), width=40, height=12)
        self.inventory_listbox.pack(padx=12, pady=8)

        buttons_frame = tk.Frame(self.inventory_window, bg="#2d2d44")
        buttons_frame.pack(pady=6)

        self.use_button = tk.Button(buttons_frame, text="Gunakan / Lengkapi", command=self.use_selected_inventory_item,
                                    font=(FONT_NAME, 12), width=12, bg="#3D9970", fg="white")
        self.use_button.pack(side="left", padx=6)

        self.close_inv_button = tk.Button(buttons_frame, text="Tutup", command=self.inventory_window.destroy,
                                          font=(FONT_NAME, 12), width=12, bg="#aaa", fg="black")
        self.close_inv_button.pack(side="left", padx=6)

        self.refresh_inventory_list()

    def refresh_inventory_list(self):
        self.inventory_listbox.delete(0, tk.END)
        if not self.player.inventory:
            self.inventory_listbox.insert(tk.END, "<Inventaris kosong>")
            self.use_button.configure(state="disabled")
            return
        for item, qty in self.player.inventory.items():
            line = f"{item.name} x{qty} - {item.description}"
            self.inventory_listbox.insert(tk.END, line)
        self.use_button.configure(state="normal")

    def use_selected_inventory_item(self):
        selection = self.inventory_listbox.curselection()
        if not selection:
            messagebox.showinfo("Pilih Item", "Silakan pilih item untuk digunakan atau dilengkapi.")
            return
        index = selection[0]
        if index >= len(self.player.inventory):
            return
        item = list(self.player.inventory.keys())[index]

        if item.item_type == ITEM_TYPE_POTION:
            result = self.player.use_potion(item)
            messagebox.showinfo("Item Digunakan", result)
            self.update_player_ui()
        elif item.item_type == ITEM_TYPE_EQUIPMENT:
            result = self.player.equip_item(item)
            messagebox.showinfo("Lengkapi Item", result)
            self.update_player_ui()
        else:
            messagebox.showinfo("Item Tidak Valid", "Item ini tidak dapat digunakan atau dilengkapi.")
            return
        self.refresh_inventory_list()

    def open_shop_window(self):
        if hasattr(self, "shop_window") and self.shop_window.winfo_exists():
            self.shop_window.lift()
            return
        self.shop_window = tk.Toplevel(self.root)
        self.shop_window.title("Toko Ramuan")
        self.shop_window.geometry("450x350")
        self.shop_window.configure(bg="#2d2d44")

        tk.Label(self.shop_window, text="Selamat Datang di Toko", font=(FONT_NAME, 14, "bold"), bg="#2d2d44", fg="#ffd54f").pack(pady=(8, 6))

        self.shop_listbox = tk.Listbox(self.shop_window, font=(FONT_NAME, 12), width=40, height=12)
        self.shop_listbox.pack(padx=12, pady=8)

        self.shop_items = self.generate_shop_items()
        for item in self.shop_items:
            line = f"{item.name} - Harga: {item.price} Emas - {item.description}"
            self.shop_listbox.insert(tk.END, line)

        shop_buttons_frame = tk.Frame(self.shop_window, bg="#2d2d44")
        shop_buttons_frame.pack(pady=6)

        self.buy_button = tk.Button(shop_buttons_frame, text="Beli", command=self.buy_selected_shop_item,
                                    font=(FONT_NAME, 12), width=12, bg="#007b40", fg="white")
        self.buy_button.pack(side="left", padx=6)

        self.close_shop_button = tk.Button(shop_buttons_frame, text="Tutup", command=self.shop_window.destroy,
                                           font=(FONT_NAME, 12), width=12, bg="#aaa", fg="black")
        self.close_shop_button.pack(side="left", padx=6)

    def buy_selected_shop_item(self):
        selection = self.shop_listbox.curselection()
        if not selection:
            messagebox.showinfo("Pilih Item", "Silakan pilih item untuk dibeli.")
            return
        index = selection[0]
        if index >= len(self.shop_items):
            return
        item = self.shop_items[index]
        if self.player.gold >= item.price:
            self.player.gold -= item.price
            self.player.add_item(item, 1)
            self.update_gold_label()
            messagebox.showinfo("Pembelian Berhasil", f"Anda membeli 1x {item.name}.")
        else:
            messagebox.showwarning("Emas Tidak Cukup", "Anda tidak memiliki cukup emas untuk membeli item ini.")