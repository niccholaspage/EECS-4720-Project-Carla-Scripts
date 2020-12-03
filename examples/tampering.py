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
import random

actor_list = []

# vehicle list:
# vehicle.citroen.c3
# vehicle.chevrolet.impala
# vehicle.audi.a2
# vehicle.nissan.micra
# vehicle.carlamotors.carlacola
# vehicle.audi.tt
# vehicle.bmw.grandtourer
# vehicle.harley-davidson.low_rider
# vehicle.bmw.isetta
# vehicle.dodge_charger.police
# vehicle.jeep.wrangler_rubicon
# vehicle.mercedes-benz.coupe
# vehicle.mini.cooperst
# vehicle.nissan.patrol
# vehicle.seat.leon
# vehicle.toyota.prius
# vehicle.yamaha.yzf
# vehicle.kawasaki.ninja
# vehicle.bh.crossbike
# vehicle.tesla.model3
# vehicle.gazelle.omafiets
# vehicle.tesla.cybertruck
# vehicle.diamondback.century
# vehicle.audi.etron
# vehicle.volkswagen.t2
# vehicle.lincoln.mkz2017
# vehicle.mustang.mustang

next_vehicle_types = ['vehicle.audi.tt', 'vehicle.tesla.model3',
                      'vehicle.toyota.prius', 'vehicle.mustang.mustang'] * 2

SpawnActor = carla.command.SpawnActor
SetAutopilot = carla.command.SetAutopilot
FutureActor = carla.command.FutureActor
ApplyVehicleControl = carla.command.ApplyVehicleControl


def spawn_car(world, spawn_point):
    global next_vehicle_types
    global actor_list

    vehicle_blueprint = world.get_blueprint_library().filter(
        next_vehicle_types[0])[0]

    next_vehicle_types = next_vehicle_types[1:]

    random_color = random.choice(
        vehicle_blueprint.get_attribute('color').recommended_values)

    vehicle_blueprint.set_attribute('color', random_color)

    for response in client.apply_batch_sync([SpawnActor(vehicle_blueprint, spawn_point).then(SetAutopilot(FutureActor, True))]):
        if response.error:
            print(response.error)
        else:
            actor_list.append(response.actor_id)


try:
    client = carla.Client('localhost', 2000)

    client.set_timeout(10.0)

    client.start_recorder(
        'C:\\Users\\nicch\\Desktop\\CARLA Fun\\CARLA_0.9.10.1\\WindowsNoEditor\\PythonAPI\\recordings\\tampering.log')

    world = client.get_world()

    traffic_manager = client.get_trafficmanager(
        8000)  # Traffic Manager Port

    traffic_manager.set_global_distance_to_leading_vehicle(1.0)

    spawn_points = world.get_map().get_spawn_points()

    left_lane_spawnpoint = spawn_points[3]

    right_lane_spawnpoint = carla.Transform(carla.Location(x=left_lane_spawnpoint.location.x - 5, y=left_lane_spawnpoint.location.y + 3.5,
                                                           z=left_lane_spawnpoint.location.z), carla.Rotation(yaw=left_lane_spawnpoint.rotation.yaw))

    for i in range(4):
        spawn_car(world, left_lane_spawnpoint)

        left_lane_spawnpoint = carla.Transform(carla.Location(x=left_lane_spawnpoint.location.x + 7, y=left_lane_spawnpoint.location.y,
                                                              z=left_lane_spawnpoint.location.z), carla.Rotation(yaw=left_lane_spawnpoint.rotation.yaw))

    for i in range(4):
        spawned_car = spawn_car(world, right_lane_spawnpoint)

        if i == 2:
            marked_car = spawned_car

        right_lane_spawnpoint = carla.Transform(carla.Location(x=right_lane_spawnpoint.location.x + 7, y=right_lane_spawnpoint.location.y,
                                                               z=right_lane_spawnpoint.location.z), carla.Rotation(yaw=right_lane_spawnpoint.rotation.yaw))

    time.sleep(5)

    danger_car = world.get_actor(actor_list[2])
    traffic_manager.ignore_lights_percentage(danger_car, 100)
    traffic_manager.ignore_vehicles_percentage(danger_car, 100)
    traffic_manager.distance_to_leading_vehicle(danger_car, 0)
    traffic_manager.vehicle_percentage_speed_difference(danger_car, -100)

    print('danger danger danger!')

    time.sleep(1.20)

    car_ahead = world.get_actor(actor_list[3])

    danger_transform = danger_car.get_transform()
    car_ahead_transform = car_ahead.get_transform()

    while True:
        world.wait_for_tick()

        car_ahead.set_transform(car_ahead_transform)
        danger_car.set_transform(danger_transform)
except Exception as e:
    print('Exception:')

    print(e)
finally:
    client.stop_recorder()

    print('destroying actors')

    actors = client.get_world().get_actors(actor_list)

    for actor in actors:
        actor.destroy()

    print('done.')
