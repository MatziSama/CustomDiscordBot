from discord import Interaction, ui, SelectOption
import os

class Memero(ui.Select):
    
    def __init__(self):
        lista = os.listdir("./images/memes/")
    
        options = []
        
        for meme in lista:
            lista.append(SelectOption(label=meme, value=meme))
            
        super().__init__(placeholder="Seleccione un meme:", options=options)
        
    async def callback(self, ctx: Interaction):
        await ctx.response.send_message(f'Elegiste {self.values[0]}')
    
class MemeroView(ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Memero())