class Environment:
    def __init__(self, outer=None):
        self.store = {}
        self.constants = set()
        self.outer = outer

    def get(self, name):
        if name in self.store:
            return self.store[name]
        elif self.outer is not None:
            return self.outer.get(name)
        else:
            return None

    def set(self, name, value, is_const=False):
        if name in self.store:
            raise RuntimeError(f"Variable '{name}' is already defined.")
        self.store[name] = value
        if is_const:
            self.constants.add(name)
        return value

    def assign(self, name, value):
        if name in self.store:
            if name in self.constants:
                raise RuntimeError(f"Cannot assign to constant '{name}'")
            self.store[name] = value
            return value
        elif self.outer is not None:
            return self.outer.assign(name, value)
        else:
            raise RuntimeError(f"Undefined variable '{name}'")
