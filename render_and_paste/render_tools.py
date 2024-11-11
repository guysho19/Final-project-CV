import blenderproc as bproc
from blenderproc.python.camera import CameraUtility
import bpy
import numpy as np
import argparse
import json
import random
import os

def filter_annotations_by_category(data, valid_category_ids):
    filtered_data = {
        'category_id_segmaps': [],
        'instance_segmaps': [],
        'instance_attribute_maps': [],
        'colors': []
    }

    for idx, (seg_map, instance_map, attrs) in enumerate(zip(data['category_id_segmaps'], data['instance_segmaps'], data['instance_attribute_maps'])):
        filtered_data['category_id_segmaps'].append(seg_map)
        filtered_data['instance_segmaps'].append(instance_map)

        # Filter instance attributes by category ID
        filtered_attrs = [attr for attr in attrs if attr['category_id'] in valid_category_ids]
        filtered_data['instance_attribute_maps'].append(filtered_attrs)

        # You can also store the colors if needed
        filtered_data['colors'].append(data['colors'][idx])

    return filtered_data
# Function to load paths from a configuration file
def load_paths_from_config(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)

    needle_holders = config.get("needle_holders", [])
    tweezers = config.get("tweezers", [])
    camera_params = config.get("camera_params", "camera.json")
    output_dir = config.get("output_dir", "")
    num_images = config.get("num_images", 50)

    return needle_holders, tweezers, camera_params, output_dir, num_images


# Argument parser setup
parser = argparse.ArgumentParser()
parser.add_argument('--config', required=True, help="Path to the configuration JSON file.")
args = parser.parse_args()

# Load object paths and parameters from the config file
needle_holders, tweezers, camera_params, output_dir, num_images = load_paths_from_config(args.config)
hand_occlude_path='/home/student/hw2_cv/render_on_hdri/Hand_LowPoly.obj'

# Initialize BlenderProc
bproc.init()

# Set camera intrinsics parameters
with open(camera_params, "r") as file:
    camera_params = json.load(file)

fx = camera_params["fx"]
fy = camera_params["fy"]
cx = camera_params["cx"]
cy = camera_params["cy"]
im_width = camera_params["width"]
im_height = camera_params["height"]
K = np.array([[fx, 0, cx],
              [0, fy, cy],
              [0, 0, 1]])
CameraUtility.set_intrinsics_from_K_matrix(K, im_width, im_height)

# Function to generate images for a specific object path
num_images_per_obj=num_images // (len(needle_holders)+len(tweezers))

poses = 0
instance_id=0
all_objects = needle_holders + tweezers

