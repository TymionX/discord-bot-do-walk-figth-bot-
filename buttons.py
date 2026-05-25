import discord


async def verification(view, interaction, role):
    if interaction.user.id in view.clicked_fight:
        await interaction.response.send_message("⏳ Już wybrałeś w tej turze!", ephemeral=True)
        return False
    if interaction.user.id not in view.players:
        await interaction.response.send_message("❌ Nie bierzesz udziału w walce!", ephemeral=True)
        return False
    if role == "attacker" and interaction.user.id != view.logic.attacker.id:
        await interaction.response.send_message("❌ To nie twoja opcja!", ephemeral=True)
        return False
    if role == "defender" and interaction.user.id != view.logic.defender.id:
        await interaction.response.send_message("❌ To nie twoja opcja!", ephemeral=True)
        return False
    view.clicked_fight.add(interaction.user.id)
    return True


async def factory(view, interaction, move):
    if interaction.user.id == view.player1.id:
        view.player1.fight_move = move
        children = view.player1_view.children
        embed = view.player1_embed
        msg = view.player1_message
        current_view = view.player1_view
    else:
        view.player2.fight_move = move
        children = view.player2_view.children
        embed = view.player2_embed
        msg = view.player2_message
        current_view = view.player2_view

    label = interaction.data.get("custom_id").split("_")[1]  
    embed.description = f"Wybrałeś {label}"

    for child in children:
        if isinstance(child, discord.ui.Button):
            child.disabled = True

    await msg.edit(embed=embed, view=current_view)  


def pkn_callback_factory(move):
    async def callback(view, interaction):
        if interaction.user.id in view.clicked_fight:
            await interaction.response.send_message("⏳ Już wybrałeś w tej turze!", ephemeral=True)
            return
        if interaction.user.id not in view.players:
            await interaction.response.send_message("❌ Nie bierzesz udziału w walce!", ephemeral=True)
            return
        view.clickedPKN.add(interaction.user.id)
        if interaction.user.id == view.player1.id:
            view.logic.player1.move = move
        else:
            view.logic.player2.move = move
        await view.logic.pkn(interaction)
    return callback


def atak_callback_factory(spread, komunikat):
    async def callback(view, interaction):
        if not await verification(view, interaction, "attacker"):
            return
        move = ["atak", spread, komunikat]
        await factory(view, interaction, move)
        await view.logic.conclude(interaction)
    return callback

def zwieksz_atk_callback_factory(factor, komunikat):
    async def callback(view, interaction):
        if not await verification(view, interaction, "attacker"):
            return
        move = ["zwieksz_atk", factor, komunikat]
        await factory(view, interaction, move)
        await view.logic.conclude(interaction)
    return callback

def zwieksz_def_callback_factory(factor, komunikat):
    async def callback(view, interaction):
        if not await verification(view, interaction, "attacker"):
            return
        move = ["zwieksz_def", factor, komunikat]
        await factory(view, interaction, move)
        await view.logic.conclude(interaction)
    return callback

def zmniejsz_enemy_def_callback_factory(factor, komunikat):
    async def callback(view, interaction):
        if not await verification(view, interaction, "attacker"):
            return
        move = ["zmniejsz_enemy_def", factor, komunikat]
        await factory(view, interaction, move)
        await view.logic.conclude(interaction)
    return callback

def zmniejsz_enemy_atk_callback_factory(factor, komunikat):
    async def callback(view, interaction):
        if not await verification(view, interaction, "attacker"):
            return
        move = ["zmniejsz_enemy_atk", factor, komunikat]
        await factory(view, interaction, move)
        await view.logic.conclude(interaction)
    return callback

def leczenie_callback_factory(factor, komunikat):
    async def callback(view, interaction):
        if not await verification(view, interaction, "attacker"):
            return
        move = ["leczenie", factor, komunikat]
        await factory(view, interaction, move)
        await view.logic.conclude(interaction)
    return callback

def leczenie_losowe_callback_factory():
    async def callback(view, interaction):
        if not await verification(view, interaction, "defender"):
            return
        move = ["leczenie_losowe"]
        await factory(view, interaction, move)
        await view.logic.conclude(interaction)
    return callback

def obrona_callback_factory():
    async def callback(view, interaction):
        if not await verification(view, interaction, "defender"):
            return
        move = ["obrona"]
        await factory(view, interaction, move)
        await view.logic.conclude(interaction)
    return callback

def unik_callback_factory():
    async def callback(view, interaction):
        if not await verification(view, interaction, "defender"):
            return
        move = ["unik"]
        await factory(view, interaction, move)
        await view.logic.conclude(interaction)
    return callback




normal_spread = [0.7, 1.2]
rare_spread = [0.9, 1.3]
epic_spread = [0.7, 2]

