from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # TODO:
        # Write (two?) classes inside this .py file that represent data structures for
        # (1) neighbors of 'this' DVRouter
        # (2) routing table for 'this' DVRouter
        # Need to then call constructors for these data structures

        self.neighbors_table = Neighbors()
        self.routing_table = RoutingTable()


        # Data structures: https://piazza.com/class/hz9lw7aquvu2r9?cid=257


    """
    Called by the framework when the Entity self receives a packet.
	 packet - a Packet (or subclass).
	 port - port number it arrived on.
    """
    def handle_rx (self, packet, port):
        # Needs to be able to handle 3 types of packets:

        # 1) DiscoveryPacket: received by either end of the a link when the link either goes up or down
        # (DVRouter should never send or forward DiscoveryPackets) (.send() is a method of Entity superclass)

        # 2) RoutingUpdate: contain routing information that is received from the neighbors of the 'self' DVRouter

        # 3) Other packets are *data packets* which need to be sent on an appropriate port based on the switch's
        # current routing table

        # NOTE: Your DVRouter implementation must use the RoutingUpdate class 
        # as specified to share forwarding tables between routers


        if type(packet) is DiscoveryPacket:
            # Handle receiving of a discovery packet
            self.receive_discovery_packet(packet, port)
        elif type(packet) is RoutingUpdate:
            # Handle receiving of a routing update
            self.receive_routing_update(packet, port)
        else:
            # Send the packet on its way, based on this DVRouter's current routing table
            desired_packet_destination = packet.dst

            # If our desired packet destination is not even listed in the possible destinations for 'this' DVRouter
            # then we cannot possibly forward the packet, so we simply return
            if (desired_packet_destination not in self.routing_table.get_all_destinations_from_source().keys()):
                return
            elif (self.routing_table.get_next_hop_cost_for_source_and_destination(self, desired_packet_destination).getCost() != float("inf")):
                # Case where we do have a meaningful (i.e. non-infinity) cost to reach our destination

                # Use routing table to find out the next hop that we should use to get to desired_packet_destination
                next_hop_destination = self.routing_table.get_next_hop_cost_for_source_and_destination(self, desired_packet_destination).getNextHop()

                # Send the packet with the port that maps to our next hop destination
                self.send(packet, self.neighbors_table.get(next_hop_destination))
            else:
                # Case where the cost to reach our destination is infinity, so we just return (without sending the packet)
                return

	  # send(packet, port) obviously takes in a port number; this means that we have to determine
	  # precisely which port a packet needs to be sent out of. But how is this done?

	  # Via Piazza (@195), when we receive a discovery packet indicating a new link is up,
	  # we can pair the port that we received the packet on with the entity from which we
	  # received the packet -- i.e. *the data structure that maintains neighbors of 'this' DVRouter'
	  # can be a dictionary from <neighbor -> port>, where neighbor (i.e. other switches) is the key.

	  # Piazza (Shu Zhong) says: If you receive a discovery packet from source A on some port, 
	  # then you can send packets to A through the same port as long as the link stays up.



    """
    Helper method that handles the case where we are receiving a _DiscoveryPacket_

    This method checks whether the DiscoveryPacket has indicated that a neighbor was discovered or removed.
    It then:
    (1) updates the data structure that maintains 'this' DVRouter's list of neighbors
    (2) updates the data structure that maintains 'this' DVRouter's routing table (that contains costs to other switches)
    """
    def receive_discovery_packet(self, packet, port):

        # When is_link_up is True, you're discovering a neighbor (hence the name DiscoveryPacket). 
        if packet.is_link_up:
            # New neighbor of 'this' DVRouter has been discovered
            new_neighbor = packet.src

            # (updating of data structures):
            # (1) add this newly discovered neighbor to the list of neighbors for 'this' DVRouter
            self.neighbors_table.put(new_neighbor, port)

            # (2) update the cost from 'this' DVRouter to this newly discovered neighbor in our routing table
            self.routing_table.create_next_hop_cost_for_destination(self, new_neighbor, new_neighbor, 1)

        else:
            # Link has gone down, must handle this
            deleted_neighbor = packet.src

            # (updating of data structres):
            # (1) remove this deleted neighbor from our list of neighbors for 'this' DVRouter

            self.neighbors_table.remove_neighbor(deleted_neighbor)

            # (2) update the cost from 'this' DVRouter to our newly-deleted neighbor
            #     (need to do some weird stuff here based on how we handle deletion of links...
            #      maybe set the distance from 'this' DVRouter to newly-deleted neighbor as infinity?)

            # We will delete our entry in the routing table (for now)
            self.routing_table.delete_next_hop_cost_entry_for_destination(self, deleted_neighbor)

        # TODO: Since we have properly updated our data structures when neighbors have been
        # discovered/removed from 'this' DVRouter, we need to propagate our updated information
        # to all neighbors of 'this' DVRouter

        # Via project spec, we "send update packets to neighbors when the forwarding table of your router changes.
        # Update packets can also help withdraw routes the router previous announces to its neighbors by implicit
        # withdrawal or explicit withdrawal"

        # We can send an update by instantiating a new RoutingUpdate packet, potentially adding destinations to it,
        # and then calling this.send(routingUpdatePacket, ...) if routingUpdatePacket.allDests returns a value
        # greater than 0 (i.e. if there are actually updated costs that need to be sent)

        self.update_neighbors()


    """
    Helper method that handles the case where we are receiving a _RoutingUpdate (Packet)_

    A routing update simply corresponds to an update of routing table (i.e. costs) from a neighboring switch
    Thus, this helper method simply updates 'this' DVRouter's routing table basd on (many!) conditions
    and then sends an update as well.
    """
    def receive_routing_update(self, packet, port):

        # Argument 'packet' is of type RoutingUpdate

        needs_update = False

        # update_source is the router from which the routing update came from
    	update_source = packet.src

        # Get a list of all destinations with paths announced in this message.
        all_announced_destinations = packet.all_dests()
     
        for destination in all_announced_destinations:
            # First, propagate all of our new destinations into the routing table for the incoming packet's row
            self.routing_table.create_next_hop_cost_for_destination(update_source, destination, None, packet.get_distance(destination))

            # If the addition of our new destinations from incoming packet's row causes 'self' to find out about new destinations,
            # then add the new destinations to our routing table with the appropriate cost
            if destination not in self.routing_table.get_all_destinations_from_source(self):
                cost_from_source_to_update_source = self.routing_table.get_next_hop_cost_for_source_and_destination(self, update_source).getCost()
                cost_from_update_source_to_destination = packet.get_distance(destination)
                self.routing_table.create_next_hop_cost_for_destination(self, destination, update_source, cost_from_source_to_update_source + cost_from_update_source_to_destination)
                needs_update = True

        # ALGORITHM (https://piazza.com/class/hz9lw7aquvu2r9?cid=290):
        # First, we look at each of our <destination -> NextHopCost> entries in source_router_to_destinations_map[self]
        # Each of these entries, which we will denote by cost_from_self_to_destination, indicate the cost to go from self -> destination

        # Then, packet.get_distance(packet_destination') will represent the cost to go from update_source -> packet_destination

        # If cost_from_source_to_update_source + (cost_from_update_source_to_destination) < cost_from_self_to_destination
        #       (from dictionary)                     (from call to get_distance)                 (from iteration)

        # If the above equality is true, we update our routing table and set nextHop to update_source

        # Returns destinations from current router, along with the cost/next hop to these destinations
        # i.e. {D: {A: (3, C), B: (9, A), C: (2, D), D: (0, D), E: (3, D)} } is the outer array
        # extracted part is {A: (3, C), B: (9, A), C: (2, D), D: (0, D), E: (3, D)}
        current_router_destinations_to_next_hop_cost_map = self.routing_table.get_all_destinations_from_source(self)

        for final_destination, next_hop_cost in current_router_destinations_to_next_hop_cost_map.iteritems():
            # cost_from_self_to_destination
            cost_from_self_to_destination = next_hop_cost.getCost()

            # our final destination wasn't contained in our routing update, so the current 'final_destination' we're on cannot possibly be updated
            if final_destination not in packet.all_dests():
                continue

            # cost_from_update_source_to_destination
            cost_from_update_source_to_destination = packet.get_distance(final_destination)
            # cost_from_source_to_update_source
            cost_from_source_to_update_source = self.routing_table.get_next_hop_cost_for_source_and_destination(self, update_source).getCost()

            summed_alternate_path = cost_from_update_source_to_destination + cost_from_source_to_update_source

            next_hop_for_final_destination = self.routing_table.get_next_hop_cost_for_source_and_destination(self, final_destination).getNextHop()

            # new found path cost and old path cost are the same, so instructions say to take the one with the lower port number
            if summed_alternate_path == cost_from_self_to_destination:
                # new path has a lower port number than the old path
                if self.neighbors_table.get(update_source) < self.neighbors_table.get(next_hop_for_final_destination):
                    # ... so update the routing table with the new path
                    self.routing_table.create_next_hop_cost_for_destination(self, final_destination, update_source, summed_alternate_path)
                    needs_update = True

            # our new path from 'self' to 'destination' is shorter than our routing table's original path, so update routing table
            # with the new cost and with a new NextHop
            elif summed_alternate_path < cost_from_self_to_destination:
                self.routing_table.create_next_hop_cost_for_destination(self, final_destination, update_source, summed_alternate_path)
                needs_update = True

        # TODO: Implicit/explicit withdrawals

        if needs_update:
            self.update_neighbors()

        # Can call packet.all_dests to get a list of all destinations contained in the routing update
        # Can call packet.get_distance(destination) to get the distance to 'destination' as specified
        # by the packet who is calling the update

        # Perform implicit withdrawal
        # Implicit withdrawal means that routes to be withdrawn are excluded in a update,
        # so the receiver knows implicitly what routes are no longer available.




    """
    Helper method that sends RoutingUpdate packets to 'this' DVRouter's neighbors, 
    based on the current routing table
    """
    def update_neighbors(self):

        # These are the neighbors that we will be sending updates to
        list_of_neighbors = self.neighbors_table.get_neighbors()

        for neighbor in list_of_neighbors:
            if type(neighbor) is HostEntity:
                # Do not send any updates to HostEntities
                continue

            port_to_send_from = self.neighbors_table.get(neighbor)
            routing_update = RoutingUpdate()

            # map of destination -> NextHopCost for all destinations from self
            destinations_to_next_hop_costs_map = self.routing_table.get_all_destinations_from_source(self)
            for destination, next_hop_cost in destinations_to_next_hop_costs_map.iteritems():
                # if the destination/cost pair that we're on is exactly the neighbor that we would be updating, then skip it
                # i.e. 'Split Horizon'
                if neighbor == destination:
                    continue

                # TODO: Poison reverse
                

                routing_update.add_destination(destination, next_hop_cost.getCost())

            # Send the update packet from self
            self.send(routing_update, port_to_send_from, False)



