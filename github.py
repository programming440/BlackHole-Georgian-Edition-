import discord
from discord.ext import commands
import cmath
import datetime
import requests

client = commands.Bot(command_prefix = "b.")


@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.online, activity = discord.Game("with b.help_me"))

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name = "general")
    embed = discord.Embed(description = f"გამარჯობა, {member.name}")
    embed.set_thumbnail(url = f"{member.avatar_url}")
    embed.set_author(name = f"{member.name}", icon_url = f"{member.avatar_url}")
    embed.set_footer(text = f"{member.guild}", icon_url = f"{member.guild.icon_url}")
    embed.timestamp = datetime.datetime.utcnow()
    embed.add_field(name = "User ID :", value = member.id)
    embed.add_field(name = "User Name :", value = member.display_name)
    await channel.send(embed = embed)

@client.command()
async def serverinfo(ctx):
    role_count = len(ctx.guild.roles)
    channel_count = len([x for x in ctx.guild.channels if isinstance(x, discord.channel.TextChannel)])
    embed = discord.Embed(colour = discord.Colour.darker_grey(), timestamp=ctx.message.created_at)
    embed.add_field(name='სახელი (ID)', value = f"{ctx.guild.name} ({ctx.guild.id})")
    embed.add_field(name='მფლობელი', value = ctx.guild.owner)
    embed.add_field(name='ჯგუფის წევრები', value = ctx.guild.member_count)
    embed.add_field(name='რეგიონი', value = ctx.guild.region)
    embed.add_field(name='როლები', value=str(role_count))
    embed.add_field(name='Text Channel-ები  ', value=str(channel_count))
    embed.add_field(name='შეიქმნა', value=ctx.guild.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
    embed.set_thumbnail(url=ctx.guild.icon_url)
    await ctx.send(embed = embed)

@client.command()
async def userinfo(ctx, member : discord.Member):

    embed = discord.Embed(colour = member.color, timestamp = ctx.message.created_at)
    embed.set_author(name = f"User Info - {member}")
    embed.set_thumbnail(url = member.avatar_url)
    embed.add_field(name = "ID", value = member.id)
    embed.add_field(name = "სახელი", value = member.display_name)
    embed.add_field(name = "ექაუნთის შექმნის დროს", value = member.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
    embed.add_field(name = "სერვერზე შემოსვლის დრო", value = member.joined_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
    embed.add_field(name = "როლი", value = member.top_role.name)


    await ctx.send(embed = embed)

@client.command()
async def clear(ctx, amount : int):
    await ctx.channel.purge(limit = amount)

@client.command()
async def ping(ctx):
    embed = discord.Embed(description = f"შენი პინგია {round(client.latency * 1000)}ms", colour = discord.Colour.darker_grey())
    await ctx.send(embed = embed)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#moderation /kick/ban/mute/umute

#Ban
@client.command(pass_context = True)
@commands.has_permissions(ban_members = True)
async def ban(ctx, adamiani : discord.Member, *, reason = None):
    await adamiani.ban(reason = reason)
    embed = discord.Embed(title = f'{adamiani.name}-ს დაედო ბანი !', colour = discord.Colour.darker_grey())
    embed.add_field(name = "Goodbye!", value=":hammer:")
    embed.set_thumbnail(url = adamiani.avatar_url)
    await ctx.send(embed = embed)

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "b.ban [სახელი]", colour = discord.Colour.red())
        await ctx.send(embed = embed)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

#unban 
@client.command()
@commands.has_permissions(administrator = True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            embed = discord.Embed(description = f"ბანი აეხსნა {user.mention}-ს", colour = discord.Colour.darker_grey())
            await ctx.send(embed = embed)
            return

@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "b.ban @სახელი !", colour = discord.Colour.red())
        await ctx.send(embed = embed)

#-----------------------------------------------------------------------------------------------------------------------------------------------------

#kick
@client.command(pass_context = True)
@commands.has_permissions(kick_members = True)
async def kick(ctx, member : discord.Member, *, reason = None):
    await member.kick(reason = reason)
    embed = discord.Embed(description = f"{member} გავარდა ჯგუფიდან !", colour = discord.Colour.darker_grey())
    await ctx.send(embed = embed)

@kick.error 
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "ჩაწერე იმ ადამიანის სახელი ვინც გინდა გააგდო !", colour = discord.Colour.red())
        await ctx.send(embed = embed)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#mute
@client.command()
async def mute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    guild = ctx.guild
    if role not in guild.roles:
        perms = discord.Permissions(send_messages=False, speak=False)
        await guild.create_role(name="Muted", permissions=perms)
        await member.add_roles(role)
        embed = discord.Embed(description = f"🔨{member} უკვე გაჩუმებულია \n თუ გინდა mute ახსნა ჩაწერე b.umute", colour = discord.Colour.darker_grey())
        await ctx.send(embed = embed)
    else:
        await member.add_roles(role) 
        embed = discord.Embed(description =f"🔨{member} გაჩუმდა")
        await ctx.send(embed = embed)

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "b.mute [სახელი]")
        await ctx.send(embed = embed)

