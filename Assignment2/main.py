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
    times = {"high" : {"waited_outside": [], "waited_needy": [], "served": [], "content": []},
             "low" : {"waited_outside": [], "waited_needy": [], "served": [], "content": []}}

    # counts per priority: blocking and total arrivals
    blocks_count = {"high": 0, "low": 0}
    total_count = {"high": 0, "low": 0}
    waiting_count = {"high": 0, "low": 0}
    # counts per priority of customers that encountered no delay
    nodelay_count = {"high": 0, "low": 0}

    free_servers_list = []
    needy_queue_lengths = []

    properties = load_properties()
    # container lists
    servers, needy_customers, served_customers, content_customers = [], [], [], []
    waiting_outside_low, waiting_outside_high = [], []
    total_arrival_count = 0
    change_occurred = True

    for _ in range(properties["servers_num"]):
        # add servers
        server = Server()
        servers.append(server)

    # function to decide insertion of blocked arrivals to the facility
    def insert_waiting(max_total_admitted, source_list, admitted_list, num_served_or_content, source_type):
        num_sources = len(source_list)
        inserted = False
        if max_total_admitted is not None:
            capacity = max_total_admitted - len(admitted_list) - num_served_or_content
            num_to_insert = min(capacity, num_sources)
        else:
            num_to_insert = len(source_list)
        if num_to_insert > 0:
            for _ in range(num_to_insert):
                cust = source_list.pop(0)
                cust.complete_waiting_outside()
                cust.become_needy()
                admitted_list.append(cust)
            num_blocked = 0
            # mark all other customers as blocked
            for cust in source_list:
                if not cust.waited_outside:
                    # just arrived, and blocked
                    num_blocked += 1
                cust.waited_outside = True
            print("Blocked {} {}-priority customers".format(num_blocked, source_type))
            print("Inserted {}/{} {}-priority customers.".format(num_to_insert, num_sources, source_type))
            inserted = True
        return inserted

    # simulate
    while True:
        # add new customers
        # boolean noting if new arrivals come at this iteration
        new_arrivals_present = total_arrival_count <= properties["max_total_arrivals"]
        if new_arrivals_present:
            # count up the new arrivals
            new_low, new_high = get_new_customers(properties)
            total_arrival_count += len(new_low) + len(new_high)
            print("**Arrived: {} low and {} high priority customers".format(len(new_low), len(new_high)))
            # update the queues 
            waiting_outside_low.extend(new_low)
            waiting_outside_high.extend(new_high)
            # count up total arrivals
            total_count["high"] += len(new_high)
            total_count["low"] += len(new_low)

        # let customers enter until capacity
        num_content_or_served = len(content_customers) + len(served_customers)
        pprint("Waiting ||  high: {} low: {}, admitted ||  needy: {}, served: {}, content {}"
               .format(len(waiting_outside_high), len(waiting_outside_low), len(needy_customers), len(served_customers),
                       len(content_customers)), change_occurred)
        # for less verbose printing (eg only if something changed)
        change_occurred = False

        # insertion of high priorities
        change_occurred = insert_waiting(properties["max_total_admitted"], waiting_outside_high, needy_customers, num_content_or_served, "high")
        change_occurred = insert_waiting(properties["max_total_admitted"], waiting_outside_low, needy_customers, num_content_or_served, "low")
        pprint("Waiting ||  high: {} low: {}, admitted ||  needy: {}, served: {}, content {}"
            .format(len(waiting_outside_high), len(waiting_outside_low), len(needy_customers), len(served_customers),
                        len(content_customers)), change_occurred)
        change_occurred = False

        # print("Block / total count for high: {} {}".format(blocks_h, total_h))
        # print("Block / total count for low: {} {}".format(blocks_l, total_l))

        # assign needy customers to free servers
        free_servers_list.append(count_free_servers(servers))
        needy_queue_lengths.append(len(needy_customers))


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
                        for k in res:
                            times[customer.priority][k].append(res[k])

                        # only if burned-in
                        num_customers_left =  len(times[customer.priority][k])
                        if num_customers_left > properties["num_burnin"]:
                            # do counts for probabilities
                            if not customer.waited_outside:
                                if not customer.waited_inside:
                                    # no delay for the customer
                                    nodelay_count[customer.priority] += 1
                                else:
                                    waiting_count[customer.priority] += 1
                            else:
                                blocks_count[customer.priority] += 1

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

    burnin = properties["num_burnin"]
    print("Using burnin: ", burnin)
    print("Done. Total timings:")

    for prior in times:
        print("####### {}-probability customers:".format(prior))
        for k, v in times[prior].items():
            # apply burnin for time durations
            v = v[burnin:]
            print(k, ":", sum(v)/len(v))

        print("Blocked prob {}, i.e. {}/{}".format(blocks_count[prior] / total_count[prior], blocks_count[prior], total_count[prior]))
        print("Waiting prob {}, i.e. {}/{}".format(waiting_count[prior] / total_count[prior], waiting_count[prior], total_count[prior]))
        print("No-delay prob {}, i.e. {}/{}".format(nodelay_count[prior] / total_count[prior], nodelay_count[prior], total_count[prior]))

    # apply burnin
    free_servers_list = free_servers_list[burnin:]
    needy_queue_lengths = needy_queue_lengths[burnin:]
    print("Mean number of free servers: {}".format(sum(free_servers_list) / len(free_servers_list)))
    print("Mean queue length for needy customers: {}".format(sum(needy_queue_lengths) / len(needy_queue_lengths)))

if __name__ == '__main__':
    main()
