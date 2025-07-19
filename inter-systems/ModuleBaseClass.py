class ModuleBase:
  def __init__(self, name):
    self.name = name

  def generate(self, params):
    print(self.name + " module generating 3d model from Text")
