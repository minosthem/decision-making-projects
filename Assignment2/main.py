from os.path import join, exists
from models.models import Server, Customer
import yaml
import os

properties_folder = join(os.getcwd(), "properties")
example_properties_file = join(properties_folder, "example_properties.yaml")
properties_file = join(properties_folder, "properties.yaml")
properties_file = "/home/sissy/Documents/minos/decision-making-projects/Assignment2/properties/properties.yaml"

def load_properties():
    """
    Load yaml file containint program's properties
    :return: the properties dictionary and the output folder path
    """
    ffile = properties_file if exists(properties_file) else example_properties_file
    with open(ffile, 'r') as f:
        properties = yaml.safe_load(f)
    return properties


def main():
    properties = load_properties()
    servers, needy_customers, content_customers = [], [], []

    for _ in range(properties["servers_num"]):
        # add servers
        server = Server()
        servers.append(server)
        # add customers
        needy_customers.append(Customer(prob_stay=properties["prob_stay"], exp_params=properties["exp_params"]))

    # simulate
    while True:
        # assign customers to free servers
        for s in servers:
            if not s.is_occupied():
                # get a needy customer
                cust = needy_customers.pop(0)
                # assign them to the server
                cust.become_served(s)

        # see if waiting / serving / ...  times are over
        # check if servign time is over
        for s in servers:
            if s.is_occupied():
                # get customer they're serving
                cust = s.customer
                # check if he's served enough
                if cust.is_done_being_served():
                    # release server
                    s.release()
                    # complete customer service state
                    cust.complete_being_served()
                    # decide if he'll become content or leave
                    left = cust.decide_to_leave_or_not()
                    if left:
                        results = cust.get_waiting_times()
                    else:
                        cust.become_content()
                        content_customers.append(cust)

        # check if customers are done being content
        for cust in content_customers:
            if cust.is_done_being_content():
                cust.complete_being_content() 
                # remove from the list
                content_customers.remove(cust)
                needy_customers.append(cust)
    


if __name__ == '__main__':
    main()