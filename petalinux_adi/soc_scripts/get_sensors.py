#! /usr/bin/env python

import os
import time
import socket
import argparse

SENSOR_PATH = "/sys/bus/iio/devices/iio:device0"

def read_file_as_float(fname):
    with open(fname) as fh:
        raw = fh.read()
        try:
            v = float(raw)
        except ValueError:
            print("Failed to interpret %s contents (%s) as int" % (fname, raw))
            v = None
    return v

def get_sensors():
    sensor_files = os.listdir(SENSOR_PATH)
    # Sensors have names of form: in_<sensor_name>_[raw|offset|scale]
    # Sensor names may contain underscores.
    sensors_done = {}
    for f in sensor_files:
        f_split = f.split("_")
        # Skip non-sensor files
        if f_split[0] != "in":
            continue
        # Skip non-sensor files
        if len(f_split) < 3:
            continue
        else:
            # The name of the sensor with the trailing _raw / _offset / _scale removed
            sensor_basename = "_".join(f_split[0:-1])
            # Skip done sensors
            if sensor_basename in sensors_done:
                continue
            # Check all three filenames exist
            f_offset = sensor_basename+"_offset"
            f_raw    = sensor_basename+"_raw"
            f_scale  = sensor_basename+"_scale"

            if f_raw not in sensor_files:
                print("%s missing raw" % sensor_basename)
                continue
            if f_scale not in sensor_files:
                print("%s missing scale" % sensor_basename)
                continue

            if f_offset not in sensor_files:
                offset = 0
            else:
                offset = read_file_as_float(os.path.join(SENSOR_PATH, f_offset))
            raw = read_file_as_float(os.path.join(SENSOR_PATH, f_raw))
            scale = read_file_as_float(os.path.join(SENSOR_PATH, f_scale))
            if (raw is None) or (offset is None) or (scale is None):
                continue
            value = scale * (raw + offset) / 1000.
            sensor_name = sensor_basename.split("_", 2)[2] # strip in_voltage / in_temp
            sensors_done[sensor_name] = value
    sensors_done['timestamp'] = time.time()
    return sensors_done

def main():
    parser = argparse.ArgumentParser(description='Poll Voltage / Temperature sensors and optionally push to redis',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-r', dest='redishost', default=None,
                        help ='Hostname of redis server. If none is provided, sensor values are printed to stdout')
    args = parser.parse_args()
    sensors = get_sensors()
    if args.redishost is None:
        for s, v in sorted(sensors.items()):
            print("%15s: %.3f" % (s, v))
    else:
        try:
            import redis
        except ImportError:
            print("Failed to import redis. Is the `redis` library installed?")
            exit()
        try:
            r = redis.Redis(args.redishost)
        except:
            print("Failed to connect to redis server %s" % args.redishost)
            exit()
        hostname = socket.gethostname().split(".")[0]
        keyname = hostname + "_sensors"
        try:
            r.hmset(keyname, sensors)
        except ConnectionError:
            print("Failed to write sensor key to %s" % args.redishost)

if __name__ == "__main__":
    main()