@client.command()
async def unmute(ctx, member : discord.Member):
    role = discord.utils.get(ctx.guild.roles, name = "Muted")
    embed = discord.Embed(description = f"{member} unmuted", colour = discord.Colour.darker_grey())
    await member.remove_roles(role)
    await ctx.send(embed = embed)

@unmute.error 
async def umute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "ჩაწერე იმ ადამიანის სახელი ვისაც გინდა Mute ახსნა !")
        await ctx.send(embed = embed)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------


#poll
@client.command()
async def poll(ctx, *, message):
    embed = discord.Embed(title = "Poll", description = f"New poll: {message} \n✅ = Yes**\n**❎ = No", colour = discord.Colour.darker_grey())
    await ctx.channel.purge(limit=1)
    message = await ctx.send(embed = embed)
    await message.add_reaction('❎')
    await message.add_reaction('✅')

@poll.error
async def poll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "b.poll Among-Us gindaat ?", colour = discord.Colour.red())
        await ctx.send(embed = embed)

# -------------------------------------------------------------------------------------------------------------------------------------------------------------

#role 
@client.command()
async def addrole(ctx, member: discord.Member = None, role: discord.Role = None, reason = None):
    await member.add_roles(role)
    embed = discord.Embed(title = "როლი", description = f"{member.mention}-მ მიიღო წოდება {role.mention}", colour = discord.Colour.darker_grey())
    await ctx.send(embed = embed)   

@addrole.error
async def addrole_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "b.addrole [სახელი] [წოდება]", colour = discord.Colour.red())
        await ctx.send(embed = embed)

@client.command()
async def removerole(ctx, member: discord.Member = None, role: discord.Role = None, reason = None):
    await member.remove_roles(role)
    embed = discord.Embed(title = "როლი", description = f"{member.mention}-ს ჩამოერთვა წოდება {role.mention}", colour = discord.Colour.darker_grey())
    await ctx.send(embed = embed)

@removerole.error
async def removerole_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "b.removerole [სახელი] [წოდება]", colour = discord.Colour.red())
        await ctx.send(embed = embed)

@client.command()
async def createrole(ctx, *, rolename = None):
    role = await ctx.guild.create_role(name=rolename, mentionable=True)
    embed = discord.Embed(description = f"იქმნება ახალი წოდება {role.mention}")
    await ctx.author.add_roles(role)
    await ctx.send(embed = embed)

@createrole.error
async def createrole_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "ჩაწერე როლის სახელი !", colour = discord.Colour.red())
        await ctx.send(embed = embed)

@client.command(oass_context = True)
async def deleterole(ctx, *, role: discord.Role):
    embed = discord.Embed(description = f"გაუქმდა წოდება {role}", colour = discord.Colour.darker_grey())
    await role.delete()
    await ctx.send(embed = embed)

@deleterole.error
async def deleterole_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "b.deleterole {როლის სახელი}", colour = discord.Colour.red())
        await ctx.send(embed = embed)
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------
#nickname
@client.command()
async def changenickname(ctx, member: discord.Member, nick: str):
    await member.edit(nick = nick)
    embed = discord.Embed(description = f"{member}-ს შეეცვალა სახელი\nმისი ახალი სახელია {nick}", colour = discord.Colour.darker_grey())
    await ctx.send(embed = embed)

@changenickname.error
async def changenickname_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "b.changenickname @nika kvercxi", colour = discord.Colour.red())
        await ctx.send(embed = embed)
#---------------------------------------------------------------------------------------------------------------------------------------------------------
@client.command(pass_context = True)
async def invite(ctx, *argument):
    link = await ctx.channel.create_invite(max_uses = 1, unique = True)
    await ctx.send(link)

@client.command()
async def dawere(ctx, times : int, url: str):
    for i in range(times):
        await ctx.send(url)
    
@client.command()
async def botinvite(ctx):
    embed = discord.Embed(description = "https://discord.com/api/oauth2/authorize?client_id=717088492840026205&permissions=8&scope=bot", colour = discord.Colour.darker_grey())
    await ctx.send(embed = embed)

@client.command()
async def botstat(ctx):
    embed = discord.Embed(description = f"BlackHole(Georgian Edition) არის {len(client.guilds)} სერვერში", colour = discord.Colour.darker_grey())
    await ctx.send(embed = embed)

