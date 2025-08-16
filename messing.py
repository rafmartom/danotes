from danotes import *
import importlib

with importlib.resources.files("danotes.filters.builtin").joinpath("helloworld.lua") as path:
    with open(path) as file:
        content = file.read()

print(content)
