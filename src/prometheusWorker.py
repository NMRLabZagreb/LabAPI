from prometheus_client import Gauge, Enum
import os
import json
import time

class PrometheusWorker:
    """ Class wraps all calls to local device method which then update respective Prometheus metrics """
    def __init__(self, app):
        # Load device configuration: metrics, labels, class methods, update intervals...
        path = os.path.dirname(__file__)
        with open(f'{path}/prometheus_config.json') as json_file:
            device_configuration = json.load(json_file)

        # Define worker class arguments
        self.is_running = True
        self.list_of_update_calls = []

        for device, list_of_metrics in device_configuration.items():
            # For each device check whether it is local (class methods are called directly)
            if device in app.local_devices.keys():
                # Iterate through all metrics
                for metric in list_of_metrics:
                    if metric['type'] == "gauge":
                        gauge = Gauge(metric['name'],
                                      metric['description'],
                                      metric['label_names'])
                        
                        # Define update method - local device class method
                        update_method = getattr(app.local_devices[device], metric['method'])

                        # Label values represent different parameters with which update method can be called
                        if len(metric['label_values']):
                            for label_value in metric['label_values']:
                                update_method_parameters = {name: value for name, value in zip(metric['label_names'],
                                                                                               label_value)}
                                update_metric = gauge.labels(*label_value).set
                                # Add a method call to the list
                                self.list_of_update_calls.append([update_metric,
                                                                  update_method,
                                                                  update_method_parameters,
                                                                  metric['update_interval'],
                                                                  0])
                        # Handle single label (no label)
                        else:
                            self.list_of_update_calls.append([gauge.set,
                                                              update_method,
                                                              {},
                                                              metric['update_interval'],
                                                              0])
                                                              
                    # Enum metric follows the same pattern
                    elif metric['type'] == "enum":
                        enum = Enum(metric['name'],
                                    metric['description'],
                                    metric['label_names'],
                                    states=metric['states'])
                        if len(metric['label_values']):
                            for label_value in metric['label_values']:
                                    update_method_parameters = {name: value for name, value in zip(metric['label_names'],
                                                                                                   label_value)}
                                    update_metric = enum.labels(*label_value).state
                                    self.list_of_update_calls.append([update_metric,
                                                                      update_method,
                                                                      update_method_parameters,
                                                                      metric['update_interval'],
                                                                      0])
                        # Handle single label (no label)
                        else:
                            self.list_of_update_calls.append([gauge.set,
                                                              update_method,
                                                              {},
                                                              metric['update_interval'],
                                                              0])
    def run(self):
        # Run all update calls periodically (fastest update interval = 5 seconds)
        while self.is_running:
            for i, (update_metric, update_method, update_method_parameters, update_interval, next_update) in enumerate(self.list_of_update_calls):
                if next_update < time.time():
                    update_metric(update_method(**update_method_parameters))
                    self.list_of_update_calls[i][4] = time.time() + update_interval
            time.sleep(5)
