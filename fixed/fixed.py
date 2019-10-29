import ctypes

class fixed:
    value = ctypes.c_int(0)
    factor = 16

    def from_int(self, i : int):
        self.value = i << self.factor

    def from_float(self, f:float):
        pass

def main():
    pass

if __name__ == "__main__":
    main()