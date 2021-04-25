
# Gen.IO Simulator

Using CARLA to build a simulator.

## Files

1.  `objects_on_vehicles.py`: test version of demo, spawning objects on top of vehicles in the scene

2.  `demo.py`: main demo file, currently demo NLP weather

3.  `WorldManager.py`: manages world conditions

4.  `sensors.py`: manages sensors

  

## How to install:

Do the entire CARLA install process:
Windows https://carla.readthedocs.io/en/latest/build_windows/

Navigate to carla/PythonAPI

`git clone https://github.com/adamchang2000/GenIO`

Run the Python scripts while the simulator is running within Unreal Engine (launch the simulator using `make launch` then pressing play inside UE4).


## Usage:

1. `objects_on_vehicles.py --query_object <object>`, example object: trashbag, cone, pot

2. `demo.py <weather description>`, example weather description: raining at dawn