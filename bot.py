import os
import re
import discord
from discord.ext import commands
from dotenv import load_dotenv

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
    
    async def update_member(self, member: discord.Member):
        print(f'Updating {member.display_name}')
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
            except Exception as e:
                print(f"Couldn't change nickname for {member.name}: {e}")
        else:
            print("Member's nickname is already up to date")
    
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        await self.update_member(after)

    async def update_all(self, ctx):
        print('Running update on all members')
        member_list = ctx.guild.members
        for member in member_list:
            await self.update_member(member)
            

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
    
bot = MyClient(command_prefix='!', intents=intents)
bot.run(TOKEN)