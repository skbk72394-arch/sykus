import math
import time
import random
import urllib.request
import os
import platform
import subprocess

from evaluator import NativeFunction

def register_stdlib(env):
    # Math namespace
    env.set("math", {
        "sin": NativeFunction(lambda args: math.sin(args[0])),
        "cos": NativeFunction(lambda args: math.cos(args[0])),
        "floor": NativeFunction(lambda args: math.floor(args[0])),
        "random": NativeFunction(lambda args: random.random())
    })
    
    # System namespace
    def system_run(args):
        try:
            subprocess.run(args[0], shell=True)
        except Exception as e:
            return str(e)
        return None
        
    def system_clear(args):
        os.system('cls' if os.name == 'nt' else 'clear')
        return None
        
    env.set("system", {
        "run": NativeFunction(system_run),
        "clear": NativeFunction(system_clear),
        "get_os": NativeFunction(lambda args: platform.system()),
        "sleep": NativeFunction(lambda args: time.sleep(args[0])),
        "torch": NativeFunction(lambda args: "Simulated: Torch " + str(args[0])),
        "battery": NativeFunction(lambda args: "Simulated: Battery 100%"),
        "vibrate": NativeFunction(lambda args: "Simulated: Vibrate")
    })
    
    # File namespace
    def file_read(args):
        with open(args[0], 'r') as f:
            return f.read()
            
    def file_write(args):
        with open(args[0], 'w') as f:
            f.write(args[1])
        return None
        
    env.set("file", {
        "read": NativeFunction(file_read),
        "write": NativeFunction(file_write)
    })
    
    # Net namespace
    def net_fetch(args):
        try:
            with urllib.request.urlopen(args[0]) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            return str(e)
            
    env.set("net", {
        "fetch": NativeFunction(net_fetch)
    })

    # AI namespace
    def ai_ask(args):
        query = args[0]
        # Setup for a real API key injection
        return f"AI Mock Response to: {query}"

    env.set("ai", {
        "ask": NativeFunction(ai_ask)
    })
    
    env.set("current_time", NativeFunction(lambda args: time.time()))