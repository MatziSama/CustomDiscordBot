import asyncio
import datetime
import shutil
from typing import Self
import discord
import jsonHandler
from discord import app_commands 
import typing
import os
import re
from modules.imageGenerator import generateImage
from rolManager import ExistingRoleEmbedView, NewRoleEmbedView

# -- Bot --
intents = discord.Intents.default()
intents.guild_messages = True
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)


# -- Utils --
token = "OTY2ODU5NTc0NjA0ODg2MTM2.GaA_-4.1G6oEeyIiw1ETSTSbehs9WewplZuaCsqcsRkvg"
tree = app_commands.CommandTree(client)


# -- Ids --
#803624601003098166 - general
#880945272321105941 - cementerio
#997630005314064505 - salon de juegos
server_id = 803624601003098163
log_channel_id = 880945272321105941
general_channel_id = 803624601003098166
update_channel_id = 1200955460728139886
matzi_id = 374711888409395210
manipulador_id = 1202070803680862290

# -- Paths --
images_path = "./images"
    
class Memero(discord.ui.Select):
    
    def __init__(self, message: discord.Message):
        lista = os.listdir("./images/memes/")
        self.msg = message
    
        options = []
        
        for meme in lista:
            options.append(discord.SelectOption(label=re.sub(r'.(png|jpg|gif)', '', meme), value=meme))
            
        super().__init__(placeholder="Seleccione un meme:", options=options)
        
    async def callback(self, ctx: discord.Interaction):
        await ctx.response.edit_message(content="Meme seleccionado!", view=None, delete_after=2)
        
        meme = discord.File(f"./images/memes/{self.values[0]}")
        
        await self.msg.reply(file=meme)
        
        
    
class MemeroView(discord.ui.View):
    def __init__(self, message):
        super().__init__()
        self.add_item(Memero(message=message))    

@client.event
async def on_ready():
    global log_channel, guild, general_channel, update_channel, manipulador_rol
    
    guild = client.get_guild(server_id)
    log_channel = await guild.fetch_channel(log_channel_id)
    general_channel = await guild.fetch_channel(general_channel_id)
    update_channel = await guild.fetch_channel(update_channel_id)

    manipulador_rol = guild.get_role(manipulador_id)
    
    os.system("cls")
    
    welcome = '¡Estoy Funcionando!'
    
    welcome = welcome.center(shutil.get_terminal_size().columns, '-')
    
    print('\n')
    print(welcome)
    print('\n')
    
    
    await tree.sync(guild=discord.Object(id=server_id))
    await tree.sync()
    
    await changePresence()
    
    
    
async def changePresence():
    await client.wait_until_ready()
    
    while not client.is_closed():
        activityName, activityType = jsonHandler.getRandomStatus()
        activity = await getActivity(activityType, activityName)
        
        await client.change_presence(activity=activity)
        
        await asyncio.sleep(60)
        
    
async def getActivity(type, name):
    tipo = None

    if type == 'watch': tipo = discord.ActivityType.watching
    elif type == 'play': tipo = discord.ActivityType.playing
    elif type == 'listening': tipo = discord.ActivityType.listening
    
    actividad = discord.Activity(type=tipo, name=name)
    return actividad
    
    
# ---- |COMANDO: RESETEAR_NOMBRES| ----
@tree.command(name="resetear_nombres", description="Cambia los nombres de los canales a sus predeterminados.", guild=discord.Object(id=server_id))
@app_commands.describe(mensaje="Envía un mensaje al canal general al cambiar los nombres.")
async def reset_command(ctx: discord.Interaction, mensaje: typing.Optional[str]):
    global log_channel, general_channel
    if not ctx.user.guild_permissions.administrator:
        await ctx.response.send_message("No tienes permisos para usar este comando.", ephemeral=True)
        await log_channel.send(f"<@{ctx.user.id}> intentó usar el comando de resetear canales")
        return
    data = jsonHandler.getChannelsName()
    
    for d in data:
        channel = guild.get_channel(data[f"{d}"]["id"])
        await channel.edit(name=data[f"{d}"]["name"])
    
    await ctx.response.send_message("Nombres cambiados exitosamente.")
    
    if mensaje != None:
        await general_channel.send(mensaje)   
# -------------------------------------
    
# ---- |COMANDO: GUARDAR_NOMBRES| ----

@tree.command(name="guardar_nombres", description="Guarda los nombres actuales de los canales", guild=discord.Object(id=server_id))
async def save_commands(ctx: discord.Interaction):
    global log_channel
    if not ctx.user.guild_permissions.administrator:
        await ctx.response.send_message("No tienes permisos para usar este comando.", ephemeral=True)
        await log_channel.send(f"<@{ctx.user.id}> intentó usar el comando de guardar nombres")
        return
    cates = guild.categories
    channels_list = []
    
    for x in range(2):
        for c in cates[x].channels:
            channels_list.append(c)
        
    jsonHandler.writeJson(channels_list)
    await ctx.response.send_message("Nombres guardados!", ephemeral=True)
    
