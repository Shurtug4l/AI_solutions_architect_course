# Object-Oriented Programming

## Classes and Instances

```python
class Dog:
    species = "Canis lupus familiaris"   # class attribute (shared by all instances)

    def __init__(self, name, age):       # initializer — called when instance is created
        self.name = name                 # instance attributes (unique per instance)
        self.age = age

    def bark(self):
        return f"{self.name} says woof!"

    def __repr__(self):
        return f"Dog(name={self.name!r}, age={self.age})"

rex = Dog("Rex", 3)
rex.bark()           # "Rex says woof!"
rex.name             # "Rex"
Dog.species          # "Canis lupus familiaris"
rex.species          # also works — instance lookup falls through to class
```

`self` is a convention (not a keyword). It refers to the current instance and must be the first parameter of every instance method.

`__init__` is not a constructor — the object already exists when `__init__` is called. The actual constructor is `__new__`. In practice, `__init__` is where you initialize instance state.

---

## Class vs Instance Attributes

```python
class Counter:
    count = 0                  # class attribute

    def __init__(self):
        Counter.count += 1
        self.id = Counter.count  # instance attribute

a = Counter()
b = Counter()
Counter.count   # 2
a.id            # 1
b.id            # 2
```

If you assign `self.count = x`, you create an **instance attribute** that shadows the class attribute — the class attribute is unchanged.

---

## Methods

### Instance Methods

Standard methods. Receive the instance as `self`.

### Class Methods

Receive the class as `cls`. Used as alternate constructors or for operations on the class itself.

```python
class Date:
    def __init__(self, year, month, day):
        self.year, self.month, self.day = year, month, day

    @classmethod
    def from_string(cls, s):       # factory method
        y, m, d = map(int, s.split('-'))
        return cls(y, m, d)        # works correctly in subclasses too

d = Date.from_string("2024-01-15")
```

### Static Methods

No `self` or `cls`. Logically grouped with the class but do not access class or instance state.

```python
class MathUtils:
    @staticmethod
    def clamp(value, lo, hi):
        return max(lo, min(value, hi))

MathUtils.clamp(15, 0, 10)   # 10
```

### Property

Turn a method into a computed attribute. Allows read-only access, validation on set, and lazy computation.

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self):
        import math
        return math.pi * self._radius ** 2

c = Circle(5)
c.radius         # 5  — calls getter
c.radius = 10    # calls setter
c.area           # 314.15...  — computed on access
```

---

## Inheritance

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return f"{self.name}: woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name}: meow!"

for animal in [Dog("Rex"), Cat("Whiskers")]:
    print(animal.speak())   # polymorphic dispatch
```

### super()

Access the parent class's implementation. Essential in `__init__` to initialize the parent:

```python
class GuideDog(Dog):
    def __init__(self, name, owner):
        super().__init__(name)    # call Dog.__init__
        self.owner = owner
```

Always call `super().__init__()` unless you have a specific reason not to. Failing to do so leaves parent state uninitialized.

### Multiple Inheritance and MRO

Python supports multiple inheritance. The **Method Resolution Order** (MRO) is determined by the **C3 linearization** algorithm:

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

D.__mro__   # (D, B, C, A, object)
```

`super()` follows the MRO — it calls the next class in the MRO, not necessarily the direct parent. This enables the **cooperative multiple inheritance** pattern where all `__init__` methods in the hierarchy are called correctly.

---

## Dunder (Magic) Methods

Define how instances respond to built-in operations.

| Method | Triggered by |
|--------|-------------|
| `__init__(self, ...)` | `ClassName(...)` |
| `__repr__(self)` | `repr(obj)`, debugging |
| `__str__(self)` | `str(obj)`, `print(obj)` |
| `__len__(self)` | `len(obj)` |
| `__getitem__(self, key)` | `obj[key]` |
| `__setitem__(self, key, val)` | `obj[key] = val` |
| `__contains__(self, item)` | `item in obj` |
| `__iter__(self)` | `for x in obj`, `iter(obj)` |
| `__next__(self)` | `next(obj)` |
| `__eq__(self, other)` | `obj == other` |
| `__lt__(self, other)` | `obj < other` |
| `__hash__(self)` | `hash(obj)`, use in sets/dicts |
| `__call__(self, ...)` | `obj(...)` — callable instance |
| `__enter__` / `__exit__` | `with obj:` — context manager |
| `__add__`, `__mul__`, ... | `obj + other`, `obj * other` |

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):           # required if __eq__ is defined
        return hash((self.x, self.y))

v1 + v2   # calls __add__
```

**Important**: if you define `__eq__`, Python sets `__hash__` to `None` by default (making the object unhashable). Define `__hash__` explicitly if you need the object in sets or as dict keys.

---

## Abstract Base Classes

Enforce that subclasses implement specific methods:

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        ...

    @abstractmethod
    def perimeter(self) -> float:
        ...

class Rectangle(Shape):
    def __init__(self, w, h):
        self.w, self.h = w, h

    def area(self):
        return self.w * self.h

    def perimeter(self):
        return 2 * (self.w + self.h)

Shape()        # raises TypeError — cannot instantiate abstract class
Rectangle(3, 4).area()   # 12
```

---

## Dataclasses

Auto-generate boilerplate (`__init__`, `__repr__`, `__eq__`) from field annotations:

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float
    z: float = 0.0                     # default value

@dataclass(frozen=True)                # immutable — also makes it hashable
class Config:
    host: str
    port: int = 8080

@dataclass
class Inventory:
    items: list = field(default_factory=list)   # mutable default — use field()

p = Point(1.0, 2.0)
p.x          # 1.0
repr(p)      # 'Point(x=1.0, y=2.0, z=0.0)'
```

`field(default_factory=...)` is the dataclass equivalent of the mutable default argument fix.

---

## Encapsulation Conventions

Python has no enforced access control. Conventions:

| Name | Convention | Meaning |
|------|-----------|---------|
| `attribute` | Public | Part of the public API |
| `_attribute` | Protected | Internal; not for external use, but accessible |
| `__attribute` | Private (name-mangled) | Triggers name mangling to `_ClassName__attribute`; avoids accidental override in subclasses |

Name mangling is rarely needed. Use `_prefix` for internal attributes and document the public API.

---

## OOP Design Principles (Reference)

| Principle | Meaning |
|-----------|---------|
| **Single Responsibility** | A class should do one thing |
| **Open/Closed** | Open for extension, closed for modification (use inheritance/composition) |
| **Liskov Substitution** | Subclass must be usable wherever the parent is expected |
| **Interface Segregation** | Prefer small, specific interfaces over large general ones |
| **Dependency Inversion** | Depend on abstractions (ABCs), not concrete implementations |
| **Composition over inheritance** | Prefer building with small, single-purpose objects rather than deep hierarchies |