@client.command()
async def info(ctx):
    await ctx.send("Aleksandre#4848")

@client.command()
async def help_me(ctx):
    embed = discord.Embed(description = "ბოტის მოსაწვევი ლინკი: https://discord.com/api/oauth2/authorize?client_id=717088492840026205&permissions=8&scope=bot", colour = discord.Colour.darker_grey())

    embed.add_field(name = "ავტორი", value = "Aleksandre#4848")
    embed.add_field(name = "b.ping", value = "გეუბნება პინგს ")
    embed.add_field(name = "b.clear", value = "ასუფთავებს მესიჯებს")
    embed.add_field(name = "b.kick", value = "გააგდებს ჯგუფის წევრს")
    embed.add_field(name = "b.ban", value = "ბანს დაადებს ჯგუფის წევრს")
    embed.add_field(name = "b.mute", value = "გააჩუმებს ჯგუფის წევრს")
    embed.add_field(name = "b.unmute", value = "unmute")
    embed.add_field(name = "b.unban", value = "ბანს ახსნის")
    embed.add_field(name = "b.info", value = "ნახავ ბოტის ინფორმაციას")
    embed.add_field(name = "b.invite", value = "შექმნის სერვერის ლინკს")
    embed.add_field(name = "b.tchannel", value = "შექმნის Text Channel-ს (ეს კოდი არის ადმინებისთვის)")
    embed.add_field(name = "b.vchannel", value = "შექმნის Voice Channel-ს (ეს კოდი არის ადმინებისთვის)")
    embed.add_field(name = "b.tdelete", value = "წაშლის Text Channel-ს")
    embed.add_field(name = "b.vdelete", value = "წაშლის Voice Channel-ს")
    embed.add_field(name = "b.changenickname", value = "შეუცვლის სახელს")
    embed.add_field(name = "b.userinfo", value = "გეუბნება ჯგუფის წევრის ინფორმაციას")
    embed.add_field(name = "b.serverinfo", value = "გეუბნება სერვერის ინფორმაციას")
    embed.add_field(name = "b.botstat", value = "ბოტის სტატისტიკა")
    embed.add_field(name = "b.dawere", value = "მაგ: b.dawere 5 Aleksandre")
    embed.add_field(name = "b.botinvite", value = "ბოტის მოსაწვევი ლინკი")
    embed.add_field(name = "b.addrole", value = "მისცემს წოდებას ჯგუფის წევრს")
    embed.add_field(name = "b.removerole", value = "ჩამოართმევს წოდებას")
    embed.add_field(name = "b.createrole", value = "შექმნის წოდებას")
    embed.add_field(name = "b.deleterole", value = "წაშლის წოდებას")


    await ctx.send(embed = embed)


@client.command()
async def tchannel(ctx, name : str):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=name)
    if not existing_channel:
        embed = discord.Embed(description = f"იქმნება ახალი Text Channel-ი {name}", colour = discord.Colour.darker_grey())
        await ctx.send(embed = embed)
        await guild.create_text_channel(name)

@tchannel.error
async def tchannel_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "ჩაწერე Channel-ის სახელი !", colour = discord.Colour.red())
        await ctx.send(embed = embed)


@client.command()
async def vchannel(ctx, name1 : str):
    guild1 = ctx.guild
    existing_channel1 = discord.utils.get(guild1.channels, name = name1)
    if not existing_channel1:
        embed = discord.Embed(description = f"იქმნება ახალი Voice Channel-ი {name1}", colour = discord.Colour.darker_grey())
        await ctx.send(embed = embed)
        await guild1.create_voice_channel(name1)

@vchannel.error
async def vchannel_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "ჩაწერე Channel-ის სახელი !", colour = discord.Colour.red())
        await ctx.send(embed = embed)

@client.command()
async def tdelete(ctx, ch : discord.TextChannel):
    embed = discord.Embed(description = f"წაიშალა Text-Channel-ი {ch}", colour = discord.Colour.darker_grey())
    await ch.delete()
    await ctx.send(embed = embed)

@tdelete.error
async def tdelete_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "ჩაწერე Text-channel-ის სახელი !", colour = discord.Colour.red())
        await ctx.send(embed = embed)

@client.command()
async def vdelete(ctx, vh : discord.VoiceChannel):
    embed = discord.Embed(description = f"წაიშალა Voice-Channel-ი {vh}", colour = discord.Colour.darker_grey())
    await vh.delete()
    await ctx.send(embed = embed)

@vdelete.error
async def vdelete_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title = "შეცდომა", description = "ჩაწერე Voice-Channel-ის სახელი !", colour = discord.Colour.red())
        await ctx.send(embed = embed)

client.run()