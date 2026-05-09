# Object-Oriented Programming

## TL;DR

In Python, classes are factories for objects with shared behaviour, not the rigid contracts they are in Java or C++. Every method takes the instance as its first argument (named `self` by convention) and **`__init__` is not the constructor** — the object already exists when `__init__` is called; the real constructor is `__new__`. Three method flavours: instance methods take `self`, class methods take `cls` (used for alternate constructors), static methods take neither. **Properties** turn methods into computed attributes, useful for read-only views, lazy computation, and validation. Inheritance gives you polymorphism via shared interfaces; **multiple inheritance** is supported and method resolution follows the **C3 linearisation** (the MRO). The data model is exposed through **dunder methods** — define `__add__` to make `+` work, `__eq__` for `==`, `__iter__` for `for x in obj`. **Dataclasses** auto-generate boilerplate (`__init__`, `__repr__`, `__eq__`) from type-annotated fields and should be your default for plain data containers. Two operational reminders: if you define `__eq__` you must define `__hash__` (or accept the object becoming unhashable), and `field(default_factory=list)` is the dataclass equivalent of the mutable-default-argument fix.

## Cheatsheet

| Concept | Syntax | When |
|---|---|---|
| Instance method | `def m(self, ...)` | Standard methods |
| Class method | `@classmethod def m(cls, ...)` | Alternate constructors, class-level operations |
| Static method | `@staticmethod def m(...)` | Logically grouped utility, no class/instance state |
| Property | `@property def x(self): ...` | Computed attribute, read-only by default |
| Property setter | `@x.setter` | Validation on set |
| Inheritance | `class Sub(Base):` | Reuse + polymorphism |
| Parent call | `super().__init__(...)` | Initialise parent state in subclass |
| Abstract method | `@abstractmethod` (in `ABC` subclass) | Force subclasses to implement |
| Dataclass | `@dataclass` | Auto-generate `__init__`, `__repr__`, `__eq__` |
| Frozen dataclass | `@dataclass(frozen=True)` | Immutable; hashable |
| Mutable default in dataclass | `field(default_factory=list)` | Avoid shared mutable state |
| Equality + hashable | `__eq__` and `__hash__` together | Use in sets / dict keys |
| Custom add | `__add__(self, other)` | Make `obj + other` work |
| Iteration | `__iter__`, `__next__` | Make object iterable |
| Context manager | `__enter__`, `__exit__` | `with obj:` |
| Callable instance | `__call__(self, ...)` | `obj(...)` |

---

## Classes and instances

```python
class Dog:
    species = "Canis lupus familiaris"      # class attribute (shared across instances)

    def __init__(self, name, age):          # initialiser — called when instance is created
        self.name = name                    # instance attributes (unique per instance)
        self.age = age

    def bark(self):
        return f"{self.name} says woof!"

    def __repr__(self):
        return f"Dog(name={self.name!r}, age={self.age})"

rex = Dog("Rex", 3)
rex.bark()              # "Rex says woof!"
rex.name                # "Rex"
Dog.species             # "Canis lupus familiaris"
rex.species             # also works — instance lookup falls through to the class
```

`self` is a convention, not a keyword. Every instance method's first parameter receives the instance.

`__init__` is not technically a constructor — by the time it runs, the object already exists, allocated by `__new__`. In day-to-day code you only ever override `__init__` to populate instance state; `__new__` matters for metaclasses and for immutable types where you need to control creation.

---

## Class vs instance attributes

```python
class Counter:
    count = 0                       # class attribute (shared)

    def __init__(self):
        Counter.count += 1
        self.id = Counter.count     # instance attribute (per object)

a = Counter()
b = Counter()
Counter.count                       # 2
a.id                                # 1
b.id                                # 2
```

When you write `self.count = x`, you create a new **instance attribute** that shadows the class attribute on this instance only — the class attribute is unchanged. Mutating a class-level mutable (e.g., `self.shared.append(x)` where `shared` is a class attribute) is a classic bug because every instance shares the same list.

---

## Methods

### Instance methods

The standard form: receive the instance as `self`, can read and write instance state.

### Class methods

Receive the class as `cls` (not the instance). The canonical use case is **alternate constructors** — factory methods that build an instance from a different input shape:

```python
class Date:
    def __init__(self, year, month, day):
        self.year, self.month, self.day = year, month, day

    @classmethod
    def from_string(cls, s):
        y, m, d = map(int, s.split('-'))
        return cls(y, m, d)         # using cls means subclasses get their own type back

d = Date.from_string("2024-01-15")
```

