import tkinter as tk
from tkinter import messagebox, simpledialog
import random
from game_logic import (
    Player, Monster, BossMonster,
    ITEM_TYPE_POTION, ITEM_TYPE_EQUIPMENT,
    HEALTH_POTION, MP_POTION, WOODEN_SWORD, IRON_SWORD,
    LEATHER_ARMOR, CHAINMAIL_ARMOR, LUCKY_CHARM, CRIT_RING
)

# Constants for UI
WINDOW_WIDTH = 900
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
        self.player = Player()
        self.monsters = []
        self.player_defending = False

        self.setup_frames()
        self.create_widgets()
        
        self.start_stage()

    def setup_frames(self):
        self.main_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=10)
        self.main_frame.grid_columnconfigure((0, 1), weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.player_frame = tk.LabelFrame(self.main_frame, text="Pemain", fg="#8a5cf6", bg="#2d2d44", font=(FONT_NAME, 14, "bold"))
        self.player_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.monster_frame = tk.LabelFrame(self.main_frame, text="Musuh", fg="#d44e4e", bg="#2d2d44", font=(FONT_NAME, 14, "bold"))
        self.monster_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.monster_frame.grid_columnconfigure((0, 1), weight=1)
        self.monster_frame.grid_rowconfigure(0, weight=1)

        self.status_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.status_frame.pack(fill="x", padx=20, pady=5)

        self.buttons_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.buttons_frame.pack(pady=5)
        
        self.upgrade_frame = tk.LabelFrame(self.root, text="Peningkatan", fg="#4ecdc4", bg="#2d2d44", font=(FONT_NAME, 12, "bold"))
        self.upgrade_frame.pack(fill="x", padx=20, pady=5)

        self.menu_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.menu_frame.pack(pady=10)

    def create_widgets(self):
        # Player UI
        self.player_vars = {
            "name": tk.StringVar(), "hp": tk.StringVar(), "mp": tk.StringVar(),
            "stats": tk.StringVar(), "level": tk.StringVar(), "equipped": tk.StringVar()
        }
        tk.Label(self.player_frame, textvariable=self.player_vars["name"], font=(FONT_NAME, 16, 'bold'), fg="#8a5cf6", bg="#2d2d44").pack(pady=(10,5))
        tk.Label(self.player_frame, textvariable=self.player_vars["hp"], font=(FONT_NAME, 12), fg="#ffa3a3", bg="#2d2d44").pack()
        tk.Label(self.player_frame, textvariable=self.player_vars["mp"], font=(FONT_NAME, 12), fg="#4dc4ff", bg="#2d2d44").pack()
        tk.Label(self.player_frame, textvariable=self.player_vars["stats"], font=(FONT_NAME, 12), fg="#b29cff", bg="#2d2d44").pack()
        tk.Label(self.player_frame, textvariable=self.player_vars["level"], font=(FONT_NAME, 12, "italic"), fg="#dedede", bg="#2d2d44").pack(pady=5)
        tk.Label(self.player_frame, textvariable=self.player_vars["equipped"], font=(FONT_NAME, 11), fg="#76ffc1", bg="#2d2d44", justify="left").pack(pady=5, padx=10, fill='x')

        # Monster UI
        self.monster_widgets = []
        for i in range(2):
            m_frame = tk.Frame(self.monster_frame, bg="#2d2d44", bd=2, relief="groove")
            m_frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            m_vars = {"name": tk.StringVar(), "hp": tk.StringVar(), "stats": tk.StringVar()}
            tk.Label(m_frame, textvariable=m_vars["name"], font=(FONT_NAME, 14, 'bold'), fg="#d44e4e", bg="#2d2d44").pack(pady=(10, 5))
            tk.Label(m_frame, textvariable=m_vars["hp"], font=(FONT_NAME, 12), fg="#ffa3a3", bg="#2d2d44").pack()
            tk.Label(m_frame, textvariable=m_vars["stats"], font=(FONT_NAME, 12), fg="#efa7a7", bg="#2d2d44").pack(pady=(0,10))
            self.monster_widgets.append({"frame": m_frame, "vars": m_vars})

        # Status Label
        self.status_var = tk.StringVar()
        tk.Label(self.status_frame, textvariable=self.status_var, font=(FONT_NAME, 12), fg="#E0E0E0", bg="#1a1a2e", wraplength=850).pack()
        
        # Gold Label
        self.gold_var = tk.StringVar()
        tk.Label(self.menu_frame, textvariable=self.gold_var, font=(FONT_NAME, 14, "bold"), fg="#ffaa00", bg="#1a1a2e").grid(row=0, column=2, padx=20)
        
        # Action Buttons
        self.action_buttons = {
            "attack": tk.Button(self.buttons_frame, text="Serang", command=self.player_attack_action, font=(FONT_NAME, 12, "bold"), bg="#8a5cf6", fg="white", width=14, height=2),
            "special": tk.Button(self.buttons_frame, text="Spesial (15 MP)", command=self.player_special_attack_action, font=(FONT_NAME, 12, "bold"), bg="#4ecdc4", fg="white", width=16, height=2),
            "defend": tk.Button(self.buttons_frame, text="Bertahan", command=self.player_defend_action, font=(FONT_NAME, 12, "bold"), bg="#ffa500", fg="black", width=14, height=2)
        }
        self.action_buttons["attack"].grid(row=0, column=0, padx=8)
        self.action_buttons["special"].grid(row=0, column=1, padx=8)
        self.action_buttons["defend"].grid(row=0, column=2, padx=8)

        # Upgrade Buttons
        self.upgrade_info_var = tk.StringVar()
        tk.Label(self.upgrade_frame, textvariable=self.upgrade_info_var, font=(FONT_NAME, 12), fg="#4ecdc4", bg="#2d2d44").pack(pady=5)
        u_buttons_frame = tk.Frame(self.upgrade_frame, bg="#2d2d44")
        u_buttons_frame.pack(pady=5)
        self.upgrade_buttons = {
            "hp": tk.Button(u_buttons_frame, text="HP +10", command=lambda: self.upgrade_stat("hp"), font=(FONT_NAME, 10, "bold"), width=12, bg="#7c4dff", fg="white"),
            "mp": tk.Button(u_buttons_frame, text="MP +5", command=lambda: self.upgrade_stat("mp"), font=(FONT_NAME, 10, "bold"), width=12, bg="#7c4dff", fg="white"),
            "attack": tk.Button(u_buttons_frame, text="Serangan +2", command=lambda: self.upgrade_stat("attack"), font=(FONT_NAME, 10, "bold"), width=12, bg="#7c4dff", fg="white"),
            "defense": tk.Button(u_buttons_frame, text="Pertahanan +2", command=lambda: self.upgrade_stat("defense"), font=(FONT_NAME, 10, "bold"), width=12, bg="#7c4dff", fg="white"),
            "evasion": tk.Button(u_buttons_frame, text="Hindaran +3%", command=lambda: self.upgrade_stat("evasion"), font=(FONT_NAME, 10, "bold"), width=12, bg="#7c4dff", fg="white")
        }
        for i, btn in enumerate(self.upgrade_buttons.values()):
            btn.grid(row=0, column=i, padx=5)

        # Menu Buttons
        tk.Button(self.menu_frame, text="Inventaris", command=self.open_inventory_window, font=(FONT_NAME, 12), bg="#4078c0", fg="white", width=12).grid(row=0, column=0, padx=20)
        tk.Button(self.menu_frame, text="Toko", command=self.open_shop_window, font=(FONT_NAME, 12), bg="#28a745", fg="white", width=12).grid(row=0, column=1, padx=20)

    def update_all_ui(self):
        # Update Player UI
        p = self.player
        self.player_vars["name"].set(p.name)
        self.player_vars["hp"].set(f"HP: {p.hp} / {p.max_hp}")
        self.player_vars["mp"].set(f"MP: {p.mp} / {p.max_mp}")
        self.player_vars["stats"].set(f"Serangan: {p.attack_stat} | Pertahanan: {p.defense_stat} | Hindaran: {p.evasion_stat}%")
        self.player_vars["level"].set(f"Level: {p.level} | XP: {p.xp}/100")
        
        weapon = p.equipped_items.get('weapon')
        armor = p.equipped_items.get('armor')
        accessory = p.equipped_items.get('accessory')
        
        equipped_text = (
            f"Senjata: {weapon.name if weapon else 'Kosong'}\n"
            f"Zirah: {armor.name if armor else 'Kosong'}\n"
            f"Aksesori: {accessory.name if accessory else 'Kosong'}"
        )
        self.player_vars["equipped"].set(equipped_text)

        # Update Monster UI
        for i, m_widget in enumerate(self.monster_widgets):
            if i < len(self.monsters) and self.monsters[i].is_alive:
                m = self.monsters[i]
                m_widget["vars"]["name"].set(m.name)
                m_widget["vars"]["hp"].set(f"HP: {m.hp} / {m.max_hp}")
                m_widget["vars"]["stats"].set(f"ATK: {m.attack_stat} | DEF: {m.defense_stat}")
                m_widget["frame"].grid()
            else:
                m_widget["frame"].grid_remove()

        # Update Gold
        self.gold_var.set(f"Emas: {self.player.gold}")
        
        # Update Upgrade UI
        self.upgrade_info_var.set(f"Poin Peningkatan: {self.player.upgrade_points}")
        state = "normal" if self.player.upgrade_points > 0 else "disabled"
        for btn in self.upgrade_buttons.values():
            btn.config(state=state)

    def set_action_buttons_state(self, state):
        for btn in self.action_buttons.values():
            btn.config(state=state)
    
    def start_stage(self):
        self.player_defending = False
        if self.stage % 3 == 0:
            boss_stage_num = self.stage // 3
            self.monsters = [BossMonster(f"Boss Tahap {boss_stage_num}", stage=boss_stage_num)]
            self.status_var.set(f"BOSS yang kuat muncul!")
        else:
            monster_count = 1 if self.stage == 1 else 2
            self.monsters = [Monster(f"Monster #{i+1}", stage=self.stage) for i in range(monster_count)]
            self.status_var.set(f"{len(self.monsters)} monster liar muncul!")

        self.update_all_ui()
        self.set_action_buttons_state("normal")

    def end_battle(self, won):
        self.set_action_buttons_state("disabled")
        if won:
            xp_earned = 25 * self.stage
            gold_earned = 50 * self.stage
            self.player.gain_xp(xp_earned)
            self.player.gold += gold_earned
            
            all_drops = sum([m.drop_loot() for m in self.monsters], [])
            for item in all_drops:
                self.player.add_item(item)

            drop_names = ", ".join(item.name for item in all_drops) if all_drops else "Tidak ada."
            result_text = (f"Menang! Dapat {xp_earned} XP & {gold_earned} Emas.\n"
                           f"Jarahan: {drop_names}\nBersiap untuk tahap selanjutnya...")
            self.status_var.set(result_text)
            self.stage += 1
            self.root.after(4000, self.start_stage)
        else:
            self.status_var.set("Permainan Berakhir! Anda telah dikalahkan.")
            messagebox.showinfo("Kalah", "Anda dikalahkan! Permainan akan diatur ulang.")
            self.reset_game()
        self.update_all_ui()

    def reset_game(self):
        self.stage = 1
        self.player = Player()
        self.start_stage()
        
    def execute_player_turn(self, action, *args):
        if not any(m.is_alive for m in self.monsters): return
        
        self.set_action_buttons_state("disabled")
        
        result = action(*args)
        self.status_var.set(result)
        self.update_all_ui()
        
        alive_monsters = [m for m in self.monsters if m.is_alive]
        if not alive_monsters:
            self.end_battle(won=True)
            return

        if self.player.is_alive:
            self.root.after(1500, self.execute_monster_turn)
            
    def player_attack_action(self):
        target = self.choose_target()
        if target:
            self.execute_player_turn(self.player.attack, target)

    def player_special_attack_action(self):
        target = self.choose_target()
        if target:
            self.execute_player_turn(self.player.special_attack, target)
            
    def player_defend_action(self):
        self.player_defending = True
        self.execute_player_turn(lambda: "Anda bersiap untuk bertahan!")

    def execute_monster_turn(self):
        turn_results = []
        for monster in self.monsters:
            if not monster.is_alive: continue
            
            # Simple AI: 20% chance to use special attack
            action = monster.special_attack if random.random() < 0.2 else monster.attack
            result = action(self.player)
            
            if self.player_defending:
                # Defending logic should ideally be in the take_damage method.
                # For now, just show a message.
                result += " (Bertahan!)"
                
            turn_results.append(result)

            if not self.player.is_alive:
                self.status_var.set("\n".join(turn_results))
                self.update_all_ui()
                self.end_battle(won=False)
                return
        
        self.player_defending = False # Defense wears off
        self.status_var.set("\n".join(turn_results))
        self.update_all_ui()
        self.set_action_buttons_state("normal")

    def choose_target(self):
        alive_monsters = [m for m in self.monsters if m.is_alive]
        if not alive_monsters: return None
        if len(alive_monsters) == 1: return alive_monsters[0]

        target_names = [f"{i+1}. {m.name}" for i, m in enumerate(alive_monsters)]
        choice = simpledialog.askstring("Pilih Target", "Pilih target dengan nomor:\n" + "\n".join(target_names), parent=self.root)
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(alive_monsters):
                return alive_monsters[choice_idx]
        except (ValueError, TypeError):
            pass # Invalid input
        
        return alive_monsters[0] # Default to first

    def upgrade_stat(self, stat):
        result = self.player.upgrade_stat(stat)
        self.status_var.set(result)
        self.update_all_ui()

    def open_inventory_window(self):
        win = tk.Toplevel(self.root)
        win.title("Inventaris")
        win.transient(self.root)
        win.grab_set()
        win.geometry("500x400")
        win.configure(bg="#2d2d44")
        
        listbox = tk.Listbox(win, font=(FONT_NAME, 12), width=60, height=12, bg="#3c3c54", fg="white", selectbackground="#8a5cf6")
        listbox.pack(padx=12, pady=8)

        def refresh_list():
            listbox.delete(0, tk.END)
            if not self.player.inventory:
                listbox.insert(tk.END, "<Inventaris kosong>")
                return
            for item, qty in self.player.inventory.items():
                listbox.insert(tk.END, f"{item.name} x{qty} - {item.description}")
        
        def use_item():
            selected_index = listbox.curselection()
            if not selected_index: return
            
            item_name_to_find = listbox.get(selected_index[0]).split(" x")[0]
            item_to_use = next((item for item in self.player.inventory if item.name == item_name_to_find), None)
            
            if not item_to_use: return

            if item_to_use.item_type == ITEM_TYPE_POTION:
                result = self.player.use_potion(item_to_use)
            elif item_to_use.item_type == ITEM_TYPE_EQUIPMENT:
                result = self.player.equip_item(item_to_use)
            else:
                result = "Item tidak bisa digunakan."
            
            messagebox.showinfo("Hasil", result, parent=win)
            self.update_all_ui()
            refresh_list()

        refresh_list()
        
        btn_frame = tk.Frame(win, bg="#2d2d44")
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Gunakan/Lengkapi", command=use_item, font=(FONT_NAME, 12), bg="#3D9970", fg="white").pack(side="left", padx=6)
        tk.Button(btn_frame, text="Tutup", command=win.destroy, font=(FONT_NAME, 12), bg="#aaa", fg="black").pack(side="left", padx=6)

    def open_shop_window(self):
        shop_items = [HEALTH_POTION, MP_POTION, WOODEN_SWORD, IRON_SWORD, LUCKY_CHARM, CRIT_RING, CHAINMAIL_ARMOR]
        win = tk.Toplevel(self.root)
        win.title("Toko")
        win.transient(self.root)
        win.grab_set()
        win.geometry("500x400")
        win.configure(bg="#2d2d44")

        listbox = tk.Listbox(win, font=(FONT_NAME, 12), width=60, height=12, bg="#3c3c54", fg="white", selectbackground="#28a745")
        listbox.pack(padx=12, pady=8)
        for item in shop_items:
            listbox.insert(tk.END, f"{item.name} ({item.price} Emas) - {item.description}")

        def buy_item():
            selected_index = listbox.curselection()
            if not selected_index: return
            item = shop_items[selected_index[0]]

            if self.player.gold >= item.price:
                self.player.gold -= item.price
                self.player.add_item(item, 1)
                messagebox.showinfo("Berhasil", f"Anda membeli {item.name}.", parent=win)
                self.update_all_ui()
            else:
                messagebox.showwarning("Gagal", "Emas tidak cukup.", parent=win)
        
        btn_frame = tk.Frame(win, bg="#2d2d44")
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Beli", command=buy_item, font=(FONT_NAME, 12), bg="#007b40", fg="white").pack(side="left", padx=6)
        tk.Button(btn_frame, text="Tutup", command=win.destroy, font=(FONT_NAME, 12), bg="#aaa", fg="black").pack(side="left", padx=6)
