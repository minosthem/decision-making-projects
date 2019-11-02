from os.path import join, exists
from models.models import Server
import yaml
import os

properties_folder = join(os.getcwd(), "properties")
example_properties_file = join(properties_folder, "example_properties.yaml")
properties_file = join(properties_folder, "properties.yaml")


def load_properties():
    """
    Load yaml file containint program's properties
    :return: the properties dictionary and the output folder path
    """
    file = properties_file if exists(properties_file) else example_properties_file
    with open(file, 'r') as f:
        properties = yaml.safe_load(f)
    return properties


def main():
    properties = load_properties()
    servers = []
    for i in range(properties["servers_num"]):
        server = Server(properties["server_capacity"])
        servers.append(server)


if __name__ == '__main__':
    main()