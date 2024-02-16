import json
import random
from discord import User

actualState = None
    
def writeJson(channels: list):
    print("Writing Json..")
    
    test = {}
    
    for x in channels:
        index = channels.index(x)
        test[index] = {}
        test[index]["id"] = channels[index].id
        test[index]["name"] = channels[index].name
    
    
    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(test, f, indent=4)
        
def getChannelsName():
    file = open("channels.json", encoding="utf-8")
    data = json.load(file)
     
    return data


def getRandomStatus():
    global actualState
    
    with open("./status.json", encoding='utf-8') as f:
        data:list = json.load(f)
        
        if actualState == None:
            n = random.randint(0, len(data) - 1)
            
            nombre:str = data[n]["name"]
            tipo:str = data[n]["type"]
            
            actualState = data[n]
            return nombre, tipo
        else:
            newData = data
            newData.remove(actualState)
            
            n = random.randint(0, len(newData) - 1)
            
            nombre:str = newData[n]["name"]
            tipo:str = newData[n]["type"]
            
            actualState = newData[n]
            return nombre, tipo
        
def getCustomRoles(*args: str):
    
    roles = open("./roles.json", encoding='utf-8')
    data = json.load(roles)
    
    if len(args) == 0:
        return data
    else:
        return data[f"{args[0]}"] 


def WriteRol(user: User, nombre, color, rol_id, icon_url):
    
    data = getCustomRoles()
    
    data[f"{user.id}"] = {}
    data[f"{user.id}"]["name"] = user.name
    data[f"{user.id}"]["rol_id"] = rol_id
    data[f"{user.id}"]["rol_name"] = nombre
    data[f"{user.id}"]["custom_color"] = color
    data[f"{user.id}"]["custom_icon"] = icon_url
    
    with open("./roles.json", mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    
    