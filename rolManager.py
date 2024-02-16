from typing import Any, Coroutine
from discord import Emoji, Interaction, PartialEmoji, TextStyle, ButtonStyle, Colour, Embed
import discord.ui as UI
import jsonHandler

class RolModal(UI.Modal):
    
    title = "Crear Rol"
    
    nombre = UI.TextInput(label="Nombre del rol", style=TextStyle.short, custom_id="rol_name", placeholder="¡Un nombre asombroso!")
    color = UI.TextInput(label="Color del rol", style=TextStyle.short, custom_id="rol_color", placeholder="#8c50ef")
    
    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer()
        
class NewRoleEmbedView(UI.View):
    
    class StartButton(UI.Button):
        def __init__(self, ctx: Interaction):
            super().__init__(label="Empezar", style=ButtonStyle.green)
            
        async def callback(self, interaction: Interaction):
            await newRole(ctx = interaction)
    
    def __init__(self, ctx: Interaction):
        super().__init__()
        self.add_item(self.StartButton(ctx=ctx))       

class ExistingRoleEmbedView(UI.View):
    
    class EditButton(UI.Button):
        
        def __init__(self, ctx: Interaction, call):
            super().__init__(label="Editar", style=ButtonStyle.blurple)
            self._call = modifyRole
            
        async def callback(self, ctx: Interaction):
            await self._call(ctx)
            
    class FinishButton(UI.Button):
        
        def __init__(self, ctx: Interaction):
            super().__init__(label="Finalizar", style=ButtonStyle.green)
            
        async def callback(self, interaction: Interaction):
            info = jsonHandler.getCustomRoles(interaction.user.id)
            role = interaction.guild.get_role(info["rol_id"])
            color = Colour.from_str(info["custom_color"])
            desc = f'''
            Se cancelaron las modificaciones de tu rol.
            
            Nombre: **{info["rol_name"]}**
            *(El color de rol se muestra en la barra lateral izquierda)*
            '''
            emb = Embed(title="Finalizado", description=desc, color=color)
            
            if not role in interaction.user.roles:
                await interaction.user.add_roles(role)
            
            await interaction.response.edit_message(view=None, embed=emb)
    
    def __init__(self, ctx: Interaction, call):
        super().__init__()
        self.add_item(self.EditButton( ctx=ctx, call=call ))
        self.add_item(self.FinishButton( ctx=ctx ))
        
    
async def newRole(ctx: Interaction):
    modal = RolModal()
    modal.title = "Crea tu rol"
    
    await ctx.response.send_modal(modal)
    await modal.wait()
    
    _name = str(modal.children[0])
    __color = str(modal.children[1])
    responseContent = "Se cambió con éxito la información de tu rol."
    
    try:
        _color = Colour.from_str(__color)
    except ValueError:
        responseContent = "El valor para el color asignado es inválido, así que se agregó un valor aleatorio.\nIntente usar formatos de colores hexadecimales.\n\nSe cambió con éxito la información de tu rol."
        _color = Colour.random()
        
    role = await ctx.guild.create_role(name=_name, colour=_color)
    icon_url = role.icon.url if not role.icon == None else str(None)
    
    await ctx.user.add_roles(role)
    
    responseContent = responseContent + "\n\n" + f"Tu nuevo rol: **{_name}** \n*(El color de rol se muestra en la barra lateral izquierda)*"
    newEmbed = Embed(title="Rol creado con éxito", description=responseContent, color=_color)
    
    if not icon_url == "None":
        newEmbed.set_thumbnail(url=icon_url)
    
    jsonHandler.WriteRol(ctx.user, _name, str(_color), role.id, icon_url)
    await ctx.edit_original_response(view=None, embed=newEmbed)
    
async def modifyRole(ctx: Interaction):
    modal = RolModal()
    modal.title = "Modificar Rol"
    roles = jsonHandler.getCustomRoles()
    
    role = ctx.guild.get_role(roles[f'{ctx.user.id}']["rol_id"])
    
    icon_url = role.icon.url if not role.icon == None else str(None)
    
    if role == None:
        await newRole(ctx)
        return
    
    user_role = roles[f"{ctx.user.id}"]
    
    modal.nombre.placeholder = user_role["rol_name"]
    modal.nombre.default = user_role["rol_name"]
    modal.nombre.required = False
    
    modal.color.placeholder = user_role["custom_color"]
    modal.color.default = user_role["custom_color"]
    modal.color.required = False
    
    await ctx.response.send_modal(modal)
    await modal.wait()
    
    _name = str(modal.children[0])
    __color = str(modal.children[1])
    
    if __color == "":
        __color = str(modal.children[1].default)
        
    if _name == "":
        _name = str(modal.children[0].default)
    
    responseContent = "Se cambió con éxito la información de tu rol."
    
    try:
        _color = Colour.from_str(__color)
    except ValueError:
        responseContent = "El valor para el color asignado es inválido, así que se agregó un valor aleatorio.\nIntente usar formatos de colores hexadecimales.\n\nSe cambió con éxito la información de tu rol.\n\n"
        _color = Colour.random()
        
    
    responseContent = responseContent + f"\nTu nuevo nombre de rol: **{_name}**\n*(El color de rol se muestra en la barra lateral izquierda)*"
    
    await role.edit(name=_name, color=_color)
    
    if not role in ctx.user.roles:
        await ctx.user.add_roles(role)
        
    resEmbed = Embed(title="Rol cambiado con éxito", description=responseContent, color=_color)
    
    if not icon_url == "None":
        resEmbed.set_thumbnail(url=icon_url)
        
    jsonHandler.WriteRol(ctx.user, _name, str(_color), role.id, icon_url)
    await ctx.edit_original_response(view=None, embed=resEmbed)