import os
import re
import discord
from discord.ext import commands
from dotenv import load_dotenv
from typing import List

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyClient(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.emoji_pattern = re.compile("["
                            u"\U0001F600-\U0001F64F"  # emoticons
                            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                            u"\U0001F680-\U0001F6FF"  # transport & map symbols
                            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            u"\U00002500-\U00002BEF"  # chinese characters
                            u"\U00002702-\U000027B0"
                            u"\U000024C2-\U0001F251"
                            u"\U0001f926-\U0001f937"
                            u"\U00010000-\U0010ffff"
                            u"\u2600-\u26FF"         # Miscellaneous Symbols
                            u"\u2700-\u27BF"         # Dingbats
                            u"\u2B50-\u2BFF"         # Miscellaneous Symbols and Arrows
                            u"\u23E9-\u23FA"         # Additional transport & map symbols
                            u"\u23F0-\u23FF"         # Clock face symbols (including stopwatch ⏱)
                            u"\uFE0F"                # Variation Selectors
                            u"\u3030"                # Wavy Dash
                            "]+", flags=re.UNICODE)

    def _remove_emojis(self, str):
        return self.emoji_pattern.sub(r'', str)
    
    def _get_emojis(self, str):
        return self.emoji_pattern.findall(str)
    
    async def update_member(self, member: discord.Member, **kwargs):
        tabs = kwargs.get("tabs", "")
        print(f'{tabs}Updating {member.display_name}')
        new_nickname = self._remove_emojis(member.display_name).strip() + ' '
        
        roles = member.roles
        roles.reverse()
        
        for role in roles:
            emojis = self._get_emojis(role.name)
            new_nickname += ''.join(emojis)
            
        new_nickname = new_nickname.strip()
        
        if new_nickname != member.display_name:
            try:
                await member.edit(nick=new_nickname)
                print(f"{tabs}    Name updated to {new_nickname}")
            except Exception as e:
                print(f"{tabs}    ERROR: Couldn't change nickname for {member.name}: {e}")
        else:
            print(f"{tabs}    Member's nickname is already up to date")

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        await self.update_member(after)

    async def update_all(self, ctx):
        print('Running update on all members:')
        member_list = ctx.guild.members
        for member in member_list:
            await self.update_member(member, tabs='    ')


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
    
bot = MyClient(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print("Bot is up and ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s): {synced}")
    except Exception as e:
        print(e)

@bot.tree.command(name="users", description="It is my_command")
async def test_command(interaction: discord.Interaction, role: discord.Role, print_for_everyone: bool=False):
    members: List[discord.Member] = role.members
    num_members = len(members)
    message = ""
    
    if num_members == 0:
        message = f"There are no members with role {role.mention}."
    elif num_members == 1:
        message = f"{members[0].mention} is the only member of {role.mention}."
    else:
        members.sort(key=lambda a: a.nick or a.name)
        message = f"Here are all {len(members)} users with role {role.mention}:"
        for member in members:
            message += f"\n- {member.mention}"
    await interaction.response.send_message(message, ephemeral=(not print_for_everyone))

@bot.command(name="update-all", description="Update all user's rolemojis (WARNING: This will remove all existing emojis from all user's names).")
async def update_all(ctx: commands.context.Context):
    print("Running command {}", ctx.bot)
    await ctx.bot.update_all(ctx)

bot.run(TOKEN)