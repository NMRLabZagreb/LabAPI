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
py -m venv .venv
.venv/bin/activate
```
Install the required Python packages:
```bash
py -m pip install -r requirements.txt
```

Navigate to the src directory, copy `config_template.py` file and rename it to `config.py`. Edit configuration parameters in the file.

#### Development
Start the Flask server:
```bash
py -m flask --app flaskr run [--debug] [--host 0.0.0.0] [--port 5000]
```
The Swagger UI, displaying all available API endpoints, should now be accessible at [http://localhost:5000/swagger](http://localhost:5000/swagger).

If you want to add or edit a device, refer to the next section.

#### Production

- *Setup and Configuration*

This setup utilizes **Waitress** as the WSGI server and **nginx** as the reverse proxy (with SSL, since Waitress does not natively support it).

To install Waitress, first activate your virtual environment:

```bash
.venv/bin/activate
```

Then, install the Waitress package:

```bash
py -m pip install waitress
```
Next, download and extract **nginx** to your preferred location (e.g., C:/nginx/). Configure the nginx setup by editing the `nginx.conf` file located at `C:/nginx/conf/nginx.conf`. For reference, consult: [Setting Up a Simple Proxy Server](https://nginx.org/en/docs/beginners_guide.html#proxy). The proxy server should point to[http://localhost:5000/](http://localhost:5000/), where Waitress is serving the application.

- *Optional: Setting Up SSL Encryption*

Create a folder to store your certificates. We recommend using `C:/nginx/conf/cert/` for easier setup. Ensure your `nginx.conf` file points to this directory for simplified verification.

Download and extract the [**win-acme**](https://www.win-acme.com/) client. Navigate to the folder containing the extracted files and run `wacs.exe`. Follow these steps to generate the necessary certificates:

    - M: Create certificate (full options)
    - 2: Manual input
    Enter host name
    - 4: Single certificate
    - 1: Save verification files on (network) path
    Enter path - C:/nginx/conf/cert/ (or the path specified in your `nginx.conf` file)
    - 2: RSA key
    - 2: PEM encoded files (Apache, nginx, etc.)
    Enter folder - C:/nginx/conf/cert/ (or your preferred location for saving .pem certificate files)
    - 1: None
    - 5: No (additional) store steps
    - 3: No (additional) installation steps

Once the certificates are generated, they will be saved in `C:/nginx/conf/cert`. 

Update your `nginx.conf` to listen on port 443 (SSL) and redirect all HTTP (port 80) traffic to HTTPS. For more details, refer to the [Configuring HTTPS servers](https://nginx.org/en/docs/http/configuring_https_servers.html) documentation.

- *Running the Server on Windows Startup*

To have the server run on startup, open the Windows Startup folder by pressing `Win + R`, typing `shell:startup`, and pressing `Enter`.

Copy the `labapi_template.bat` file into the Startup folder and rename it to `labapi.bat` (optional). Open the file and update it to reference the paths to your **LabAPI** and **nginx** directories.

Finally, manually run `labapi.bat` to verify that your setup is functioning as expected.

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