import nextcord
from nextcord.ext import commands
import requests
import csv

client = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())

@client.event
async def on_ready():
    print("Bot is ready")

coverage_options = {
    "Normal": ["Fighting", "Psychic", "Dark"],
    "Water": ["Ice", "Steel", "Psychic"],
    "Poison": ["Bug", "Grass", "Electric"],
    "Psychic": ["Fairy", "Ghost", "Water"],
    "Fighting": ["Electric", "Ice", "Fire"],
    "Flying": ["Steel", "Dragon", "Fighting"],
    "Grass": ["Ground", "Poison", "Rock"],
    "Ground": ["Rock", "Grass", "Dark"],
    "Bug": ["Dark", "Poison", "Ground"],
    "Rock": ["Ground", "Fire", "Electric"],
    "Dark": ["Rock", "Electric", "Poison"],
    "Fairy": ["Psychic", "Water", "Grass"],
    "Steel": ["Ice", "Ground", "Ghost"],
    "Ghost": ["Poison", "Flying", "Bug"],
    "Ice": ["Water", "Fairy", "Steel"],
    "Dragon": ["Fire", "Grass", "Psychic"],
    "Electric": ["Fairy", "Grass", "Dragon"],
    "Fire": ["Dragon", "Electric", "Fighting"]
}

with open("Pokedex.txt", "r") as file:
    options = file.readlines()
    file.close()

with open("Type_Data.csv", encoding="utf8") as f:
    cr = csv.reader(f)
    next(cr)
    Type_Data = {}
    headers = ["", "Coverages", "Color", "Resistance", "Weakness", "Immunity"]
    for row in cr:
        d = {}
        for value in range(len(row)):
            if value == 0:
                continue
            if value == 2:
                d[headers[value]] = row[value]
            else:
                d[headers[value]] = eval(row[value])
        Type_Data[row[0]] = d

pokemon_options = {
    option.strip(): option.strip().lower()
    for option in options
}

@client.slash_command(name="pokemon", description="Get info on a Pokemon")
async def pokemon(interaction: nextcord.Interaction,
                  pokemon: str = nextcord.SlashOption(
                      name="pokemon",
                      description="Choose a Pokémon",
                      autocomplete=True,
                  )):
    try:
        url = "https://pokeapi.co/api/v2/pokemon/" + pokemon.lower()
        data = requests.get(url).json()
        name = data['name'].title()
        image_url = data['sprites']['front_default']
        weight_int = str(data["weight"])
        weight = weight_int[0:-1:] + "." + weight_int[-1] + " kg"
        base_stats = {}
        bst_total = 0
        for stat in data["stats"]:
            base_stats[stat["stat"]["name"]] = stat["base_stat"]
            bst_total += stat["base_stat"]
        types = [
            type_data["type"]["name"].capitalize()
            for type_data in data["types"]
        ]
        coverages = []
        imm, res, weak = [], [], []
        for type in types:
            imm.extend(Type_Data[type]["Immunity"])
            res.extend(Type_Data[type]["Resistance"])
            weak.extend(Type_Data[type]["Weakness"])
            for coverage in coverage_options[type]:
                if coverage not in coverages:
                    coverages.append(coverage)
        res_ = []
        for r in res:
            if r not in res_ and r not in weak and r not in imm:
                res_.append(r)
        weak_ = []
        for w in weak:
            if w not in res and w not in weak_ and w not in imm:
                weak_.append(w)
        embed = nextcord.Embed(title=f"{name} Info",
                               color=nextcord.Colour.blue())
        embed.set_thumbnail(url=image_url)
        embed.add_field(name="Type", value=f"{types}", inline=False)
        basestats = {
            "Hp": base_stats['hp'],
            "Atk": base_stats['attack'],
            "Def": base_stats['defense'],
            "SpAtk": base_stats['special-attack'],
            "SpDef": base_stats['special-defense'],
            "Spe": base_stats['speed']
        }
        formatted_stats = "\n".join(
            [f"{key}: {value}" for key, value in basestats.items()])
        embed.add_field(name=f"Base Stats ({bst_total})",
                        value=f"{formatted_stats}",
                        inline=False)
        embed.add_field(name="Weight", value=f"{weight}", inline=False)
        embed.add_field(name="Coverage Options",
                        value=f"{coverages}",
                        inline=False)
        embed.add_field(name="Weaknesses", value=f"{weak_}", inline=False)
        embed.add_field(name="Immunities", value=f"{imm}", inline=False)
        embed.add_field(name="Resistances", value=f"{res_}", inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Invalid Pokemon")

@pokemon.on_autocomplete("pokemon")
async def pokemon_autocomplete(interaction: nextcord.Interaction,
                               current: str):
    filtered_options = [
        name for name, value in pokemon_options.items()
        if value.startswith(current.lower())
    ]
    await interaction.response.send_autocomplete(filtered_options[:25])

client.run("")
