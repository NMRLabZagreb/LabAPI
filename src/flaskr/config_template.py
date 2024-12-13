# Flask server configuration file: copy this template, rename it to config.py and fill in the missing data.
# API key used for authorization
# hexadecimal SHA256 hash
API_KEY = ''
# What is this computer's IP or domain?
THIS_PC = '127.0.0.1:5000' # host:port
# Which devices are connected and where? Provide a json-like dictionary {device: {name, description, host, port, mode}}
AVAILABLE_DEVICES = {'KeysightE5080A': {'name': 'Keysight E5080A',
                                        'description': 'VNA analyzer',
                                        'host': '127.0.0.1',
                                        'port': '5000',
                                        'device_present': False},}