class ModuleBase:
  def __init__(self, name):
    self.name = name

  def generateFromText(self, prompt):
    print(self.name + " module generating 3d model from Text")
