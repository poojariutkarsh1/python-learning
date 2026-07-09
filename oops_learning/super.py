#this was to teach super() function
class Shape:
    def __init__(self, color, filled):
        self.color = color
        self.filled = filled
        
    def describe(self):
        print(f"It is {self.color} and is {'filled' if self.filled else 'not filled'}")

class Circle(Shape):
    def __init__(self, color, filled, radius):
        super().__init__(color,filled)
        self.radius = radius
        
    def describe(self):
        print(f"it is a circle and has an area of {3.14*self.radius*self.radius} cm")
        super().describe()

class Square(Shape):
    def __init__(self, color, filled, width):
        super().__init__(color,filled)
        self.width = width

class Triangle(Shape):
    def __init__(self, color, filled, width, height):
        super().__init__(color,filled)
        self.radius = width
        self.height = height
        

circle = Circle("Red", False, 5)
circle.describe()
