import math
import time
import random
import urllib.request

from .evaluator import NativeFunction

def register_stdlib(env):
    env.set("sin", NativeFunction(lambda args: math.sin(args[0])))
    env.set("cos", NativeFunction(lambda args: math.cos(args[0])))
    env.set("floor", NativeFunction(lambda args: math.floor(args[0])))
    env.set("random", NativeFunction(lambda args: random.random()))
    env.set("sleep", NativeFunction(lambda args: time.sleep(args[0])))
    env.set("current_time", NativeFunction(lambda args: time.time()))
    
    def read_file(args):
        with open(args[0], 'r') as f:
            return f.read()
    env.set("read_file", NativeFunction(read_file))
    
    def write_file(args):
        with open(args[0], 'w') as f:
            f.write(args[1])
        return None
    env.set("write_file", NativeFunction(write_file))
    
    def fetch_url(args):
        try:
            with urllib.request.urlopen(args[0]) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            return str(e)
            
    env.set("fetch_url", NativeFunction(fetch_url))
