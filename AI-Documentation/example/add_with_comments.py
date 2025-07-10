import os


def greet(name: str) -> None:
    """
    Prints a personalized greeting message to the console.

    Args:
        name (str): The name of the person to be greeted. This argument is required and must be a string.

    Returns:
        None: This function does not return any value.

    Notes:
        The greeting message is formatted using an f-string, which allows for easy insertion of the name variable.
    """
    # Print a greeting message to the console, using the provided name
    print(f"Hello, {name}!")  # The f-string is used to insert the name variable into the greeting message


class MyClass:
    def __init__(self):
        """
        Initializes the object with a default value.

        This method sets the initial value of the object to 10.0.

        Args:
            None

        Returns:
            None
        """
        # Set the initial value of the object to 10.0
        self.value = 10.0  # Assign the default value to the object's attribute

    def add(self, x, y):
        """
        Adds two numbers together.

        This method takes two arguments, x and y, and returns their sum.
        It is intended for use in arithmetic operations.

        Args:
            x (int or float): The first number to add.
            y (int or float): The second number to add.

        Returns:
            int or float: The sum of x and y.

        Notes:
            The method does not perform any error checking on the input values.
            It assumes that x and y are valid numbers.
        """
        # The method simply returns the sum of x and y, which is a basic arithmetic operation.
        # The result is calculated using the + operator, which is overloaded for numbers in Python.
        return x + y


if __name__ == "__main__":
    greet("World")
    my_obj = MyClass()
    result = my_obj.add(5, 7)
    print(f"Result: {result}")