'''
This class represents the data structure that keeps track of 'this' DVRouter's neighbors, along with the
port that should be used to send packet to each neighbor
'''
class Neighbors (object):

    def __init__(self):
        self.neighbor_to_port = {}

    # Retrieves a port in 'this' DVRouter that is associated to the given 'neighbor'
    def get(self, neighbor):
        return self.neighbor_to_port[neighbor]

    # Adds a <neighbor -> port> pair into the dictionary
    def put(self, neighbor, port):
        self.neighbor_to_port[neighbor] = port

    # Removes a neighbor from 'this' DVRouter (called when a link is torn down)
    def remove_neighbor(self, neighbor):
        del self.neighbor_to_port[neighbor]

    def get_number_of_neighbors(self):
        return len(self.neighbor_to_port.keys())

    def get_neighbors(self):
        return self.neighbor_to_port.keys()

'''

{D: {A: (3, C), B: (9, A), C: (2, D), D: (0, D), E: (3, D)} }

To get from source router D to A requires a cost of 3, with next hop C
To get from source router D to B requires a cost of 9, with next hop A
...

'''
class RoutingTable (object):
    INFINITY = 51

    def __init__(self):
        self.source_router_to_destinations_map = {}

    # Will return a dictionary correspondent to all destinations accessible by 'this' DVRouter, 
    # and the (cost, NextHop) object associated with each destination
    # i.e. {D: {A: (3, C), B: (9, A), C: (2, D), D: (0, D), E: (3, D)} } is the outer array
    # get_all_destinations_from_source(D) returns {A: (3, C), B: (9, A), C: (2, D), D: (0, D), E: (3, D)}
    def get_all_destinations_from_source(self, source_router):
        return self.source_router_to_destinations_map[source_router]

    # i.e. {D: {A: (3, C), B: (9, A), C: (2, D), D: (0, D), E: (3, D)} } 
    # get_next_hop_cost_for_source_and_destination(D, B) returns (9, A), correspondent to
    # the fact that it takes a cost of 9 to reach B, and the next hop to do so is A
    def get_next_hop_cost_for_source_and_destination(self, source_router, destination_router):
        return self.source_router_to_destinations_map[source_router][destination_router]

    # Given a source router, this method creates OR overwrites the <destination -> NextHopCost> entry in the 
    # inner map that is associated with the input destination_router
    def create_next_hop_cost_for_destination(self, source_router, destination_router, next_hop, cost):
        if (source_router not in self.source_router_to_destinations_map):
            # Need to make a new inner dictionary that corresponds to our source_router
            destinations_to_next_hop_costs_map = {}
            destinations_to_next_hop_costs_map[destination_router] = NextHopCost(cost, next_hop)
            self.source_router_to_destinations_map[source_router] = destinations_to_next_hop_costs_map

        else:
            self.source_router_to_destinations_map[source_router][destination_router] = NextHopCost(cost, next_hop)

    # Removes a <destination -> NextHopCost> entry in the inner map that is associated with an input source_router
    def delete_next_hop_cost_entry_for_destination(self, source_router, destination_router):
        if source_router in self.source_router_to_destinations_map and destination_router in self.source_router_to_destinations_map[source_router]:
            self.source_router_to_destinations_map[source_router].pop(destination_router, None)

    def __str__(self):
        return str(self.source_router_to_destinations_map)



'''
Wrapper class that represents the total cost/next hop correspondant to a particular destination
i.e. for {D: {A: (3, C), B: (9, A), C: (2, D), D: (0, D), E: (3, D)} }

(3, C) would be a NextHopCost object, as would (9, A), (2, D), (0, D), (3, D)
'''
class NextHopCost (object):

    def __init__(self, cost, next_hop):
        self.cost = cost
        self.next_hop = next_hop

    def getCost(self):
        return self.cost

    def getNextHop(self):
        return self.next_hop

    def setCost(self, new_cost):
        self.cost = new_cost

    def __repr__(self):
        s = "(Cost: "
        s += str(self.cost)
        s += " ; NextHop: "
        s += str(self.next_hop)
        s += ")"
        return s
