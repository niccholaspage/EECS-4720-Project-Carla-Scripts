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

SpawnActor = carla.command.SpawnActor
SetAutopilot = carla.command.SetAutopilot
FutureActor = carla.command.FutureActor
ApplyVehicleControl = carla.command.ApplyVehicleControl

actor_list = []

vehicle_blueprint_names = [
    # "vehicle.citroen.c3",
    # "vehicle.chevrolet.impala",
    # "vehicle.audi.a2",
    # "vehicle.nissan.micra",
    # "vehicle.carlamotors.carlacola",
    # "vehicle.audi.tt",
    # "vehicle.bmw.grandtourer",
    # "vehicle.bmw.isetta",
    # "vehicle.dodge_charger.police",
    # "vehicle.jeep.wrangler_rubicon",
    # "vehicle.mercedes-benz.coupe",
    # "vehicle.mini.cooperst",
    # "vehicle.nissan.patrol",
    # "vehicle.seat.leon",
    # "vehicle.toyota.prius",
    "vehicle.tesla.model3",
    # "vehicle.audi.etron",
    # "vehicle.volkswagen.t2",
    # "vehicle.lincoln.mkz2017",
    # "vehicle.mustang.mustang",
]


def spawn_cars(world, spawn_point):
    global actor_list

    batch = []

    forward_spawnpoint = spawn_point
    back_spawnpoint = carla.Transform(carla.Location(x=forward_spawnpoint.location.x - 5.5, y=forward_spawnpoint.location.y,
                                                     z=forward_spawnpoint.location.z), carla.Rotation(yaw=forward_spawnpoint.rotation.yaw))

    for i in range(7):
        vehicle_blueprint = world.get_blueprint_library().filter(
            random.choice(vehicle_blueprint_names))[0]

        color = random.choice(
            vehicle_blueprint.get_attribute('color').recommended_values)
        vehicle_blueprint.set_attribute('color', color)

        if i % 2 == 0:
            this_spawnpoint = forward_spawnpoint
            forward_spawnpoint = carla.Transform(carla.Location(x=forward_spawnpoint.location.x + 5.5, y=forward_spawnpoint.location.y,
                                                                z=forward_spawnpoint.location.z), carla.Rotation(yaw=forward_spawnpoint.rotation.yaw))
        else:
            this_spawnpoint = back_spawnpoint
            back_spawnpoint = carla.Transform(carla.Location(x=back_spawnpoint.location.x - 5.5, y=back_spawnpoint.location.y,
                                                             z=back_spawnpoint.location.z), carla.Rotation(yaw=back_spawnpoint.rotation.yaw))

        batch += [
            SpawnActor(vehicle_blueprint, this_spawnpoint)
            # .then(SetAutopilot(FutureActor, False))
        ]

    responses = client.apply_batch_sync(batch)
    for response in responses:
        if response.error:
            print(response.error)
        else:
            actor_list.append(response.actor_id)


def stop_all_cars():
    batch = []

    for actor_id in actor_list:
        batch += [ApplyVehicleControl(actor_id,
                                      carla.VehicleControl(throttle=0.0))]

    client.apply_batch_sync(batch)


def move_all_cars():
    batch = []

    for actor_id in actor_list:
        batch += [ApplyVehicleControl(actor_id,
                                      carla.VehicleControl(throttle=0.4))]

    client.apply_batch_sync(batch)


try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    client.start_recorder('C:\\Users\\nicch\\Desktop\\CARLA Fun\\CARLA_0.9.10.1\\WindowsNoEditor\\PythonAPI\\recordings\\emp.log')

    world = client.get_world()
    # debug = world.debug
    # world_snapshot = world.get_snapshot()

    # for actor_snapshot in world_snapshot:
    #     actual_actor = world.get_actor(actor_snapshot.id)
    #     if actual_actor.type_id == 'traffic.traffic_light':
    #         debug.draw_box(carla.BoundingBox(actor_snapshot.get_transform().location,carla.Vector3D(0.5,0.5,2)),actor_snapshot.get_transform().rotation, 0.05, carla.Color(255,0,0,0),0)

    client.get_trafficmanager().reset_traffic_lights()

    time.sleep(2)

    spawn_points = world.get_map().get_spawn_points()

    spawn_cars(world, spawn_points[51])
    spawn_cars(world, spawn_points[52])
    spawn_cars(world, spawn_points[74])
    spawn_cars(world, spawn_points[75])

    time.sleep(2)

    move_all_cars()

    time.sleep(6.5)

    stop_all_cars()

    time.sleep(10)

    client.stop_recorder()
finally:
    print('destroying actors')

    actors = client.get_world().get_actors(actor_list)

    for actor in actors:
        actor.destroy()

    print('done.')
