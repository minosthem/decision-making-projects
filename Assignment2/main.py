from os.path import join, exists
from models.models import Server, Customer, get_new_customers
import yaml
import os

properties_folder = join(os.getcwd(), "properties")
example_properties_file = join(properties_folder, "example_properties.yaml")
properties_file = join(properties_folder, "properties.yaml")
properties_file = "/home/nik/minos/Assignment2/properties/properties.yaml"


def pprint(msg, change_occured):
    if change_occured:
        print(msg)
        change_occured = False

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

    results_h = {"waited": 0, "served": 0, "content": 0}
    results_l = {"waited": 0, "served": 0, "content": 0}

    # counts per priority
    blocks_h, blocks_l = 0, 0
    total_h, total_l = 0, 0

    properties = load_properties()
    servers, needy_customers, served_customers, content_customers = [], [], [], []
    waiting_low, waiting_high = [], []
    total_arrival_count = 0
    change_occured = True

    for _ in range(properties["servers_num"]):
        # add servers
        server = Server()
        servers.append(server)

    def insert_waiting(max_capacity, source_list, admitted_list, num_served_or_content, new_arrivals_present, source_type, num_old_sources):
        capacity = max_capacity - len(admitted_list) - num_served_or_content
        num_sources = len(source_list)
        num_to_insert = min(capacity, num_sources)
        num_newcomers_blocked = 0
        if new_arrivals_present:
            num_newcomers = num_sources - num_old_sources
            # how many insertions happened in the newcomers
            num_newcomer_insertions = max(num_to_insert - num_old_sources, 0)
            # how many blockings happened in the newcomers
            num_newcomers_blocked = num_newcomers - num_newcomer_insertions
            assert num_newcomers_blocked + num_newcomer_insertions == num_newcomers , "???"
            print("Blocked {} {}-priority customers".format(num_newcomers_blocked, source_type))
        if num_to_insert > 0:
            for _ in range(num_to_insert):
                admitted_list.append(source_list.pop(0))
            print("Inserted {}/{} {}-priority customers.".format(num_to_insert, num_sources, source_type))
        return num_newcomers_blocked

    # simulate
    while True:
        # add new customers
        new_arrivals_present = total_arrival_count <= properties["max_total_arrivals"]
        if new_arrivals_present:
            new_low, new_high = get_new_customers(properties)
            total_arrival_count += len(new_low) + len(new_high)
            print("**Arrived: {} low and {} high priority customers".format(len(new_low), len(new_high)))
            # counts before update
            n_high_old, n_low_old = len(waiting_high), len(waiting_low)
            # update the queues 
            waiting_low.extend(new_low)
            waiting_high.extend(new_high)
            total_h += len(new_high)
            total_l += len(new_low)
        
        # let customers enter until capacity
        num_content_or_served = len(content_customers) + len(served_customers)
        pprint("Waiting ||  high: {} low: {}, admitted ||  needy: {}, served: {}, content {}".format(len(waiting_high), len(waiting_low), \
            len(needy_customers), len(served_customers), len(content_customers)), change_occured)
        change_occured = False

        # insertion of high priorities
        bh = insert_waiting(properties["servers_num"], waiting_high, needy_customers, num_content_or_served, new_arrivals_present, "high", n_high_old)
        blocks_h += bh
        bl = insert_waiting(properties["servers_num"], waiting_low, needy_customers, num_content_or_served, new_arrivals_present, "low", n_low_old)
        blocks_l += bl
        # print("Block / total count for high: {} {}".format(blocks_h, total_h))
        # print("Block / total count for low: {} {}".format(blocks_l, total_l))


        # assign needy customers to free servers
        for s, serv in enumerate(servers):
            if not needy_customers:
                break
            if not serv.is_occupied():
                # get a needy customer
                cust = needy_customers.pop(0)
                # assign them to the server
                cust.become_served(serv)
                served_customers.append(cust)
                print("Assigned to server #{}".format(s))
                change_occured = True

        # see if waiting / serving / ...  times are over
        # check if servign time is over
        for s, serv in enumerate(servers):
            if serv.is_occupied():
                # get customer they're serving
                cust = serv.customer
                # check if he's served enough
                if cust.is_done_being_served():
                    change_occured = True
                    print("Server {} completed".format(s))
                    # release server
                    serv.release()
                    # complete customer service state
                    served_customers.remove(cust)
                    cust.completed_being_served()
                    # decide if he'll become content or leave
                    left = cust.decide_to_leave()
                    if left:
                        res = cust.get_waiting_times()
                        storage = results_h if cust.priority == "high" else results_l
                        for k in res:
                            storage[k] += res[k]
                    else:
                        cust.become_content()
                        content_customers.append(cust)

        # check if customers are done being content
        for cust in content_customers:
            if cust.is_done_being_content():
                cust.completed_being_content() 
                # remove from the list
                content_customers.remove(cust)
                needy_customers.append(cust)
                change_occured = True
                print("Customer finished being content.")
        
        if not needy_customers and not content_customers and not served_customers:
            break

    print("Done. Total timings:")

    print("High:")
    for k, v in results_h.items():
        print(k, ":", v)
    print("Blocked prob {}, i.e. {}/{}".format(blocks_h / total_h, blocks_h, total_h))
    print("Low:")
    for k, v in results_l.items():
        print(k, ":", v)
    print("Blocked prob {}, i.e. {}/{}".format(blocks_l / total_l, blocks_l, total_l))


if __name__ == '__main__':
    main()