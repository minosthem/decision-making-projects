import os
from os.path import join, exists
from collections import Counter
import yaml

from models.models import Server, get_new_customers

properties_folder = join(os.getcwd(), "properties")
example_properties_file = join(properties_folder, "example_properties.yaml")
properties_file = join(properties_folder, "properties.yaml")


def pprint(msg, change_occured):
    if change_occured:
        print(msg)

def count_free_servers(servers):
        return len([s for s in servers if not s.is_occupied()])

def load_properties():
    """
    Load yaml file containint program's properties
    :return: the properties dictionary and the output folder path
    """
    ffile = properties_file if exists(properties_file) else example_properties_file
    with open(ffile, 'r') as f:
        properties = yaml.safe_load(f)
    if "max_total_admitted" not in properties:
        properties["max_total_admitted"] = None
    return properties


def main():
    # containers to store timings / delays, the sum for all customers of that type
    results_h = {"waited_outside": [], "waited_needy": [], "served": [], "content": []}
    results_l = {"waited_outside": [], "waited_needy": [], "served": [], "content": []}

    # counts per priority: blocking and total arrivals
    blocks_h, blocks_l = 0, 0
    total_h, total_l = 0, 0

    # counts per priority of customers that encountered no delay
    no_delay_h, no_delay_l = 0, 0

    free_servers_list = []

    properties = load_properties()
    # container lists
    servers, needy_customers, served_customers, content_customers = [], [], [], []
    waiting_low, waiting_high = [], []
    total_arrival_count = 0
    change_occurred = True

    for _ in range(properties["servers_num"]):
        # add servers
        server = Server()
        servers.append(server)

    # function to decide insertion of blocked arrivals to the facility
    def insert_waiting(max_total_admitted, source_list, admitted_list, num_served_or_content, new_arrivals_created,
                       source_type, num_old_sources):
        num_sources = len(source_list)
        num_newcomers_blocked = 0
        inserted = False
        if max_total_admitted is not None:
            capacity = max_total_admitted - len(admitted_list) - num_served_or_content
            num_to_insert = min(capacity, num_sources)
        else:
            num_to_insert = len(source_list)
        if new_arrivals_created:
            num_newcomers = num_sources - num_old_sources
            # how many insertions happened in the newcomers
            num_newcomer_insertions = max(num_to_insert - num_old_sources, 0)
            # how many blockings happened in the newcomers
            num_newcomers_blocked = num_newcomers - num_newcomer_insertions
            assert num_newcomers_blocked + num_newcomer_insertions == num_newcomers, "???"
            print("Blocked {} {}-priority customers".format(num_newcomers_blocked, source_type))
        if num_to_insert > 0:
            for _ in range(num_to_insert):
                cust = source_list.pop(0)
                cust.complete_waiting_outside()
                cust.become_needy()
                admitted_list.append(cust)
            # mark all other customers as blocked
            for cust in source_list:
                cust.waited_outside = True
            print("Inserted {}/{} {}-priority customers.".format(num_to_insert, num_sources, source_type))
            inserted = True
        return num_newcomers_blocked, inserted

    # simulate
    while True:
        # add new customers
        # boolean noting if new arrivals come at this iteration
        new_arrivals_present = total_arrival_count <= properties["max_total_arrivals"]
        n_high_old = 0
        n_low_old = 0
        if new_arrivals_present:
            # count up the new arrivals
            new_low, new_high = get_new_customers(properties)
            total_arrival_count += len(new_low) + len(new_high)
            print("**Arrived: {} low and {} high priority customers".format(len(new_low), len(new_high)))
            # counts before update
            n_high_old, n_low_old = len(waiting_high), len(waiting_low)
            # update the queues 
            waiting_low.extend(new_low)
            waiting_high.extend(new_high)
            # count up total arrivals
            total_h += len(new_high)
            total_l += len(new_low)

        # let customers enter until capacity
        num_content_or_served = len(content_customers) + len(served_customers)
        pprint("Waiting ||  high: {} low: {}, admitted ||  needy: {}, served: {}, content {}"
               .format(len(waiting_high), len(waiting_low), len(needy_customers), len(served_customers),
                       len(content_customers)), change_occurred)
        # for less verbose printing (eg only if something changed)
        change_occurred = False

        # insertion of high priorities
        bh, change_occurred = insert_waiting(properties["max_total_admitted"], waiting_high, needy_customers, num_content_or_served,
                            new_arrivals_present, "high", n_high_old)
        blocks_h += bh
        bl, change_occurred = insert_waiting(properties["max_total_admitted"], waiting_low, needy_customers, num_content_or_served,
                            new_arrivals_present, "low", n_low_old)
        blocks_l += bl
        pprint("Waiting ||  high: {} low: {}, admitted ||  needy: {}, served: {}, content {}"
            .format(len(waiting_high), len(waiting_low), len(needy_customers), len(served_customers),
                        len(content_customers)), change_occurred)
        change_occurred = False

        # print("Block / total count for high: {} {}".format(blocks_h, total_h))
        # print("Block / total count for low: {} {}".format(blocks_l, total_l))

        # assign needy customers to free servers
        free_servers_list.append(count_free_servers(servers))

        for s, serv in enumerate(servers):
            if not needy_customers:
                break
            if not serv.is_occupied():
                # get a needy customer
                customer = needy_customers.pop(0)
                # assign them to the server
                customer.become_served(serv)
                served_customers.append(customer)
                print("Assigned to server #{}".format(s))
                change_occurred = True

        # if there are needy customers remaining, these customers waited in the internal queue
        for cust in needy_customers:
            cust.waited_inside = True

        # see if waiting / serving / ...  times are over
        # check if servign time is over
        for s, serv in enumerate(servers):
            if serv.is_occupied():
                # get customer they're serving
                customer = serv.customer
                # check if he's served enough
                if customer.is_done_being_served():
                    change_occurred = True
                    print("Server {} completed".format(s))
                    # release server
                    serv.release()
                    # complete customer service state
                    served_customers.remove(customer)
                    customer.completed_being_served()
                    # decide if he'll become content or leave
                    left = customer.decide_to_leave()
                    if left:
                        res = customer.get_waiting_times()
                        storage = results_h if customer.priority == "high" else results_l
                        for k in res:
                            storage[k].append(res[k])
                        if not (customer.waited_inside or customer.waited_outside):
                            # no delay for the customer
                            if customer.priority == "high":
                                no_delay_h +=1
                            elif customer.priority == "low":
                                no_delay_l +=1
                        print("Customer {} left".format(customer))

                    else:
                        print("Customer {} is now content".format(customer))
                        customer.become_content()
                        content_customers.append(customer)

        # check if customers are done being content
        for customer in content_customers:
            if customer.is_done_being_content():
                customer.completed_being_content()
                # remove from the list
                content_customers.remove(customer)
                needy_customers.append(customer)
                change_occurred = True
                print("Customer finished being content.")

        if not needy_customers and not content_customers and not served_customers:
            break

    print("Done. Total timings:")

    print("High:")
    for k, v in results_h.items():
        print(k, ":", sum(v)/len(v))
    print("Blocked prob {}, i.e. {}/{}".format(blocks_h / total_h, blocks_h, total_h))
    print("No delay prob {}, i.e. {}/{}".format(no_delay_h / total_h, no_delay_h, total_h))

    print("Low:")
    for k, v in results_l.items():
        print(k, ":", sum(v)/len(v))
    print("Blocked prob {}, i.e. {}/{}".format(blocks_l / total_l, blocks_l, total_l))
    print("No delay prob {}, i.e. {}/{}".format(no_delay_l / total_l, no_delay_l, total_l))

    print("Mean number of free servers: {}".format(sum(free_servers_list) / len(free_servers_list)))



if __name__ == '__main__':
    main()
