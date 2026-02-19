from dtekwaveshare.config import load_project_config
from dtekwaveshare.router import OutputRouter


config = load_project_config("config/devices.sample.json")
router = OutputRouter.from_config(config)

print("Mapped outputs:", router.mapped_outputs())
print("Current snapshot:", router.snapshot())

# Experiment: toggle output 1
# router.toggle_output(1)
