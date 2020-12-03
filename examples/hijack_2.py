import glob
import os
import sys
import time

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

actor_list = []

try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    client.start_recorder(
        'C:\\Users\\nicch\\Desktop\\CARLA Fun\\CARLA_0.9.10.1\\WindowsNoEditor\\PythonAPI\\recordings\\hijack.log')

    world = client.get_world()
    spawn_points = world.get_map().get_spawn_points()

    police_spawnpoint = spawn_points[2]

    suspect_spawnpoint = carla.Transform(carla.Location(x=police_spawnpoint.location.x + 9, y=police_spawnpoint.location.y,
                                                        z=police_spawnpoint.location.z), carla.Rotation(yaw=police_spawnpoint.rotation.yaw))

    hijacked_spawnpoint = carla.Transform(carla.Location(x=police_spawnpoint.location.x - 20, y=police_spawnpoint.location.y + 3.5,
                                                         z=police_spawnpoint.location.z), carla.Rotation(yaw=police_spawnpoint.rotation.yaw))

    suspect_blueprint = world.get_blueprint_library().filter(
        'vehicle.tesla.model3')[0]
    police_blueprint = world.get_blueprint_library().filter(
        'vehicle.dodge_charger.police')[0]
    hijack_blueprint = world.get_blueprint_library().filter(
        'vehicle.tesla.cybertruck')[0]

    suspect_vehicle = world.spawn_actor(suspect_blueprint, suspect_spawnpoint)
    police_vehicle = world.spawn_actor(police_blueprint, police_spawnpoint)
    hijack_vehicle = world.spawn_actor(hijack_blueprint, hijacked_spawnpoint)

    actor_list.append(suspect_vehicle)
    actor_list.append(police_vehicle)
    actor_list.append(hijack_vehicle)

    suspect_vehicle.apply_control(
        carla.VehicleControl(throttle=0.35, steer=0.0))

    police_vehicle.apply_control(
        carla.VehicleControl(throttle=0.4, steer=0.0))

    hijack_vehicle.apply_control(
        carla.VehicleControl(throttle=0.44, steer=0.0))

    time.sleep(5.25)

    hijack_vehicle.apply_control(
        carla.VehicleControl(throttle=0.5, steer=-10.0))

    time.sleep(0.5)

    police_vehicle.apply_control(
        carla.VehicleControl(throttle=0.0, steer=0.0))

    hijack_vehicle.apply_control(
        carla.VehicleControl(throttle=0.0, steer=0.0))

    time.sleep(0.25)

    suspect_vehicle.apply_control(
        carla.VehicleControl(throttle=0.7, steer=0.0))

    time.sleep(2.5)

    suspect_vehicle.apply_control(carla.VehicleControl(steer=0.5))

    time.sleep(0.3)

    suspect_vehicle.apply_control(carla.VehicleControl(throttle=0.7, steer=0))

    time.sleep(7)

    client.stop_recorder()
finally:
    print('destroying actors')

    for actor in actor_list:
        actor.destroy()

    print('done.')
