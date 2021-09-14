class MyObject:
    def __init__(self):
        self.public_field = 5
        self.__private_field = 10

    def get_private_field(self):
        return self.__private_field

foo = MyObject()
print(foo.get_private_field())
print(foo.__private_field)

class MyParentObject:
    def __init__(self):
        self.__private_field = 10

class MyChildObject(MyParentObject):
    def get_private_field(self):
        return self.__private_field

baz = MyChildObject()
baz.get_private_field()
print(baz._MyParentObject__private_field)
print(baz.__dict__)

class ApiClass:
    def __init__(self):
        self._value = 5

    def get(self):
        return self._value

class Child(ApiClass):
    def __init__(self):
        super().__init__()
        self._value = 'hello' # 衝突

class ApiClass:
    def __init__(self):
        self.__value = 5 # double underscore

    def get(self):
        return self.__value # # double underscore

class Child(ApiClass):
    def __init__(self):
        super().__init__()
        self._value = 'hello'

a = Child()
print(f'{a.get()} and {a._value} should be differenct')
