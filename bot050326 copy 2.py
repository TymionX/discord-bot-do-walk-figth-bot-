import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from buttons import pkn_buttons, attacker_buttons, defender_buttons
import random
import time

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

wins = {1: 2, 2: 3, 3: 1}
elements = " 📰🪨✂️"

class Players:
    def __init__(self, member, hp=100, deff=3, atk=3, lck=0):
        self.id = member.id
        self.name = member.name
        self.hp = hp
        self.deff = deff
        self.atk = atk
        self.lck = lck
        self.enemy = None
        self.move = None
        self.fight_move = None
        self.image = None

class Fight_logic:
    def __init__(self, player1, player2):
        self.player1 = Players(player1)
        self.player2 = Players(player2)
        self.players = {player1.id, player2.id}
        self.clickedPKN = set()
        self.clicked_fight = set()
        self.player1.enemy = self.player2
        self.player2.enemy = self.player1
        self.player1.image = player1.display_avatar.url
        self.player2.image = player2.display_avatar.url
        self.view = None
        self.attacker = None
        self.defender = None

    async def pkn(self, interaction):
        if self.clickedPKN != self.players:
            await interaction.response.defer()
            return
        self.clickedPKN.clear()

        if self.player1.move == self.player2.move:
            msg = "🤝 Remis!"
            self.player1.move = None  
            self.player2.move = None
            await self.view.update_pkn(msg, interaction, False)
            await interaction.response.defer()
            return
        elif wins[self.player1.move] == self.player2.move:
            self.attacker = self.player1
            self.defender = self.player2
        else:
            self.attacker = self.player2
            self.defender = self.player1

        self.defender.lck += 1
        if self.defender.lck > 5:
            self.defender.lck = 5

        msg = f"{self.attacker.name} użył {elements[self.attacker.move]} i zniszczył {elements[self.defender.move]} przeciwnika"

        await interaction.response.defer()
        await self.view.update_pkn(msg, interaction, True)
        await self.attacker_options(self.attacker, interaction)
        await self.defender_options(self.defender, interaction)

        print("LALALLAL", self.player1.name, self.player1.move, self.player2.name, self.player2.move)

        self.player1.move = None
        self.player2.move = None

    async def attacker_options(self, attacker, interaction):
        r = random.choice([0,0,0,1])
        if r == 1:
            opcje = random.sample(list(attacker_buttons.items()), 3)
        elif r==0:
            pozostale = [item for item in attacker_buttons.items() if item[0] != "atak"]
            opcje = [("atak", attacker_buttons["atak"])] + random.sample(pozostale, 2)




        print("attacker", opcje)
        msg = "Atakujesz!, wybierz swój ruch: \n"
        for opcja in opcje:
            label, opis, a, b = opcja[1]
            msg += f"{label}: {opis} \n"
        if self.attacker == self.player1:
            await self.view.update_player1_embed(msg, interaction, "attacker", opcje)
        else:
            await self.view.update_player2_embed(msg, interaction, "attacker", opcje)

    async def defender_options(self, defender, interaction):
        opcje = list(defender_buttons.items())
        print("defender", opcje)
        msg = "Bronisz się!, wybierz swój ruch \n"
        for opcja in opcje:
            label, opis, a, b = opcja[1]
            msg += f"{label}: {opis} \n"
        if self.defender == self.player1:
            await self.view.update_player1_embed(msg, interaction, "defender", opcje)
        else:
            await self.view.update_player2_embed(msg, interaction, "defender", opcje)

    async def conclude(self, interaction):
        if self.clicked_fight != self.players:
            await interaction.response.defer()
            return
        await interaction.response.defer()

        self.clicked_fight.clear()
        msg = ""
        bonus_def = 0
        unik_szansa = 0
        szansa_uniku = {
            0: 0,
            1: 10,
            2: 20,
            3: 30,
            4: 50,
            5: 66
        }

        if not self.defender.fight_move or not self.attacker.fight_move:
            await self.view.update_pkn("❌ Błąd: brak ruchu gracza!", interaction, False)
            return

        print(self.defender.fight_move)
        print(self.attacker.fight_move)

        if self.defender.fight_move[0] == "leczenie_losowe":
            leczenie = random.randint(self.defender.lck, 6) * random.randint(self.defender.lck, 6)
            if self.defender.hp + leczenie > 100:
                leczenie = 100 - self.defender.hp
            self.defender.hp += leczenie
            self.defender.lck -=1
            msg += f"{self.defender.name} uleczył się o {leczenie} HP!\n"
        elif self.defender.fight_move[0] == "obrona":
            bonus_def = 1
            msg += f"{self.defender.name} broni się!\n"
        elif self.defender.fight_move[0] == "unik":
            self.defender.lck = 0 
            unik_szansa = szansa_uniku[self.defender.lck]

        if self.attacker.fight_move[0] == "atak":
            spread_min = self.attacker.fight_move[1][0]
            spread_max = self.attacker.fight_move[1][1]
            atk = self.attacker.atk
            deff = self.defender.deff + bonus_def
            base = (atk * 30) / (1 + deff)
            damage = base * random.uniform(spread_min, spread_max)
            damage = round(damage)
            msg += f"{self.attacker.name} {self.attacker.fight_move[2].replace('x', str(damage))}"
        
            if random.randint(0, 100) > unik_szansa:
                msg += f" i {self.defender.name} nie dał rady uniknąć 🤡!"
                self.defender.hp -= damage
            else:
                msg += f" ale {self.defender.name} dał radę uniknąć 🗿!"
        elif self.attacker.fight_move[0] == "zwieksz_atk":
            self.attacker.atk += self.attacker.fight_move[1]
            msg += f"{self.attacker.name} {self.attacker.fight_move[2]}"
        elif self.attacker.fight_move[0] == "zwiększ_def":
            self.attacker.deff += self.attacker.fight_move[1]
            msg += f"{self.attacker.name} {self.attacker.fight_move[2]}"
        elif self.attacker.fight_move[0] == "zmniejsz_enemy_def":
            self.attacker.enemy.deff -= self.attacker.fight_move[1]
            if self.attacker.enemy.deff < 0:
                self.attacker.enemy.deff = 0

            msg += f"{self.attacker.name} {self.attacker.fight_move[2]}"
        elif self.attacker.fight_move[0] == "zmniejsz_enemy_atk":
            self.attacker.enemy.atk -= self.attacker.fight_move[1]
            if self.attacker.enemy.atk < 0:
                self.attacker.enemy.atk = 0

            msg += f"{self.attacker.name} {self.attacker.fight_move[2]}"
        elif self.attacker.fight_move[0] == "leczenie":
            if self.attacker.hp + self.attacker.fight_move[1] > 100:
                self.attacker.fight_move[1] = 100 - self.attacker.hp
            self.attacker.hp += self.attacker.fight_move[1]
            msg += f"{self.attacker.name} {self.attacker.fight_move[2]}"


        self.player1.fight_move = None
        self.player2.fight_move = None

        if self.player1.hp <= 0 or self.player2.hp <= 0:
            winner = self.player1.name if self.player1.hp > 0 else self.player2.name
            text = f"🏆 {winner} wygrywa walkę!"
            await self.view.delete_buttons()
            await self.view.update_pkn(text, interaction, True)
            await self.view.update_player1_embed("zakończono grę")
            await self.view.update_player2_embed("zakończono grę")

            return

        await self.view.delete_buttons()
        await self.view.update_pkn(msg, interaction, False)
        await self.view.update_player1_embed("Oczekiwanie na następną turę...")
        await self.view.update_player2_embed("Oczekiwanie na następną turę...")
        return