# -------------------------------------

# ---- |COMANDO: RESTAURAR_IMAGEN| ----

async def ri_tipo_au(interaction, current):
    return [
        app_commands.Choice(name="Banner", value="banners"),
        app_commands.Choice(name="Perfil", value="pfp")
    ]

async def ri_version_au(interaction: discord.Interaction, current):
    tipo = interaction.namespace["tipo"]
    files = os.listdir(f"{images_path}/{tipo}")
    choices = []
    
    for f in files:
        name = re.sub(r'\.(png|jpg|jpeg)', '', f)
        choices.append(app_commands.Choice(name=name, value=f))
    
    return choices

@tree.command(name="restaurar_imagen", description="Vuelve a una imagen de perfil o banner guardado anteriormente.", guild=discord.Object(id=server_id))
@app_commands.autocomplete(tipo=ri_tipo_au, version=ri_version_au)
async def restaurar_imagen(ctx: discord.Interaction, tipo: str, version: str):
    global log_channel
    if not ctx.user.guild_permissions.administrator:
        await ctx.response.send_message("No tienes permisos para usar este comando.", ephemeral=True)
        await log_channel.send(f"<@{ctx.user.id}> intentó usar el comando de guardar nombres")
        return
    
    path = f"./images/{tipo}"
    if tipo == "pfp":
        with open(f"{path}/{version}", 'rb') as img:
            icon = img.read()
        await guild.edit(icon=icon)
        await ctx.response.send_message(f"Se cambió la imagen de perfil a: {version}")
    elif tipo == "banners":
        with open(f"{path}/{version}", 'rb') as img:
            icon = img.read()
        await guild.edit(banner=icon)
        await ctx.response.send_message(f"Se cambió la imagen del banner a: {version}")
        
# -------------------------------------

# ---- |COMANDO: INFO| ----

@tree.command(name="info", description="Un poco de la historia de este bot")
async def info(ctx: discord.Interaction):
    if ctx.user.bot:
        return
    
    desc = '''
    No tengo un nombre como tal, ¡pero puedes llamarme Maerie!
    Soy una aplicación desarrollada con Python por <@374711888409395210>
    
    Mi función en este servidor es ayudar a la gestión del mismo gracias a mis comandos los cuales realizan multiples tareas al mismo tiempo.
    
    Fui reciclada de un bot anterior, su propósito era decir <<el pepe>> en múltiples idiomas, una tarea bastante burda en comparación a mis funciones.
    
    Sin dudas <<El Pepe Bot>> fue unos de los proyectos más primerizos en el camino de Matzi, y aunque tal vez muchos no lo recuerden, ahora yo nací de sus escombros, ¡y que belleza que soy!
    
    Como un bot tan capáz me duele (no realmente) ver partir a un compañero, pero le dejó su lugar a algo mejor, a mi.
    
    Descansa en paz, no te extrañaremos.
    '''
    img = discord.File('./images/res/elpepe.jpg', filename="elpepe.jpg")
    pf_img = discord.File('./images/res/sunflower.jpeg', filename="sunflower.jpeg")
    embed = discord.Embed(title="Mi historia", colour=6208467, type='rich', description=desc)
    embed.set_image(url='attachment://elpepe.jpg')
    embed.set_author(name="Maerie", icon_url='attachment://sunflower.jpeg')
    
    await ctx.response.send_message(files=[img, pf_img], embed=embed)
    
# -------------------------------------

@tree.command(name="rol", description="Asigna un 'alter' a tu cuenta o modifica el ya existente", guild=discord.Object(id=server_id))
async def modifyRol(ctx: discord.Interaction):
    
    if not manipulador_rol in ctx.user.roles:
        emb = discord.Embed(title="Permisos insuficientes", 
                            description="No tienes el rol necesario para realizar esta acción, tal vez quieras comunicarte con <@374711888409395210> para tener tu rol.",
                            color=discord.Color.brand_red()
                            )
        await ctx.response.send_message(embed=emb, ephemeral=True)
        return
    
    information = discord.Embed()
    user_id = ctx.user.id
    roles = jsonHandler.getCustomRoles()
    
    if f"{user_id}" in roles.keys():
        user_role = roles[f"{user_id}"]
        information.title = "Modificar rol"
        information.description = f'''
        Tu rol actual: **{user_role["rol_name"]}**
        *(El color de rol se muestra en la barra lateral izquierda)*
        
        ¿Qué desea hacer?
        '''
        information.color = discord.Colour.from_str(user_role["custom_color"])
        await ctx.response.send_message(embed=information, view=ExistingRoleEmbedView(ctx=ctx , call=modifyRol), ephemeral=True)
    else:
        information.title = "Crear rol nuevo"
        information.description = '''
        # ¡Comencemos!
        Para empezar dale click al botón de abajo, cuando lo hagas verás un recuadro donde podrás elegir:
        **Nombre**, **Color**, ~~Icono~~ *(próximamente)*
        
        # Cosas a tener en cuenta
        Cuando elijas el color de tu rol debe ser introducido en **formato hexadecimal**
        A continuación te brindamos una url donde podrás elegir tu color con más facilidad
        https://colorpicker.me/#d321e2
        
        Solo copia y pega el código en el recuadro, debe verse de esta manera:
        `#3fe06a` *(Incluyendo el numeral)*
        '''
        await ctx.response.send_message(embed=information, view=NewRoleEmbedView(ctx=ctx), ephemeral=True)
        
    
    
