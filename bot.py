# Imports
from random import randint
import json
import discord
import re # Needed for propper regex

# Variables
data = {}
with open("token.txt") as token_file:
	DISCORD_TOKEN = token_file.read()


# Definitions
class MyClient(discord.Client):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_ready(self):

		# Maintenance problem with translation between JSON string-keys and Python int-keys below
		try:
			if self.guilds != []:
				print(self.user, "is connected to the following guild:")  # Event log
				with open("data.json") as data_file:
					for guild in self.guilds:
						print(guild.name, "(id: " + str(guild.id) + ")")  # Event log
						guild_data = json.load(data_file)["servers"][str(guild.id)]
						print(guild_data)

						# Make the roles integer-indexed
						roles = {}
						for role in guild_data["roles"]:
							roles[int(role)] = guild_data["roles"][role]

						data[guild.id] = guild_data
						# Replace string-indexed roles with integer-indexed roles
						data[guild.id]["roles"] = roles
			print('------')
			print(data)
		except json.decoder.JSONDecodeError:
			pass

	async def on_guild_join(self, guild):
		print(self.user, "has joined the guild: " + guild.name + " with id:", guild.id)  # Event log
		# Read the data from the file
		with open("data.json") as data_file:
			data = json.load(data_file)
		servers_data = data["servers"]
		print(servers_data)

		# Checks if the server has already been joined in the past
		try:
			if servers_data[str(guild.id)] != None:
				print("Data for " + guild.name + " already stored.")
		except KeyError:
			print(guild.name + " identified as a new server. First time setup starting.")

			# Create the data for the new server
			new_guild = {"rules":
						{
						"title": "Rules for "+guild.name,
						"description": "[Description]",
						"thumbnail link": "none",
						"list": ["No low quality porn"]
						},
						"roles message id":"none",
						"roles":{}
			}
			servers_data.update({str(guild.id):new_guild})

			data["servers"] = servers_data
			# Write the updated data to the file
			with open("data.json", "w") as data_file:
				json.dump(data, data_file, indent=4)

		#await guild.channels[0].send("Please setup the rules and roles for this bot")

	async def on_message(self, message):

		# Don't respond to yourself
		if message.author.id == self.user.id:
			return

		# Set message origin's guild
		guild = self.get_guild(message.guild.id)

		# Rules
		if message.content == "!rules":
			print("`!rules` called by", message.author)  # Event log
			embed_rules = discord.Embed(title=data[guild.id]["rules"]["title"],
										description=data[guild.id]["rules"]["description"], color=0x4f7bc5)
			embed_rules.set_author(name=guild.name, icon_url=guild.icon_url)
			embed_rules.set_thumbnail(url=data[guild.id]["rules"]["thumbnail link"])
			embed_rules.add_field(name="Server rules", value="\n".join(data[guild.id]["rules"]["list"]), inline=False)
			await message.channel.send(embed=embed_rules)

		# Roles
		if message.content == "!roles":
			print("`!roles` called by", message.author)  # Event log
			embed_roles = discord.Embed(title="Role selection",
										description="React to get a role, unreact to remove it.", color=0x4f7bc5)
			value = ""
			for role in data[message.guild.id]["roles"]:
				value += data[message.guild.id]["roles"][role]["emoji"] + " " + data[message.guild.id]["roles"][role][
					"name"] + "\n"
			embed_roles.add_field(name="[Games]", value=value[:-2], inline=False)
			roles_message = await message.channel.send(embed=embed_roles)

			# Add emojis to roles message
			for role in data[message.guild.id]["roles"]:
				await roles_message.add_reaction(data[message.guild.id]["roles"][role]["emoji"])

		# Set Rules
		if message.content.startswith("!set rules"):
			parameter = message.content[len("!set rules "):] # Sets parameter to everything after the command
			parameters = parameter.split(",") # Splits parameter string into a list
			title = "Rules for " + guild.name
			description = "[Description]"
			thumbnail = "none"
			rules = ["No low quality porn"]
			for param in parameters:
				if param.startswith("title="):
					title = param[len("title="):]
				elif param.startswith("description="):
					description = param[len("description="):]
				elif param.startswith("thumbnail="):
					thumbnail = param[len("thumbnail="):]
				elif param.startswith("rules="):
					rules = re.split("\.\s|\.",param[len("rules="):]) # Splits the rules after every full stop or, preferably, a full stop followed by a space

			# Read the data from the file
			with open("data.json") as data_file:
				data = json.load(data_file)
			rules_data = data["servers"][str(message.guild.id)]["rules"]
			print(rules_data)

			# Creates new data for server
			new_rules = {
					"title": title,
					"description": description,
					"thumbnail link": thumbnail,
					"list": rules
					}
			print("Old rules: "+str(rules_data))
			print("New rules: "+str(new_rules))
			rules_data=new_rules

			data["servers"][str(message.guild.id)]["rules"] = rules_data
			# Write the updated data to the file
			with open("data.json", "w") as data_file:
				json.dump(data, data_file, indent=4)

		# Core functionality (do not alter)
		if message.author.id == 258284765776576512:
			print("Arun sighted. Locking on.")  # Event log
			if randint(1, 10) == 1:
				await message.channel.send("shut up arun")
				print("Doggie down.")  # Event log
			else:
				print("Mission failed, RTB.")  # Event log

		# Important saftey reminder
		if "gameboy" in message.content.lower():
			print("`gameboy` mentioned by", message.author)  # Event log
			await message.channel.send("Gameboys are worthless (apart from micro. micro is cool)")

		# Raspberry Racers functionality. Needs fixing
		if "raspberries" in message.content or "raspberry" in message.content:
			print("`raspberry racers` mentioned by", message.author)  # Event log
			await message.channel.send(
				"The Raspberry Racers are a team which debuted in the 2018 Winter Marble League. Their 2018 season was seen as the second-best rookie team of the year, behind only the Hazers. In the 2018 off-season, they won the A-Maze-ing Marble Race, making them one of the potential title contenders for the Marble League. They eventually did go on to win Marble League 2019.")

		if message.content == "!token":
			print("`!token` called by", message.author)  # Event log
			await message.channel.send("IdrOppED ThE TokEN gUYS!!!!")

		# Bot kill command
		if message.content.startswith("!kill"):
			print("`!kill` called by", message.author)  # Event log
			await message.channel.send(
				"https://cdn.discordapp.com/attachments/832293063803142235/832340900587110450/dogdeadinnit.mp3")

			await client.close()
			exit()  # This isn't a good heuristic. Find discord.py way of getting this done.

	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		"""Gives a role based on a reaction emoji."""

		# Make sure that the message the user is reacting to is the one we care about.
		if payload.message_id != data[payload.guild_id]["roles message id"]:
			return

		# Check if we're still in the guild and it's cached.
		guild = self.get_guild(payload.guild_id)  # DISTINCTION BEWEEN THIS AND payload.guild_id ABOVE? AS BELOW
		if guild is None:
			return

		# If the emoji isn't the one we care about then exit as well.
		role_id = -1
		for id_counter in data[guild.id]["roles"]:
			if data[guild.id]["roles"][id_counter]["emoji"] == str(payload.emoji):
				role_id = id_counter
		if role_id == -1:
			return

		# Make sure the role still exists and is valid.
		role = guild.get_role(role_id)
		if role is None:
			return

		# Finally, add the role.
		try:
			await payload.member.add_roles(role)
			print("Role `" + role.name + "` added to", payload.member.name)  # Event log

		# If we want to do something in case of errors we'd do it here.
		except discord.HTTPException:
			pass

	async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
		"""Removes a role based on a reaction emoji."""

		# Make sure that the message the user is reacting to is the one we care about.
		if payload.message_id != data[payload.guild_id]["roles message id"]:
			return

		# Check if we're still in the guild and it's cached.
		guild = self.get_guild(payload.guild_id)  # DISTINCTION BEWEEN THIS AND payload.guild_id ABOVE? AS ABOVE
		if guild is None:
			return

		# If the emoji isn't the one we care about then exit as well.
		role_id = -1
		for id_counter in data[guild.id]["roles"]:
			if data[guild.id]["roles"][id_counter]["emoji"] == str(payload.emoji):  # TYPE? AS ABOVE
				role_id = id_counter
				break
		if role_id == -1:
			return

		# Make sure the role still exists and is valid.
		role = guild.get_role(role_id)
		if role is None:
			return

		# The payload for `on_raw_reaction_remove` does not provide `.member`
		# so we must get the member ourselves from the payload's `.user_id`.

		# Make sure the member still exists and is valid.
		member = guild.get_member(payload.user_id)
		if member is None:
			return

		# Finally, remove the role.
		try:
			await member.remove_roles(role)
			print("Role `" + role.name + "` removed from", member.name)  # Event log

		# If we want to do something in case of errors we'd do it here.
		except discord.HTTPException:
			pass


# Main body
intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