class Fight_view:
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.clickedPKN = logic.clickedPKN
        self.clicked_fight = logic.clicked_fight
        self.players = logic.players
        self.player1 = logic.player1
        self.player2 = logic.player2

        self.pkn_message = None
        self.pkn_text = ["WALKA SIĘ ZACZYNA"]
        self.pkn_embed = discord.Embed(
            title="⚔️ WALKA",
            description=(
                f"## {self.player1.name} **VS** {self.player2.name}\n"
                f"**{self.pkn_text[0]}**\n\n"
            ),
            color=discord.Color.red()
        )
        self.pkn_view = discord.ui.View()

        self.player1_message = None
        self.player1_embed = discord.Embed(
            title=f"🗡️ {self.player1.name}",
            description="Oczekiwanie na walkę...",
            color=discord.Color.green()
        )
        hp_bars = int(self.player1.hp / 10)
        hp_field = "❤️" * hp_bars + "🖤" * (10 - hp_bars) + f" {self.player1.hp}/100"
        self.player1_embed.add_field(name="HP", value=hp_field, inline=False)
        self.player1_embed.add_field(name="⚔️ ATK", value=str(self.player1.atk), inline=True)
        self.player1_embed.add_field(name="🛡️ DEF", value=str(self.player1.deff), inline=True)
        self.player1_embed.add_field(name="🍀 LCK", value=str(self.player1.lck), inline=True)
        self.player1_embed.set_thumbnail(url=self.player1.image)
        self.player1_view = discord.ui.View()

        self.player2_message = None
        self.player2_embed = discord.Embed(
            title=f"🗡️ {self.player2.name}",
            description="Oczekiwanie na walkę...",
            color=discord.Color.green()
        )
        hp_bars = int(self.player2.hp / 10)
        hp_field = "❤️" * hp_bars + "🖤" * (10 - hp_bars) + f" {self.player2.hp}/100"
        self.player2_embed.add_field(name="HP", value=hp_field, inline=False)
        self.player2_embed.add_field(name="⚔️ ATK", value=str(self.player2.atk), inline=True)
        self.player2_embed.add_field(name="🛡️ DEF", value=str(self.player2.deff), inline=True)
        self.player2_embed.add_field(name="🍀 LCK", value=str(self.player2.lck), inline=True)
        self.player2_embed.set_thumbnail(url=self.player2.image)
        self.player2_view = discord.ui.View()

        for move, (label, style, cb_factory) in pkn_buttons.items():
            button = discord.ui.Button(label=label, style=style)
            async def callback(interaction, view=self, cb=cb_factory):
                await cb(view, interaction)
            button.callback = callback
            self.pkn_view.add_item(button)

    async def update_pkn(self, text, interaction, turn_off):
        if turn_off == True:
            for child in self.pkn_view.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True
        elif turn_off == False:
            for child in self.pkn_view.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = False
        self.pkn_text.append(text)
        if len(self.pkn_text) > 3:
            text_do_dodania = self.pkn_text[-3:]
        else:
            text_do_dodania = self.pkn_text
        self.pkn_embed.description = (
            f"## {self.player1.name} **VS** {self.player2.name}\n"
            + "\n".join(f"_{t}_" for t in text_do_dodania)
        )
        await self.pkn_message.edit(embed=self.pkn_embed, view=self.pkn_view)
        return



    async def update_player1_embed(self, text, interaction=0, role=0, opcje=[]):
        self.player1_embed.description = text
        self.player1_embed.clear_fields()
        hp_bars = int(self.player1.hp / 10)
        hp_field = "❤️" * hp_bars + "🖤" * (10 - hp_bars) + f" {self.player1.hp}/100"
        self.player1_embed.add_field(name="HP", value=hp_field, inline=False)
        self.player1_embed.add_field(name="⚔️ ATK", value=str(self.player1.atk), inline=True)
        self.player1_embed.add_field(name="🛡️ DEF", value=str(self.player1.deff), inline=True)
        self.player1_embed.add_field(name="🍀 LCK", value=str(self.player1.lck), inline=True)
        if len(opcje) != 0:
            for opcja in opcje:
                label, opis, style, cb_factory = opcja[1]
                unique_id = f"p1_{label}_{int(time.time())}"  # ← unikalny custom_id
                button = discord.ui.Button(label=label, style=style, custom_id=unique_id)
                async def callback(interaction, view=self, cb=cb_factory):
                    await cb(view, interaction)
                button.callback = callback
                self.player1_view.add_item(button)
        await self.player1_message.edit(embed=self.player1_embed, view=self.player1_view)
        return

    async def update_player2_embed(self, text , interaction=0, role=0, opcje=[]):
        self.player2_embed.description = text
        self.player2_embed.clear_fields()
        hp_bars = int(self.player2.hp / 10)
        hp_field = "❤️" * hp_bars + "🖤" * (10 - hp_bars) + f" {self.player2.hp}/100"
        self.player2_embed.add_field(name="HP", value=hp_field, inline=False)
        self.player2_embed.add_field(name="⚔️ ATK", value=str(self.player2.atk), inline=True)
        self.player2_embed.add_field(name="🛡️ DEF", value=str(self.player2.deff), inline=True)
        self.player2_embed.add_field(name="🍀 LCK", value=str(self.player2.lck), inline=True)
        if len(opcje) != 0:
            for opcja in opcje:
                label, opis, style, cb_factory = opcja[1]
                unique_id = f"p2_{label}_{int(time.time())}"  # ← unikalny custom_id
                button = discord.ui.Button(label=label, style=style, custom_id=unique_id)
                async def callback(interaction, view=self, cb=cb_factory):
                    await cb(view, interaction)
                button.callback = callback
                self.player2_view.add_item(button)
        await self.player2_message.edit(embed=self.player2_embed, view=self.player2_view)
        return

    async def delete_buttons(self):
        self.player1_view = discord.ui.View()
        self.player2_view = discord.ui.View()
        await self.player1_message.edit(view=self.player1_view)
        await self.player2_message.edit(view=self.player2_view)


@bot.command()
async def walcz(ctx, player1: discord.Member = None, player2: discord.Member = None):
    if player1 == None:
        await ctx.send("Format komendy /walcz to /walcz @ten_kogo_wyzywasz na walkę lub /walcz @walczący1 @walczący2")
        return
    if player2 == None:
        player2 = ctx.author
    if player1 == player2:
        await ctx.send("Nie można walczyć z samym sobą!")
    else:
        logic = Fight_logic(player1, player2)
        view = Fight_view(logic)
        logic.view = view

        pkn_msg = await ctx.send(embed=view.pkn_embed, view=view.pkn_view)
        player1_msg = await ctx.send(embed=view.player1_embed, view=view.player1_view)
        player2_msg = await ctx.send(embed=view.player2_embed, view=view.player2_view)

        view.pkn_message = pkn_msg
        view.player1_message = player1_msg
        view.player2_message = player2_msg

bot.run(TOKEN)



        


   





    

