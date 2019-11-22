from os.path import join
import pandas
from models.models import Server, get_new_customers
import logging


def pprint(msg, change_occurred, dt):
    if change_occurred:
        logging.getLogger().debug("loop: {} | ".format(dt) + msg)


def count_free_servers(servers):
    return len([s for s in servers if not s.is_occupied()])


def run_experiment(properties):
    dt = properties["dt"]
    # containers to store timings / delays, the sum for all customers of that type
    # -----------------
    times_outside, times_needy, times_served, times_content = [], [], [], []

    # index of customers that left, in that order
    left_customer_index = []
    left_customer_priority = []
    # booleans blocking and total arrivals
    waited_outside = []
    waited_inside = []

    # per-loop information containers
    current_free_servers = []
    current_needy_queue_lengths = []
    current_number_of_customers_arrived = []
    current_number_of_customers_left = []

    # -----------------

    # container lists
    servers, needy_customers, served_customers, content_customers = [], [], [], []
    waiting_outside_low, waiting_outside_high = [], []
    total_customers_created = 0
    change_occurred = True

    for _ in range(properties["servers_num"]):
        # add servers
        server = Server()
        servers.append(server)

    # function to decide insertion of blocked arrivals to the facility
    def insert_waiting(max_total_admitted, source_list, admitted_list, num_served_or_content, source_type,
                       loop_counter):
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
                admitted_list.append(cust)
            num_blocked = 0
            # mark all other customers as blocked
            for cust in source_list:
                if not cust.waited_outside:
                    # just arrived, and blocked
                    num_blocked += 1
                cust.waited_outside = True
            pprint("Blocked {} {}-priority customers".format(num_blocked, source_type), change_occurred, loop_counter)
            pprint("Inserted {}/{} {}-priority customers.".format(num_to_insert, num_sources, source_type),
                   change_occurred, loop_counter)
            inserted = True
        return inserted

    loop_counter = 0
    # simulate
    while True:
        # add new customers
        # boolean noting if new arrivals come at this iteration
        new_arrivals_present = total_customers_created <= properties["max_total_arrivals"]
        if new_arrivals_present:
            # count up the new arrivals
            new_low, new_high, total_customers_created = get_new_customers(properties, total_customers_created)
            if len(new_high + new_low) > 0:
                pprint("Arrived: {} low and {} high priority customers, global total {}".format(len(new_low),
                                                                                                len(new_high),
                                                                                                total_customers_created),
                       change_occurred, loop_counter)
                # update the queues 
                waiting_outside_low.extend(new_low)
                waiting_outside_high.extend(new_high)

        # let customers enter until capacity
        num_content_or_served = len(content_customers) + len(served_customers)
        pprint("Waiting ||  high: {} low: {}, admitted ||  needy: {}, served: {}, content {}"
               .format(len(waiting_outside_high), len(waiting_outside_low), len(needy_customers), len(served_customers),
                       len(content_customers)), change_occurred, loop_counter)
        # for less verbose printing (eg only if something changed)
        change_occurred = False

        # insertion of high priorities
        change_occurred = insert_waiting(properties["max_total_admitted"], waiting_outside_high, needy_customers,
                                         num_content_or_served, "high", loop_counter)
        change_occurred = insert_waiting(properties["max_total_admitted"], waiting_outside_low, needy_customers,
                                         num_content_or_served, "low", loop_counter)
        pprint("Waiting ||  high: {} low: {}, admitted ||  needy: {}, served: {}, content {}"
               .format(len(waiting_outside_high), len(waiting_outside_low), len(needy_customers), len(served_customers),
                       len(content_customers)), change_occurred, loop_counter)
        change_occurred = False

        # counts for mean queue length and free servers statistics
        current_free_servers.append(count_free_servers(servers))
        current_needy_queue_lengths.append(len(needy_customers))
        # keep track of information per loop, for burnin purposes
        current_number_of_customers_arrived.append(total_customers_created)
        current_number_of_customers_left.append(len(left_customer_index))

        # assign needy customers to free servers
        for s, serv in enumerate(servers):
            if not needy_customers:
                break
            current_num_customers_served = len([s for s in servers if s.is_occupied()])
            if not serv.is_occupied():
                # get a needy customer
                customer = needy_customers.pop(0)
                # assign them to the server
                customer.become_served(serv, len(servers), current_num_customers_served)
                served_customers.append(customer)
                pprint("Assigned to server #{}, time needed: {}".format(s, customer.service_time_needed),
                       change_occurred, loop_counter)
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
                    pprint("Server {} completed".format(s), change_occurred, loop_counter)
                    # release server
                    serv.release()
                    # complete customer service state
                    served_customers.remove(customer)
                    customer.completed_being_served()
                    # decide if he'll become content or leave
                    left = customer.decide_to_leave()
                    if left:
                        left_customer_index.append(customer.get_arrival_index())
                        left_customer_priority.append(customer.priority)
                        # get durations of customer states
                        w_out, w_in, w_served, w_content = customer.get_waiting_times()
                        times_outside.append(w_out)
                        times_needy.append(w_in)
                        times_served.append(w_served)
                        times_content.append(w_content)
                        # append booleans for waiting
                        waited_outside.append(customer.waited_outside)
                        waited_inside.append(customer.waited_inside)

                        pprint("Customer {} left".format(customer), change_occurred, loop_counter)

                    else:
                        pprint("Customer {} is now content, time needed: {}".format(customer,
                                                                                    customer.content_time_needed),
                               change_occurred, loop_counter)
                        customer.become_content(len(content_customers))
                        content_customers.append(customer)

        # check if customers are done being content
        for customer in content_customers:
            if customer.is_done_being_content():
                customer.completed_being_content()
                # remove from the list
                content_customers.remove(customer)
                needy_customers.append(customer)
                change_occurred = True
                pprint("Customer finished being content.", change_occurred, loop_counter)

        if total_customers_created >= properties["max_total_arrivals"] and not \
            (needy_customers or content_customers or served_customers or waiting_outside_high or waiting_outside_low):

            pprint("All {} customers consumed, processed and left!".format(total_customers_created), True, loop_counter)
            break

        # update time
        for n in needy_customers:
            n.tick(dt)
        for s in servers:
            if s.is_occupied():
                s.customer.tick(dt)
        for c in content_customers:
            c.tick(dt)
        for w in waiting_outside_high + waiting_outside_low:
            w.tick(dt)

        pprint("Loop done", True, loop_counter)
        loop_counter += 1

    df_customers = pandas.DataFrame()
    df_customers["waited_out"] = times_outside
    df_customers["waited_in"] = times_needy
    df_customers["duration_served"] = times_served
    df_customers["duration_content"] = times_content
    df_customers["arrival_index"] = left_customer_index
    df_customers["priority"] = left_customer_priority
    df_customers["delay_out"] = waited_outside
    df_customers["delay_in"] = waited_inside

    df_loop = pandas.DataFrame()
    df_loop["needy_queue_length"] = current_needy_queue_lengths
    df_loop["free_servers"] = current_free_servers
    df_loop["number_arrived"] = current_number_of_customers_arrived
    df_loop["number_left"] = current_number_of_customers_left

    customer_csv = join(properties["output_dir"], "{}_customers.csv".format(properties["run_id"]))
    loop_csv = join(properties["output_dir"], "{}_loops.csv".format(properties["run_id"]))
    df_customers.to_csv(customer_csv, index=None)
    df_loop.to_csv(loop_csv, index=None)