pkn_buttons = {
    1: ("PAPIER 📰", discord.ButtonStyle.primary, pkn_callback_factory(1)),
    2: ("KAMIEŃ 🪨", discord.ButtonStyle.primary, pkn_callback_factory(2)),
    3: ("NOŻYCE ✂️", discord.ButtonStyle.primary, pkn_callback_factory(3))
}
attacker_buttons = {
    "atak": ("ATAK", "Atakuje przeciwnika!", discord.ButtonStyle.danger, atak_callback_factory(normal_spread, " zadał x obrażeń!")),
    "zwiększenie_ataku": ("ATK +1", "Zwiększa twój atak o 1", discord.ButtonStyle.danger, zwieksz_atk_callback_factory(1, " zwiększył swój ATK o 1")),
    "zwiększenie_obrony": ("DEF +1", "Zwiększa twoją obronę o 1", discord.ButtonStyle.danger, zwieksz_def_callback_factory(1," zwiększył swój DEF o 1")),
    "zmniejszenie_obrony_przeciwnika": ("ENEMY DEF -1", "Zmniejsza obronę przeciwnika o 1", discord.ButtonStyle.danger, zmniejsz_enemy_def_callback_factory(1," zmniejszył DEF przeciwnika o 1")),
    "zmniejszenie_ataku_przeciwnika": ("ENEMY ATK -1", "Zmniejsza atak przeciwnika o 1", discord.ButtonStyle.danger, zmniejsz_enemy_atk_callback_factory(1," zmniejszył ATK przeciwnika o 1")),
    "gwarantowane_uzdrowienie": ("HP +15", " uleczył się o 15 HP", discord.ButtonStyle.danger, leczenie_callback_factory(15, "Leczy cię o 15 HP"))
}
# rare_attacker_buttons = {
#     "rare_atak": ("SILNY ATAK", "Atakuje przeciwnika mocniej!", discord.ButtonStyle.danger, atak_callback_factory(rare_spread)),
#     "rare_zwiększenie_ataku": ("ATK +2", "Zwiększa twój atak o 2", discord.ButtonStyle.danger, zwieksz_atk_callback_factory(2)),
#     "rare_zwiększenie_obrony": ("DEF +2", "Zwiększa twoją obronę o 2", discord.ButtonStyle.danger, zwieksz_def_callback_factory(2)),
#     "rare_zmniejszenie_obrony_przeciwnika": ("ENEMY DEF -2", "Zmniejsza obronę przeciwnika o 2", discord.ButtonStyle.danger, zmniejsz_enemy_def_callback_factory(2)),
#     "rare_zmniejszenie_ataku_przeciwnika": ("ENEMY ATK -2", "Zmniejsza atak przeciwnika o 2", discord.ButtonStyle.danger, zmniejsz_enemy_atk_callback_factory(2)),
#     "rare_gwarantowane_uzdrowienie": ("HP +30","Leczy cię o 30 HP", discord.ButtonStyle.danger, leczenie_callback_factory(30))
# }
# epic_attacker_buttons = {
#     "epic_atak": ("EPICKI ATAK", "Ryzykowny ruch! Może zadać ogromne obrażenia a może małe", discord.ButtonStyle.danger, atak_callback_factory(epic_spread)),
#     "epic_zwiększenie_ataku": ("ATK +3","Zwiększa twój atak o 3", discord.ButtonStyle.danger, zwieksz_atk_callback_factory(3)),
#     "epic_zwiększenie_obrony": ("DEF +3","Zwiększa twoją obronę o 3", discord.ButtonStyle.danger, zwieksz_def_callback_factory(3)),
#     "epic_zmniejszenie_obrony_przeciwnika": ("ENEMY DEF -3", "Zmniejsza obronę przeciwnika o 3", discord.ButtonStyle.danger, zmniejsz_enemy_def_callback_factory(3)),
#     "epic_zmniejszenie_ataku_przeciwnika": ("ENEMY ATK -3", "Zmniejsza atak przeciwnika o 3", discord.ButtonStyle.danger, zmniejsz_enemy_atk_callback_factory(3)),
#     "epic_gwarantowane_uzdrowienie": ("HP +50", "Leczy cię o 50 HP", discord.ButtonStyle.danger, leczenie_callback_factory(50))
# }
defender_buttons = {
    "OBRONA": ("OBRONA", "Obroń się przed atakiem przeciwnika!", discord.ButtonStyle.danger, obrona_callback_factory()),
    "LECZENIE": ("LECZENIE", "Leczenie o wartość o której zdecyduje rzut dwoma kostkami!", discord.ButtonStyle.danger, leczenie_losowe_callback_factory()),
    "UNIK": ("UNIK", "Szansa na uniknięcie całkowicie uniknięcie ataku przeciwnika!",discord.ButtonStyle.danger, unik_callback_factory()),
}