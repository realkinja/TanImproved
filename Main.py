

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
status = cycle(['Thebridge', 'skyblock', "OP Factions"])


@tasks.loop(seconds=4)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status) + " at TancraftPE,watching [!]"))


@client.event
async def on_ready():
    global message_id
    change_status.start()
    print("i am ready daddy metallic")
    guild = client.get_guild(844231449014960160)
    channel = discord.utils.get(guild.text_channels, name="👊〢bumping")
    bump_role = discord.utils.get(guild.roles, name="Bumpers")
    message = await channel.send(f"Disboard is back!\nDo `!d bump` to get the bump king role\n{bump_role.mention}", allowed_mentions=discord.AllowedMentions.all())
    message_id=message.id


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
            await ctx.channel.send(f"Muted {ctx.author.mention} for spamming")


@client.listen()
async def on_message(message: discord.Message):
    if message.author.permissions_in(message.channel).manage_messages:
        return
    elif message.author.bot:
        return
    elif "https://discord.gg/" in message.content.lower():
        await message.delete()
        await message.author.send(f"You were muted in TancraftPE for advertising")
        await message.author.kick(reason="Advertising")
        await message.channel.send(f"advertising is not allowed,{message.author.mention} is kicked")


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
        await message.channel.send("Only commands allowed in this channel", delete_after=3)


@client.listen()
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    elif "@everyone" in message.content.lower() or "@here" in message.content.lower():
        if message.author.permissions_in(message.channel).administrator:
            return
        else:
            await message.delete()
            await message.channel.send(f"{message.author.mention}you are not allowed to ping everyone",delete_after=5)
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
            await message.channel.send(f"{message.author.mention} tried to say {string}")
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
async def on_raw_reaction_add(reaction):
    guild = client.get_guild(844231449014960160)
    channel = guild.get_channel(reaction.channel_id)
    role=discord.utils.get(guild.roles, name="Bumpers")
    messages = await channel.history(oldest_first=True, limit=1).flatten()
    if reaction.emoji.name != "🔔":
        return
    if reaction.message_id != messages[0].id:
        print("not same message")
        return
    member = guild.get_member(reaction.user_id)
    if member.bot:
        return
    if role not in member.roles:
        await member.add_roles(role)
        await channel.send(f"{member.mention} you will be tagged by bump reminders",delete_after=10)
@client.event
async def on_raw_reaction_remove(reaction):
    guild =client.get_guild(844231449014960160)
    channel = guild.get_channel(reaction.channel_id)
    role=discord.utils.get(guild.roles, name="Bumpers")
    messages = await channel.history(oldest_first=True, limit=1).flatten()
    if reaction.emoji.name != "🔔":
        return
    if reaction.message_id != messages[0].id:
        print("not same message")
        return
    member = guild.get_member(reaction.user_id)
    if member.bot:
        return
    if role in member.roles:
        await member.remove_roles(role)
        await channel.send(f"{member.mention} you will no longer be tagged by bump reminders",delete_after=10)
@client.event
async def on_member_join(member):
    welcome_channel = member.guild.get_channel(850022996541702144)
    await welcome_channel.send(f'Welcome to TanraftPE Network,{member.mention} :partying_face:')

@client.command()
async def clear(ctx,arg):
    await ctx.channel.purge(limit=int(arg))

@client.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason = None):
    await member.ban(reason = reason)
    await ctx.send(f"{member} is banned")


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
bump_king_id=0
message_id=0
@client.command(name="d", aliases=["D"])
async def bump_reminder(ctx: discord.ext.commands.Context, action: str):
    global bump_king_id,message_id
    disboard = ctx.guild.get_member(302050872383242240)
    bump_king_role = discord.utils.get(ctx.guild.roles,name="BumpKing")
    if ctx.channel.id != 852646981759270972:
        await ctx.send("Use this command at the bump channel")
        return
    if not action.casefold() == "bump":
        return
    if not disboard.status == discord.Status.online:
        await ctx.send(embed=(discord.Embed(color=discord.Colour.red,
                                            description=(f"{ctx.author.mention} Whoa {disboard.mention} appears to be offline right now!\nContack MetallicWeb7080 to report that")
                                            )
                              ),
                       delete_after=20)
        return
    if lock_disboard_Out_for_two_hours.is_running():
        time_zone=timezone('US/Eastern')
        next_bump=lock_disboard_Out_for_two_hours.next_iteration.astimezone(time_zone).replace(microsecond=0)
        now = datetime.now().astimezone(time_zone).replace(microsecond=0)
        duration = next_bump-now
        print(duration)

        await ctx.send(
                    embed=discord.Embed(
                        color=0xe5e740,
                        description=f"{ctx.author.mention} disboard will be back in {duration} ",
                        title="Please Wait",
                    ),delete_after=20)
        return
    else :
        embed = discord.Embed(title=f"Thanks for bumping!!!", description=f"{ctx.author.mention}You are now the new bump king\nDisboard will be back in two hours",colour=0x0df214)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/711749954837807135.png?v=1")
        bump_king_id=ctx.author.id
        await ctx.author.add_roles(bump_king_role)
        await ctx.send(embed=embed,delete_after=7200)
        await ctx.channel.set_permissions(disboard, view_channel =False)
        if message_id == 0:
            pass
        else:
            await client.http.delete_message(ctx.channel.id, message_id)
        lock_disboard_Out_for_two_hours.start()
        return

