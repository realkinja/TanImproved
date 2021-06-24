import discord
from datetime import datetime
from pytz import timezone
import badwordlist
from discord.ext import commands, tasks
from itertools import cycle
from mcstatus import MinecraftBedrockServer
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)
time_window_milliseconds = 5000
max_msg_per_window = 6
author_msg_times = {}
client.remove_command('help')
status = cycle(['The Bridge', 'Skyblock', "OP Factions"])
#The below code stores the token, saves time of having to scroll all the way down.
token = "Your token"


@tasks.loop(seconds=4)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status) + " at The Tancraft Network, watching. [!]"))


@client.event
async def on_ready():
    global message_id
    change_status.start()
    print("The Tancraft bot is ready steady and online.")
    guild = client.get_guild(844231449014960160)


@client.listen()
async def on_message(ctx):
    global author_msg_counts
    memberRole = discord.utils.get(ctx.guild.roles, name="Member")
    guild = ctx.guild
    mutedrole = discord.utils.get(guild.roles, name="Muted")
    author_id = ctx.author.id
    curr_time = datetime.now().timestamp() * 1000
    if not author_msg_times.get(author_id, False):
        author_msg_times[author_id] = []
    author_msg_times[author_id].append(curr_time)
    expr_time = curr_time - time_window_milliseconds
    expired_msgs = [
        msg_time for msg_time in author_msg_times[author_id]
        if msg_time < expr_time
    ]
    for msg_time in expired_msgs:
        author_msg_times[author_id].remove(msg_time)
    if len(author_msg_times[author_id]) > max_msg_per_window:
        if ctx.author.bot:
            pass
        else:
            await ctx.author.remove_roles(memberRole)
            await ctx.author.add_roles(mutedrole)
            await ctx.channel.send(f"Muted {ctx.author.mention} for spamming.")


@client.listen()
async def on_message(message: discord.Message):
    if message.author.permissions_in(message.channel).manage_messages:
        return
    elif message.author.bot:
        return
    elif "https://discord.gg/" in message.content.lower():
        await message.delete()
        await message.author.send(f"You got kicked from {message.guild.name} for advertising.")
        await message.author.kick(reason="Advertising")
        await message.channel.send(f"advertising is not allowed, {message.author.mention} has been kicked.")


@client.listen()
async def on_message(message: discord.Message):
    lists = [".", "/", "!", "s!", "r!"]
    if message.channel.id != 850027624361230336:
        return
    elif message.author.bot:
        return
    elif message.content.lower().startswith(tuple(lists)):
        return
    else:
        await message.delete()
        await message.channel.send("Only commands are allowed in this channel.", delete_after=3)


@client.listen()
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    elif "@everyone" in message.content.lower() or "@here" in message.content.lower():
        if message.author.permissions_in(message.channel).administrator:
            return
        else:
            await message.delete()
            await message.channel.send(f"{message.author.mention} you are not allowed to ping everyone.",delete_after=5)
            return
    else:
        badword = True
        string = message.content.lower()
        for word in badwordlist.arrBad:
            if word in string:
                badword = False
                string=string.replace(word, ("-"*len(word)))
        if badword == False:
            await message.delete()
            await message.channel.send(f"Watch your mouth {message.author.mention}!, {message.author.mention} tried to say {string}")
        else :
            return
@client.listen()
async def on_message(message: discord.Message):
    if message.channel.id!=852646981759270972:
        return
    elif message.author.bot:
        return
    else:
        await message.delete()
@client.event

async def on_member_join(member):
    welcome_channel = member.guild.get_channel(857336332945981440)
    await welcome_channel.send(f'Welcome to {member.guild.name}, {member.mention}! :partying_face:')

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx,arg):
    await ctx.channel.purge(limit=int(arg))

# A working ban command (gamer)
@client.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason = None):
    if member == None or member == ctx.message.author:
        await ctx.channel.send("You cannot ban yourself.")
        return
    message = f"You have been banned from {ctx.guild.name} for {reason}."
    await member.send(message)
    await member.ban(reason = reason)
    await ctx.send(f"{member.mention} was struck by the ban hammer for {reason}.")


# The broken shitty unban command.
@client.command()
@commands.has_permissions(administrator = True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

@client.command()
async def whois(ctx, member: discord.Member = None):
    if not member:
        member = ctx.message.author
    roles = [role for role in member.roles]
    embed = discord.Embed(colour=discord.Colour.green(), timestamp=ctx.message.created_at,
                          title=f"User Info of {member} in {message.g}")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}")

    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Display Name:", value=member.display_name)

    embed.add_field(name="Created Account On:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

    embed.add_field(name="Roles:", value="\n".join([role.mention for role in roles][1:]))
    embed.add_field(name="Highest Role:", value=member.top_role.mention)
    await ctx.send(embed=embed)

# A working kick command
@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member == None or member == ctx.message.author:
        await ctx.channel.send("You cannot kick yourself.")
        return
    message = f"You have been kicked from {ctx.guild.name} for {reason}."
    await member.send(message)
    await member.kick(reason=reason)
    await ctx.send(f":boot: {member} was kicked out the door for {reason}!")


@client.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")
    memberRole=discord.utils.get(guild.roles, name="Member")
    await member.remove_roles(memberRole, reason=reason)
    await member.add_roles(mutedRole, reason=reason)
    await ctx.send(f"Muted {member.mention}.")


@client.command()
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member,*,reason=None):
    memberRole = discord.utils.get(ctx.guild.roles, name="Member")
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(mutedRole)
    await member.add_roles(memberRole, reason=reason)
    await ctx.send(f"Unmuted {member.mention}")


