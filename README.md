# LabAPI

Flask WSGI server for remote communication with a laboratory devices.

## Installation

Install **Python 3** and drivers for the laboratory devices you intend to use.

Clone the Git repository:

```bash
git clone http://github.com/ivanjkv/labapi
```
Create a virtual environment and activate it:
```bash
py -m venv ./venv
./venv/bin/activate
```
Install the required Python packages:
```bash
py -m pip install -r requirements.txt
```
#### Development
Navigate to the src directory and start the Flask server:
```bash
py -m flask --app flaskr run [--debug] [--host 0.0.0.0] [--port 80]
```
The Swagger UI, displaying all available API endpoints, should now be accessible at [http://localhost:5000/swagger](http://localhost:5000/swagger).

If you want to add or edit a device, refer to the next section.

## Adding New Devices

Adding a new device is a time-consuming process, but it is crucial not to skip any steps. Completing the entire procedure ensures smoother testing, debugging, and overall efficiency.

Every device requires five important files:
- A VISA communication module, `py[device_name].py`, located in `modules`, containing a single class `DeviceName()`. Each class method handles a **single** VISA query.
- A unit test file, `test[device_name].py`, located in `tests`, with one or multiple tests. This file ensures smooth VISA communication and helps identify potential exceptions caused by faulty VISA queries.
- A Pyvisa-sim-compatible `[device_name].yaml` file located in `modules/pyvisa-sim`. Refer to [Pyvisa-sim documentation](https://pyvisa.readthedocs.io/projects/pyvisa-sim/en/latest/definitions.html) and [default.yaml](https://github.com/pyvisa/pyvisa-sim/blob/main/pyvisa_sim/default.yaml) for examples. The Pyvisa-sim library is used for mock VISA communication, allowing testing without a physical device.
- A local Flask blueprint located in `flaskr/blueprints`. This file routes API calls to `DeviceName()` class methods defined in the VISA communication module.
- A Swagger `[device_name].yaml` file located in `static/swagger`. This file defines parameters and responses for each API call.

In addition to these files, each new device must also be:
- Added to `modules/config.ini` to store the VISA resource address and/or other device properties.
- Added to `modules/pyvisa-sim.yaml` to associate the VISA resource address with the corresponding mock device.
- Added to `flaskr/config.py` so Flask can route API calls correctly.