class Environment:
    def __init__(self, outer=None):
        self.store = {}
        self.consts = set()
        self.outer = outer

    def get(self, name):
        if name in self.store:
            return self.store[name]
        elif self.outer is not None:
            return self.outer.get(name)
        return None

    def set(self, name, value, is_const=False):
        if name in self.store and name in self.consts:
            raise RuntimeError(f"Cannot reassign constant '{name}'")
        self.store[name] = value
        if is_const:
            self.consts.add(name)
        return value
        
    def assign(self, name, value):
        if name in self.store:
            if name in self.consts:
                raise RuntimeError(f"Cannot reassign constant '{name}'")
            self.store[name] = value
            return value
        elif self.outer is not None:
            return self.outer.assign(name, value)
        else:
            raise RuntimeError(f"Undefined variable '{name}'")