@tasks.loop(hours=2)
async def lock_disboard_Out_for_two_hours():
    global bump_king_id,message_id
    if lock_disboard_Out_for_two_hours.current_loop == 0:
        return None
    guild =client.get_guild(844231449014960160)
    disboard=guild.get_member(302050872383242240)
    bump_role=discord.utils.get(guild.roles, name="Bumpers")
    bump_king = discord.utils.get(guild.roles, name="BumpKing")
    channel= discord.utils.get(guild.text_channels, name="👊〢bumping")
    remove_bump_king=guild.get_member(bump_king_id)
    await remove_bump_king.remove_roles(bump_king)
    message = await channel.send(f"Disboard is back!\nDo `!d bump` to get the bump king role\n{bump_role.mention}",
                                 allowed_mentions=discord.AllowedMentions.all())
    message_id = message.id
    await channel.set_permissions(disboard, view_channel=True, send_messages=False)
    lock_disboard_Out_for_two_hours.cancel()


@client.command()
async def whois(ctx, member: discord.Member = None):
    if not member:
        member = ctx.message.author
    roles = [role for role in member.roles]
    embed = discord.Embed(colour=discord.Colour.green(), timestamp=ctx.message.created_at,
                          title=f"User Info of {member} in TancraftPE")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}")

    embed.add_field(name="ID:", value=member.id)
    embed.add_field(name="Display Name:", value=member.display_name)

    embed.add_field(name="Created Account On:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

    embed.add_field(name="Roles:", value="\n".join([role.mention for role in roles][1:]))
    embed.add_field(name="Highest Role:", value=member.top_role.mention)
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member} was kicked!")


@client.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")
    memberRole=discord.utils.get(guild.roles, name="Member")
    await member.remove_roles(memberRole, reason=reason)
    await member.add_roles(mutedRole, reason=reason)
    await ctx.send(f"Muted {member.mention} for reason {reason}")


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
        online_embed.set_author(name=f"Server Is Online,runing on {online.map}\nThe server's description is {online.motd}")
        online_embed.add_field(name="Server Latency",
                        value=f"{round(online.latency*100)}ms")
        online_embed.add_field(name="Server players",value=f"{online.players_online}/{online.players_max}")
        await ctx.send(embed=online_embed)
    except:
        await ctx.send("The server you chose is either not online , don't exist or didn't enable 3rd party info fetcher")


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
                          description=f"TancraftPE is a mincraft bedrock network created at {server_created}",
                          timestamp=ctx.message.created_at)
    embed.add_field(name="Gamemodes:", value="skyblock, bedwars, skywars, spleef, sumo",
                    inline=False)
    embed.add_field(name="Shop:", value="Buy our server ranks at [TancraftPE Store](https://tancraft.tebex.io/)", inline=False)
    embed.add_field(name="Server IP:", value="IP:Not released \nPort:19132", inline=False)
    embed.add_field(name="Founders:", value="These are the people that helped to create TancraftPE", inline=False)
    embed.add_field(name="FoxyInABoxy#3570", value="owner/server developer", inline=True)
    embed.add_field(name="MetallicWeb7080#6454", value="owner/discord developer", inline=True)
    embed.add_field(name="DcRexMC#2969", value="owner/builder", inline=True)
    embed.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=embed)

@client.command(pass_contect=True)
async def help(ctx):

    embed = discord.Embed(
        title="TancraftPE Bot:\nIncludeds",
        colour=discord.Colour.green()
    )
    embed.set_author(name=ctx.message.author,icon_url= ctx.message.author.avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/850019796014858280/850433721920127016/MyLogo20201220023005.png")
    embed.add_field(name="Information Commands:",
                    value="Everyone can use Them", inline=False)
    embed.add_field(name="```!about```",
                    value="Server Information", inline=True)
    embed.add_field(name="```!online```",
                    value="check if server online and get info", inline=True)
    embed.add_field(name="```!stats```",
                    value="check out statistic of TancraftPE discord ",
                    inline=True)
    embed.add_field(name="```!whois```",
                    value="!whois for your own info \n!whois (@user) \nTo get user info in tancraft \n", inline=True)
    embed.add_field(name="Server Moderation:",
                    value="only TancraftPE staff team members can use these commands",
                    inline=False)
    embed.add_field(name="```!clear```",
                    value="use !clear(amount)", inline=True)
    embed.add_field(name="```!ban and !unban```",
                    value="!ban @user\n!unban(user_name)\neg:MetallicWeb7080#6454 ", inline=True)
    embed.add_field(name="```!kick```",
                    value="!kick @user ", inline=True)
    embed.add_field(name="```!mute and !unmute```",
                    value="!mute @user\n!unmute @user ", inline=True)
    embed.set_footer(text="Made by MetallicWeb7080")
    await ctx.send( embed=embed)

@client.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("don't have permission to use command")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("needs an argument")
    elif isinstance(error,commands.CommandInvokeError):
        await ctx.send("some code is bugged")
        print(error)

client.run("Token")