@client.command()
async def online(ctx,arg):
    try:
        server = MinecraftBedrockServer.lookup(arg)
        online=server.status()
        online_embed = discord.Embed(
            colour=discord.Colour.green()
        )
        online_embed.set_author(name=f"Server Is Online, running on {online.map}\nThe server's description is {online.motd}")
        online_embed.add_field(name="Server Latency",
                        value=f"{round(online.latency*100)}ms")
        online_embed.add_field(name="Server players",value=f"{online.players_online}/{online.players_max}")
        await ctx.send(embed=online_embed)
    except:
        await ctx.send("The server you chose is either offline, doesn't exist or you didn't enable 3rd party info fetcher.")


@client.command()
async def stats(ctx):
    embed = discord.Embed(title="Server information",colour=discord.Colour.green(),timestamp=ctx.message.created_at)

    embed.set_thumbnail(url=ctx.guild.icon_url)
    true_member_count=[m for m in ctx.guild.members if not m.bot]

    statuses = [len(list(filter(lambda m: str(m.status) == "online", true_member_count))),
                len(list(filter(lambda m: str(m.status) == "idle", true_member_count))),
                len(list(filter(lambda m: str(m.status) == "dnd", true_member_count))),
                len(list(filter(lambda m: str(m.status) == "offline", true_member_count)))]
    fields = [("ID", ctx.guild.id, True),
			 ("Owner", ctx.guild.owner, True),
			 ("Region", "Canada", True),
		     ("Created at", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
			 ("TotalMembers", len(ctx.guild.members), True),
			 ("Members", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
			 ("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
			 ("Banned members", len(await ctx.guild.bans()), True),
			 ("Statuses", f"🟢 {statuses[0]} 🟠 {statuses[1]}\n 🔴 {statuses[2]} ⚪ {statuses[3]}", True),
			 ("Text channels", len(ctx.guild.text_channels), True),
			 ("Voice channels", len(ctx.guild.voice_channels), True),
			 ("Categories", len(ctx.guild.categories), True),
			 ("Roles", len(ctx.guild.roles), True),
			 ("Invites", len(await ctx.guild.invites()), True),
			("\u200b", "\u200b", True)]
    for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
            embed.set_footer(text=f"Requested by {ctx.author}")

    await ctx.send(embed=embed)

@client.command()
async def about(ctx):
    server_created=ctx.guild.created_at.strftime("%d/%m/%Y")
    embed = discord.Embed(title="About TancraftPE",
                          colour=discord.Colour.green(),
                          description=f"TancraftPE is a Minecraft bedrock editon network created at {server_created}",
                          timestamp=ctx.message.created_at)
    embed.add_field(name="Gamemodes:", value="Skyblock, Bedwars, Skywars, Spleef, Sumo",
                    inline=False)
    embed.add_field(name="Shop:", value="Buy our server ranks at the [TancraftPE Store](https://tancraft.tebex.io/)", inline=False)
    embed.add_field(name="Server IP:", value="IP: Not released yet \nPort: 19132", inline=False)
    embed.add_field(name="Founders:", value="These are the people that helped to create TancraftPE", inline=False)
    embed.add_field(name="FoxyInABoxy#3570", value="Owner/Server developer", inline=True)
    embed.add_field(name="MetallicWeb7080#6454", value="Owner/Discord developer", inline=True)
    embed.add_field(name="DcRexMC#2969", value="Owner/Builder", inline=True)
    embed.add_field(name="kinja#2137", value="[Improved Bot Developer](https://beacons.page/yeezys)", inline=True)
    embed.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=embed)

@client.command(pass_contect=True)
async def help(ctx):

    embed = discord.Embed(
        title="The Tancraft Network Bot:\nIncludes",
        colour=discord.Colour.green()
    )
    embed.set_author(name=ctx.message.author,icon_url= ctx.message.author.avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/850019796014858280/850433721920127016/MyLogo20201220023005.png")
    embed.add_field(name="Information Commands:",
                    value="Everyone can use Them", inline=False)
    embed.add_field(name="```!about```",
                    value="Server Information", inline=True)
    embed.add_field(name="```!online```",
                    value="Check if a server online and get info.", inline=True)
    embed.add_field(name="```!stats```",
                    value="Check out statistics of this discord server!",
                    inline=True)
    embed.add_field(name="```!whois```",
                    value="!whois for your own info \n!whois (@user) \nTo get user info in {message.guild.name} \n", inline=True)
    embed.add_field(name="Server Moderation:",
                    value="Only {message.guild.name} staff team members can use these commands.",
                    inline=False)
    embed.add_field(name="```!clear```",
                    value="Use !clear (amount)", inline=True)
    embed.add_field(name="```!ban and !unban```",
                    value="!ban @user\n!unban(user_name)\neg:MetallicWeb7080#6454 ", inline=True)
    embed.add_field(name="```!kick```",
                    value="!kick @user ", inline=True)
    embed.add_field(name="```!mute and !unmute```",
                    value="!mute @user\n!unmute @user ", inline=True)
    embed.set_footer(text="Made by MetallicWeb7080 • Improved by Kinja")
    await ctx.send( embed=embed)

@client.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Needs an argument")
    elif isinstance(error,commands.CommandInvokeError):
        await ctx.send("Error:404 Code Is Bugged until further fix")
        print(error)

client.run(token)
