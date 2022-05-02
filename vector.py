from dataclasses import dataclass
import math

@dataclass
class Vec2:
    x: float
    y: float

    def __add__(self, other):
        return Vec2(self.x+other.x, self.y+other.y)

    def __mul__(self, other):
        return Vec2(self.x*other.x, self.y*other.y)

    def __sub__(self, other):
        return Vec2(self.x-other.x, self.y-other.y)

    def s_mul(self, scalar):
        return Vec2(self.x*scalar, self.y*scalar)

    def dot(self, other) -> float:
        return self.x*other.x + self.y*other.y

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def __truediv__(self, other):
        return Vec2(self.x/other.x, self.y/other.y)

    def s_div(self, scalar):
        return Vec2(self.x/scalar, self.y/scalar)

    def normalize(self, magnitude: float = 1) -> None:
        relative_magnitude = magnitude/self.magnitude()
        self.x *= relative_magnitude
        self.y *= relative_magnitude

    def __getitem__(self, item):
        if item < 2:
            return [self.x, self.y][item]
        else:
            raise StopIteration

    # def __iter__(self):
    #     self.n = 0
    #     return self

    # def __next__(self):
    #     if self.n < 2:
    #         if self.n == 0:
    #             self.n += 1
    #             return self.x
    #         self.n += 1
    #         return self.y
    #     raise StopIteration

@dataclass
class Trajectory:
    points: list[Vec2]
    time_taken: float
    height: float
    velocity: Vec2

def main():
    a = Vec2(100, 200)
    b = Vec2(50, 300)
    print(a + b, a * b, a - b, a/b)
    print(a.dot(b))


if __name__ == "__main__":
    main()