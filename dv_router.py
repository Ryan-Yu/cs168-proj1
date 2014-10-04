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

			# TODO (updating of data structures):
			# (1) add this newly discovered neighbor to the list of neighbors for 'this' DVRouter
			# (2) update the cost from 'this' DVRouter to this newly discovered neighbor in our routing table

		else:
			# Link has gone down, must handle this
			deleted_neighbor = packet.src

			# TODO (updating of data structres):
			# (1) remove this deleted neighbor from our list of neighbors for 'this' DVRouter
			# (2) update the cost from 'this' DVRouter to our newly-deleted neighbor
			#     (need to do some weird stuff here based on how we handle deletion of links...
			#	  maybe set the distance from 'this' DVRouter to newly-deleted neighbor as infinity?)

		# TODO: Since we have properly updated our data structures when neighbors have been
		# discovered/removed from 'this' DVRouter, we need to propagate our updated information
		# to all neighbors of 'this' DVRouter

		# Via project spec, we "send update packets to neighbors when the forwarding table of your router changes.
		# Update packets can also help withdraw routes the router previous announces to its neighbors by implicit
		# withdrawal or explicit withdrawal"

		# We can send an update by instantiating a new RoutingUpdate packet, potentially adding destinations to it,
		# and then calling this.send(routingUpdatePacket, ...) if routingUpdatePacket.allDests returns a value
		# greater than 0 (i.e. if there are actually updated costs that need to be sent)



	"""
	Helper method that handles the case where we are receiving a _RoutingUpdate (Packet)_

	A routing update simply corresponds to an update of routing table (i.e. costs) from a neighboring switch
	Thus, this helper method simply updates 'this' DVRouter's routing table basd on (many!) conditions
	and then... maybe sends an update as well? (Does it need to actually send an update?)
	"""
	def receive_routing_update(self, packet, port):
		# Argument 'packet' is of type RoutingUpdate

		# Can call packet.all_dests to get a list of all destinations contained in the routing update
		# Can call packet.get_distance(destination) to get the distance to 'destination' as specified
		# by the packet who is calling the update