Using `cls(...)` instead of `Date(...)` makes the factory work correctly in subclasses: a subclass's `from_string` produces a subclass instance.

### Static methods

No `self`, no `cls`. Logically grouped under the class but neither read nor write class or instance state. They're glorified module functions, made accessible through the class namespace:

```python
class MathUtils:
    @staticmethod
    def clamp(value, lo, hi):
        return max(lo, min(value, hi))

MathUtils.clamp(15, 0, 10)          # 10
```

If you find yourself with many static methods, consider whether a plain module wouldn't be a better home.

### Property

`@property` turns a method into a computed attribute, callable without `()`. Use it for read-only views, lazy computations, and validation on assignment:

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
c.radius            # 5  — calls the getter
c.radius = 10       # calls the setter (validated)
c.area              # 314.15... — computed on access
```

For values you compute once per instance and want to cache, use `functools.cached_property` instead — same syntax, value memoised on first access.

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
    print(animal.speak())           # polymorphic dispatch
```

### `super`

`super()` returns a proxy that delegates to the parent class. It is essential in `__init__` to initialise inherited state:

```python
class GuideDog(Dog):
    def __init__(self, name, owner):
        super().__init__(name)      # call Dog.__init__
        self.owner = owner
```

**Always call `super().__init__()`** unless you have a specific reason not to. Skipping it leaves parent state uninitialised, which produces subtle bugs that surface much later.

### Multiple inheritance and the MRO

Python supports multiple inheritance. The order in which methods are looked up across the bases is the **Method Resolution Order**, computed by the C3 linearisation algorithm. You rarely need to reason about C3 in detail; you can always inspect the MRO directly:

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

D.__mro__       # (D, B, C, A, object)
```

`super()` follows the MRO — it calls the next class in the linearisation, which may not be the direct parent. This is what makes **cooperative multiple inheritance** possible: every `__init__` in the chain can call `super().__init__()` and the resulting traversal visits each parent once, in a consistent order.

---

## Dunder (magic) methods

Define how instances respond to built-in operations. Choose the right ones and your custom class becomes indistinguishable from a built-in.

| Method | Triggered by |
|---|---|
| `__init__(self, ...)` | `ClassName(...)` |
| `__repr__(self)` | `repr(obj)`, debugging, REPL |
| `__str__(self)` | `str(obj)`, `print(obj)` |
| `__len__(self)` | `len(obj)` |
| `__getitem__(self, key)` | `obj[key]` |
| `__setitem__(self, key, val)` | `obj[key] = val` |
| `__contains__(self, item)` | `item in obj` |
| `__iter__(self)` | `for x in obj`, `iter(obj)` |
| `__next__(self)` | `next(obj)` |
| `__eq__(self, other)` | `obj == other` |
| `__lt__(self, other)` | `obj < other` |
| `__hash__(self)` | `hash(obj)`, use as dict key or set element |
| `__call__(self, ...)` | `obj(...)` — instance becomes callable |
| `__enter__` / `__exit__` | `with obj:` |
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

    def __hash__(self):                 # required if __eq__ is defined and you want hashing
        return hash((self.x, self.y))

v1 + v2                                 # calls __add__
```

**Important contract**: if you define `__eq__`, Python automatically sets `__hash__` to `None`, making instances unhashable. If you want the object to live in a set or be used as a dict key, you must explicitly define `__hash__`. The hash must be consistent with equality: equal objects must hash the same.

---

## Abstract base classes

Force subclasses to implement specific methods. Useful for declaring interfaces:

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

class Rectangle(Shape):
    def __init__(self, w, h):
        self.w, self.h = w, h
    def area(self):
        return self.w * self.h
    def perimeter(self):
        return 2 * (self.w + self.h)

Shape()                 # TypeError — cannot instantiate an abstract class
Rectangle(3, 4).area()  # 12
```

Abstract classes can include concrete methods alongside abstract ones, allowing partial implementation that subclasses extend.

---

## Dataclasses

`@dataclass` auto-generates `__init__`, `__repr__`, and `__eq__` from type-annotated fields. Use it as the default for plain data containers — every line of class body that just initialises a field is now redundant.

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float
    z: float = 0.0                              # default value

@dataclass(frozen=True)                         # immutable; also makes it hashable
class Config:
    host: str
    port: int = 8080

@dataclass
class Inventory:
    items: list = field(default_factory=list)   # mutable default — use field()

p = Point(1.0, 2.0)
p.x                     # 1.0
repr(p)                 # 'Point(x=1.0, y=2.0, z=0.0)'
```