for obj_path in all_objects:
    # bproc.clean_up(True)  # This will remove all objects from the scene
    for obj_x in bpy.context.scene.objects:
        if obj_x.type == 'MESH':
            bpy.data.objects.remove(obj_x, do_unlink=True)
    obj = bproc.loader.load_obj(obj_path)[0]

    hand_obj = bproc.loader.load_obj(hand_occlude_path)[0]
    hand_obj.set_cp("category_id", 10)
    new_scale = hand_obj.get_scale() * 4
    new_scale[1] = -new_scale[1]
    hand_obj.set_scale(new_scale)
    hand_obj.set_location(obj.get_location() + np.array([0, -0.2, -1.6]))
    # hand_obj.set_location(obj.get_location() + np.random.uniform([-0.4, -0.4, -0.4], [0.4, 0.4, 0.4])+np.array([0,0,-1.2]))
    # Darken hand_obj material
    hand_material = bproc.material.create(name="hand_material")
    # hand_material.set_principled_shader_value("Base Color", (0.1, 0.1, 0.1, 1.0))  # Dark gray color
    # hand_material.set_principled_shader_value("Base Color", (0.3, 0.25, 0.2, 1.0))  # Darkest beige
    hand_material.set_principled_shader_value("Base Color", (0.2, 0.18, 0.16, 1.0))  # Dark gray-beige
    hand_material.set_principled_shader_value("Specular", 0.1)  # Low specular for a matte finish
    hand_material.set_principled_shader_value("Roughness", 0.8)  # High roughness for less shine
    hand_obj.replace_materials(hand_material)

    if obj_path in needle_holders:
        obj.set_cp("category_id", 1)  # Assign the category ID
    else:
        obj.set_cp("category_id", 2)
    new_scale = obj.get_scale() * 1.2
    obj.set_scale(new_scale)
    obj.set_cp("instance_id", instance_id + 1)
    instance_id+=1
    initial_poses = poses
    tries = 0
    bproc.utility.reset_keyframes()

    while tries < 300 and poses - initial_poses < num_images_per_obj:
        # Set random world lighting strength
        #bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = np.random.uniform(0.1, 1.5)
        light = bproc.types.Light()
        light.set_type("POINT")

        if obj_path in tweezers:
            mat=obj.get_materials()[0]
            color_tweezers = random.uniform(0.02, 0.08)  # Random value for red channel
            mat.set_principled_shader_value("Base Color", (color_tweezers, color_tweezers, color_tweezers, 1.0))
            mat.set_principled_shader_value("Roughness", random.uniform(0.5, 1.0))
            mat.set_principled_shader_value("Metallic", random.uniform(0.0, 0.5))

            light.set_location(bproc.sampler.shell(
                center=obj.get_location(),
                radius_min=1,
                radius_max=2,  # Reduced radius for closer, less intense lighting
                elevation_min=10,  # Start at a higher elevation to simulate surgery light
                elevation_max=20
            ))
            light.set_energy(random.uniform(0, 4))  # Lowered energy for a dimmer effect

        else: #than it is needle holder and there are 2 materials - metal and gold
            metal=obj.get_materials()[0]
            gold=obj.get_materials()[1]
            #metal############
            metal.set_principled_shader_value("Specular", random.uniform(0.25, 0.75))
            metal.set_principled_shader_value("Roughness", random.uniform(0.0, 0.8))
            metal.set_principled_shader_value("Metallic", random.uniform(0.5, 1.0))
            # gold############
            gold.set_principled_shader_value("Specular", random.uniform(0.25, 0.75))
            gold.set_principled_shader_value("Roughness", random.uniform(0.0, 0.8))
            gold.set_principled_shader_value("Metallic", random.uniform(0.5, 1.0))  # Assuming metallic should be high

            light.set_location(bproc.sampler.shell(
                center=obj.get_location(),
                radius_min=1,
                radius_max=3,
                elevation_min=10,
                elevation_max=50
            ))
            light.set_energy(random.uniform(4, 14))  # Lowered energy for a dimmer effect

        # Sample random camera location
        location = bproc.sampler.shell(
            center=obj.get_location(),
            radius_min=10,
            radius_max=38,
            elevation_min=-90,
            elevation_max=90
        )
        lookat_point = obj.get_location() + np.random.uniform([-0.3, -0.3, -0.3], [0.3, 0.3, 0.3])
        rotation_matrix = bproc.camera.rotation_from_forward_vec(lookat_point - location,
                                                                 inplane_rot=np.pi + np.random.uniform(-0.3, 0.3))
        cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)

        # Add camera pose if the selected object is visible
        if obj in bproc.camera.visible_objects(cam2world_matrix):
            bproc.camera.add_camera_pose(cam2world_matrix)
            poses += 1

        tries += 1


    # Rendering settings
    bproc.renderer.set_max_amount_of_samples(100)  # Speed up rendering
    bproc.renderer.set_output_format(enable_transparency=True)  # Enable transparency
    bproc.renderer.enable_segmentation_output(map_by=["category_id", "instance", "name"])  # Enable segmentation masks


    valid_category_ids = [1,2]  # Keep only these IDs, excluding occluders or any unwanted IDs
    # Render RGB images
    data = bproc.renderer.render()
    # Filter out annotations with unwanted category IDs
    filtered_data = filter_annotations_by_category(data, valid_category_ids)

    # Write the filtered data to COCO file
    bproc.writer.write_coco_annotations(
        os.path.join(output_dir, 'coco_data'),
        instance_segmaps=filtered_data["instance_segmaps"],
        instance_attribute_maps=filtered_data["instance_attribute_maps"],
        colors=filtered_data["colors"],
        mask_encoding_format="polygon",
        append_to_existing_output=True
    )
    bproc.utility.reset_keyframes()

