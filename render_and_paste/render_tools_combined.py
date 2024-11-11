import blenderproc as bproc
from blenderproc.python.camera import CameraUtility
import bpy
import numpy as np
import argparse
import json
import random
import os
import glob
from itertools import product


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
num_images_per_obj=num_images // (len(tweezers)*len(needle_holders))

poses = 0
instance_id=0
all_objects = list(product(needle_holders, tweezers))

for obj_paths in all_objects:
    # bproc.clean_up(True)  # This will remove all objects from the scene
    for obj_x in bpy.context.scene.objects:
        if obj_x.type == 'MESH':
            bpy.data.objects.remove(obj_x, do_unlink=True)

    needle_obj = bproc.loader.load_obj(obj_paths[0])[0]
    needle_obj.set_location([2, 0, 0])

    # obj.set_rotation_euler([np.pi/2, 0, 0])
    tweezers_obj = bproc.loader.load_obj(obj_paths[1])[0]
    tweezers_obj.set_location([-2, 0, 0])

    #if random.random()<0.6:
    hand_obj_needle = bproc.loader.load_obj(hand_occlude_path)[0]
    hand_obj_needle.set_cp("category_id", 10)
    new_scale=hand_obj_needle.get_scale() * 4
    new_scale[1]=-new_scale[1]
    hand_obj_needle.set_scale(new_scale)
    hand_obj_needle.set_location(
        needle_obj.get_location() + np.array([0.5, -0.2, -1.2]))
    hand_obj_tweezers = bproc.loader.load_obj(hand_occlude_path)[0]
    hand_obj_tweezers.set_cp("category_id", 10)
    new_scale = hand_obj_tweezers.get_scale() * 4
    new_scale[1] = -new_scale[1]
    hand_obj_tweezers.set_scale(new_scale)
    hand_obj_tweezers.set_location(
        tweezers_obj.get_location() + np.array([0.5, -0.2, -1.4]))

    new_scale = hand_obj_tweezers.get_scale() * 1.2
    hand_obj_tweezers.set_scale([-new_scale[0], new_scale[1], new_scale[2]])
    # current_rotation_hand_tweezers = hand_obj_tweezers.get_rotation_euler()
    # # norm_hand_needle = np.random.normal(0, 0.1)
    # new_rotation_hand_tweezers = [current_rotation_hand_tweezers[0], current_rotation_hand_tweezers[1],
    #                        current_rotation_hand_tweezers[2]]
    # hand_obj_tweezers.set_rotation_euler(new_rotation_hand_tweezers)
    # hand_obj.set_location(obj.get_location() + np.random.uniform([-0.4, -0.4, -0.4], [0.4, 0.4, 0.4])+np.array([0,0,-1.2]))
    # Darken hand_obj material
    hand_material = bproc.material.create(name="hand_material")
    #hand_material.set_principled_shader_value("Base Color", (0.1, 0.1, 0.1, 1.0))  # Dark gray color
    # hand_material.set_principled_shader_value("Base Color", (0.3, 0.25, 0.2, 1.0))  # Darkest beige
    hand_material.set_principled_shader_value("Base Color", (0.2, 0.18, 0.16, 1.0))  # Dark gray-beige
    hand_material.set_principled_shader_value("Specular", 0.1)  # Low specular for a matte finish
    hand_material.set_principled_shader_value("Roughness", 0.8)  # High roughness for less shine
    hand_obj_needle.replace_materials(hand_material)
    hand_obj_tweezers.replace_materials(hand_material)

    current_rotation_needle = needle_obj.get_rotation_euler()
    norm_needle = np.random.normal(0, 0.2)
    new_rotation_needle = [current_rotation_needle[0], current_rotation_needle[1] - np.pi / 4,
                        current_rotation_needle[2]]
    needle_obj.set_cp("category_id", 1)  # Assign the category ID
    needle_obj.set_rotation_euler(new_rotation_needle)

    current_rotation_tweezers = tweezers_obj.get_rotation_euler()
    norm_tweezers = np.random.normal(0, 0.2)
    new_rotation_tweezers = [current_rotation_tweezers[0], current_rotation_tweezers[1] + np.pi / 12,
                        current_rotation_tweezers[2]]
    tweezers_obj.set_cp("category_id", 2)
    hand_obj_tweezers.set_location(
            tweezers_obj.get_location() + np.array([-0.5, -0.2, -1]))

    tweezers_obj.set_rotation_euler(new_rotation_tweezers)
    new_scale = needle_obj.get_scale() * 1.2
    needle_obj.set_scale(new_scale)
    new_scale = tweezers_obj.get_scale() * 1.4
    tweezers_obj.set_scale(new_scale)

    needle_obj.set_cp("instance_id", instance_id + 1)
    instance_id+=1
    tweezers_obj.set_cp("instance_id", instance_id + 1)
    instance_id+=1
    initial_poses = poses
    bproc.utility.reset_keyframes()

    while poses - initial_poses < num_images_per_obj:
        tweezers_current_rotation = tweezers_obj.get_rotation_euler()
        tweezers_norm = np.random.normal(0, 0.2)
        tweezers_new_rotation = [tweezers_current_rotation[0], tweezers_current_rotation[1] + tweezers_norm,
                                 tweezers_current_rotation[2]]
        tweezers_obj.set_rotation_euler(tweezers_new_rotation)

        needle_current_rotation = needle_obj.get_rotation_euler()
        needle_norm = np.random.normal(0, 0.2)
        needle_new_rotation = [needle_current_rotation[0], needle_current_rotation[1] + needle_norm,
                               needle_current_rotation[2]]
        needle_obj.set_rotation_euler(needle_new_rotation)

        light = bproc.types.Light()
        light.set_type("POINT")

        for mat in tweezers_obj.get_materials():
            # Randomly perturbate the material properties
            # mat.set_principled_shader_value("Specular", random.uniform(0.0, 1.0))
            # mat.set_principled_shader_value("Base Color", (0.2, 0.2, 0.2, 1.0))  # Dark gray
            # Set a random dark gray base color for the tweezers
            color_tweezers = random.uniform(0.02, 0.08)  # Random value for red channel

            mat.set_principled_shader_value("Base Color", (color_tweezers, color_tweezers, color_tweezers, 1.0))

            mat.set_principled_shader_value("Roughness", random.uniform(0.5, 1.0))
            mat.set_principled_shader_value("Metallic", random.uniform(0.0, 0.5))

        for mat in needle_obj.get_materials():
            # than it is needle holder and there are 2 materials - metal and gold

            mat.set_principled_shader_value("Specular", random.uniform(0.25, 0.75))
            mat.set_principled_shader_value("Roughness", random.uniform(0.0, 0.8))
            mat.set_principled_shader_value("Metallic", random.uniform(0.5, 1.0))

        light.set_location(bproc.sampler.shell(
            center=0.5*hand_obj_needle.get_location()+0.5*hand_obj_tweezers.get_location(),
            radius_min=1,
            radius_max=15,  # Reduced radius for closer, less intense lighting
            elevation_min=10,  # Start at a higher elevation to simulate surgery light
            elevation_max=20
        ))
        light.set_energy(random.uniform(60, 170))  # Lowered energy for a dimmer effect

        # Define a fixed look-at point (e.g., the object's location)
        location = np.array([0, -20, 0])  # Camera location
        rotation_matrix = bproc.camera.rotation_from_forward_vec(
            np.array([0, 1, 0]),  # Forward vector toward the origin
            inplane_rot=np.pi * random.uniform(0.75, 1)
        )
        cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
        bproc.camera.add_camera_pose(cam2world_matrix)

        # Add camera pose if the selected object is visible
        poses += 1

        # Rendering settings
        bproc.renderer.set_max_amount_of_samples(100)  # Speed up rendering
        bproc.renderer.set_output_format(enable_transparency=True)
        bproc.renderer.enable_segmentation_output(map_by=["category_id", "instance", "name"])  # Enable segmentation masks

        valid_category_ids = [1, 2]  # Keep only these IDs, excluding occluders or any unwanted IDs
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

        tweezers_new_rotation = [tweezers_current_rotation[0], tweezers_current_rotation[1] - tweezers_norm,
                                 tweezers_current_rotation[2]]
        tweezers_obj.set_rotation_euler(tweezers_new_rotation)

        needle_new_rotation = [needle_current_rotation[0], needle_current_rotation[1] - needle_norm,
                               needle_current_rotation[2]]
        needle_obj.set_rotation_euler(needle_new_rotation)