`field(default_factory=list)` is the dataclass equivalent of the None-sentinel pattern for mutable defaults: each instance gets a fresh list, never sharing state. Use it for any mutable default in a dataclass.

`frozen=True` makes the dataclass immutable (assignment raises) and automatically hashable, perfect for cache keys and configuration objects. Use `eq=False` to opt out of automatic `__eq__`, `order=True` to add comparison operators (`<`, `<=`, etc.), `slots=True` (3.10+) to skip the per-instance `__dict__` for memory savings.

---

## Encapsulation conventions

Python has no enforced access control. The community uses naming conventions:

| Name | Convention | Meaning |
|---|---|---|
| `attribute` | Public | Part of the public API |
| `_attribute` | Protected | Internal; not for external use, but accessible if needed |
| `__attribute` | Private (name-mangled) | Triggers name mangling to `_ClassName__attribute`, avoids accidental override in subclasses |

Name mangling is rarely needed in application code. Use `_prefix` for internals and document the public API. Strong encapsulation is achieved through clear documentation and review, not through language-level enforcement.

---

## OOP design principles (reference)

| Principle | Meaning |
|---|---|
| **Single Responsibility** | A class should have one reason to change |
| **Open / Closed** | Open for extension (subclassing, composition), closed for modification |
| **Liskov Substitution** | Subclass instances must be usable wherever the parent is expected |
| **Interface Segregation** | Many small specific interfaces over one large general one |
| **Dependency Inversion** | Depend on abstractions (ABCs), not on concrete implementations |
| **Composition over Inheritance** | Prefer building with small, single-purpose objects rather than deep class hierarchies |

These are guidelines, not laws — favour the principle that improves the specific design at hand.

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| `__init__` without `super().__init__()` | Parent state uninitialised, mysterious failures later | Always call `super().__init__()` in subclasses |
| `__eq__` defined, hash broken | Instance is unhashable, can't be in a set or dict | Define `__hash__` explicitly, consistent with `__eq__` |
| Mutable class attribute used as default state | All instances share the same object, mutation leaks | Move to `__init__`, or use `field(default_factory=...)` in dataclass |
| `self.x = x` shadows class attribute | The class attribute is unchanged; tests pass that should fail | Be explicit about which level you're writing to (`Class.x` or `self.x`) |
| Forgetting to use `cls` in `@classmethod` | Subclass factories return parent type | Use `cls(...)`, never `ClassName(...)` |
| `@property` getter raising `AttributeError` | Confusing, looks like the attribute doesn't exist | Catch and re-raise with a clearer message, or fix the underlying issue |
| Diamond inheritance without `super()` | Some `__init__`s never run | Use `super().__init__()` in every class along the chain |
| Calling `obj.method()` where `obj` is a class | `TypeError: missing 1 required positional argument: 'self'` | Bind to an instance first |
| Using `is` to compare custom objects | Returns `False` even for "equal" objects | Use `==` (and define `__eq__` if needed) |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Plain data container | `@dataclass` | Auto boilerplate, type-annotated fields |
| Immutable record / hashable config | `@dataclass(frozen=True)` | No mutation, free hash |
| Alternate constructor | `@classmethod` | Receives `cls`, plays well with subclasses |
| Logically grouped utility | `@staticmethod` | No state needed |
| Computed attribute | `@property` | Looks like an attribute to callers |
| Cached per-instance attribute | `@functools.cached_property` | Lazy, computed once per instance |
| Force subclasses to implement methods | `ABC` + `@abstractmethod` | Interface declaration |
| Enable `obj + other` | Define `__add__` (and friends) | Operator overload |
| Make object iterable | Define `__iter__` (and `__next__` if it's the iterator) | Works in `for`, comprehensions, etc. |
| Use as context manager | Define `__enter__` / `__exit__` | `with obj:` |
| Make instance callable | Define `__call__` | Function-like object with state |
| Memory-tight class | `__slots__` or `@dataclass(slots=True)` | No `__dict__` per instance |

---

## See also

- [01_types_and_variables.md](01_types_and_variables.md) — identity vs equality, mutability, the data model
- [04_functions.md](04_functions.md) — `@property`, `@classmethod`, `@staticmethod`, decorators
- [05_functional_programming.md](05_functional_programming.md) — `functools.cached_property`, `lru_cache` on methods
- [07_exceptions.md](07_exceptions.md) — context managers, custom exception classes