@tree.command(name="agregar_update", description="Envía una update al canal designado", guild=discord.Object(id=server_id))
@app_commands.describe(imagen = "Url de una imagen para agregar")
async def updateCommand(ctx:discord.Interaction, titulo: str, cuerpo: str, footer: typing.Optional[str], imagen: typing.Optional[str]):
    
    if not ctx.user.guild_permissions.administrator:
        await ctx.response.send_message("No tienes permitido usar este comando.", ephemeral=True)
        return
    
    formattedMessage = re.sub(r'\\n', "\n", cuerpo)
    print(f"Cuerpo: {cuerpo}")
    
    embed = discord.Embed(title=titulo, description=formattedMessage, colour=discord.Color.from_rgb(249, 148, 47))
    embed.timestamp = datetime.datetime.now()
    
    if not imagen == None:
        embed.set_image(url=imagen)
        
    if not footer == None:
        embed.set_footer(text=footer)
        
        
    await update_channel.send(embed=embed)
            
    await ctx.response.send_message("Hola, esta función todavía está en desarrollo!\nIntentalo de nuevo pronto", ephemeral=True)  
    
    
@tree.command(name="enviar_mensaje", description="Envía un mensaje como si fueras el bot, si se proporciona una id de mensaje se responderá a él.", guild=discord.Object(id=server_id))
@app_commands.describe(mensaje="Mensaje a enviar")
@app_commands.describe(id="Id del mensaje para responder")
async def enviar_mensaje(ctx: discord.Interaction, mensaje: str, id: typing.Optional[str]):
    if not manipulador_rol in ctx.user.roles:
        await ctx.response.send_message("Oops!, no deberías estar usando este comando.", ephemeral=True) 
        await log_channel.send(content=f"<@{ctx.user.id}> intentó usar el comando exclusivo de <&@{manipulador_id}>")
        return
    
    mensaje = re.sub(r'\\n', '\n', mensaje)
    
    if not id == None:
        try:
            id = int(id)
            messageToRespond = await ctx.channel.fetch_message(id)
            await messageToRespond.reply(content=mensaje)
            await ctx.response.send_message(content="Mensaje enviado", ephemeral=True, delete_after=3)
        except discord.NotFound:
            await ctx.response.send_message("No se pudo encontrar ese mensaje.", ephemeral=True)
            return
    else:
        await ctx.channel.send(content=mensaje)
        await ctx.response.send_message(content="Mensaje enviado", ephemeral=True, delete_after=3)


@tree.command(name="comando_de_prueba", description="Por favor no usar, es solo para propósitos de desarrollo.", guild=discord.Object(id=server_id))
async def dev_command(ctx: discord.Interaction):
    
    if not ctx.user.id == matzi_id:
        emb = discord.Embed(title="Permisos insuficientes", description="Solo Matzi puede usar este comando al ser un comando de programador, lo sentimos!")
        
        file = discord.File("./images/res/denied.png", "denied.png")
        emb.set_thumbnail(url="attachment://denied.png")
        
        await ctx.response.send_message(embed=emb, file=file, ephemeral=True)
        return
    
    
    await ctx.response.send_message("Received.", ephemeral=True)
#
#
# ----------------------------------------- CONTEXT MENU ----------------------------------------- 
#
#
@tree.context_menu(name="Banear usuario", guild=discord.Object(id=server_id))
async def fakeBan(ctx: discord.Interaction, user: discord.Member):
    global general_channel
    
    img = await generateImage(ctx.user.avatar.with_static_format("png"))
    miniatura = discord.File(img, filename='res.png')
    
    description = f'''
    <@{ctx.user.id}> intentó banear a <@{user.id}> usando mi comando.
    
    ¡Qué pésimo compañero!
    '''
    embed = discord.Embed(title="Acceso denegado", description=description, color=int('a50000', 16))
    embed.set_image(url='attachment://res.png')
    embed.set_author(name=ctx.user.name, icon_url=ctx.user.avatar.url)
    
    await general_channel.send(file=miniatura, embed=embed)
    await ctx.response.send_message("Troleado puto!", ephemeral=True)
    
    
@tree.context_menu(name="Globo de texto", guild=discord.Object(id=server_id))
async def punishUser(ctx: discord.Interaction, msg: discord.Message):
    
    await ctx.response.send_message("Seleccione un meme:", view=MemeroView(message=msg), ephemeral=True)
    
    
    
client.run(token)

