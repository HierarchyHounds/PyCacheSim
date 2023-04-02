import argparse
import os
from cache.Cache import Cache
from policies import fifo, lru, optimal
from utils.Debugger import Debugger

def main():
	parser = argparse.ArgumentParser(description="Cache Simulator")
	parser.add_argument("blocksize", type=int, help="Block size in bytes")
	parser.add_argument("l1_size", type=int, help="L1 cache size in bytes")
	parser.add_argument("l1_assoc", type=int, help="L1 set associativity (1 is direct-mapped)")
	parser.add_argument("l2_size", type=int, help="L2 cache size in bytes (0 for no L2 cache)")
	parser.add_argument("l2_assoc", type=int, help="L2 set associativity (1 is direct-mapped)")
	parser.add_argument("replacement_policy", type=int, choices=[0, 1, 2], help="Replacement policy (0 for LRU, 1 for FIFO, 2 for optimal)")
	parser.add_argument("inclusion_property", type=int, choices=[0, 1], help="Inclusion property (0 for non-inclusive, 1 for inclusive)")
	parser.add_argument("trace_file", type=str, help="Full name of trace file including any extensions")
	parser.add_argument("--debug", action=argparse.BooleanOptionalAction, help="Generate debug output (default: False)")

	args = parser.parse_args()
	Debugger.debug = args.debug

	# check if L1_SIZE, L1_ASSOC, L2_SIZE, L2_ASSOC are all positive integers
	if args.l1_size <= 0 or args.l1_assoc <= 0 or args.l2_size < 0 or args.l2_assoc < 0:
		print("L1_SIZE, L1_ASSOC, L2_SIZE, L2_ASSOC must all be positive integers")
		exit(1)

	# check if BLOCKSIZE is a power of 2; if not, throw an error and exit
	if args.blocksize & (args.blocksize - 1) != 0:
		print("BLOCKSIZE must be a power of 2")
		exit(1)

	# TODO:\tbetter error handling- check if num_l1_sets it's fractional etc.
	# check if # of sets in L1 is power of 2; if not, throw an error and exit
	num_l1_sets = args.l1_size // (args.l1_assoc * args.blocksize)
	if num_l1_sets != int(num_l1_sets):
		print("L1 # of sets must be a power of 2")
		exit(1)
	num_l1_sets = int(num_l1_sets)

	if num_l1_sets & (num_l1_sets - 1) != 0:
		print("L1 # of sets must be a power of 2")
		exit(1)

	# if l2_size != 0, check if # of sets in L1 is power of 2; if not, throw an error and exit
	if args.l2_size != 0:
		num_l2_sets = args.l2_size // (args.l2_assoc * args.blocksize)
		if num_l2_sets & (num_l2_sets - 1) != 0:
			print("L2 # of sets must be a power of 2")
			exit(1)

	# `REPLACEMENT_POLICY`:\tPositive integer. 0 for LRU, 1 for FIFO, 2 for optimal.
	# `INCLUSION_PROPERTY`:\tPositive integer. 0 for non-inclusive, 1 for inclusive.

	inclusion_property_name = None
	if args.inclusion_property == 0:
		inclusion_property_name = "non-inclusive"
	elif args.inclusion_property == 1:
		inclusion_property_name = "inclusive"

	# Create the appropriate replacement policy
	PolicyClass = None
	if args.replacement_policy == 0:
		PolicyClass = lru.LRU
	elif args.replacement_policy == 1:
		PolicyClass = fifo.FIFO
	elif args.replacement_policy == 2:
		PolicyClass = optimal.Optimal

	policyClassName = Debugger.policyClassName = PolicyClass.__name__

	trace_file_basename = os.path.basename(args.trace_file)

	print("===== Simulator configuration =====")

	print("BLOCKSIZE:\t\t", args.blocksize)
	print("L1_SIZE:\t\t", args.l1_size)
	print("L1_ASSOC:\t\t", args.l1_assoc)
	print("L2_SIZE:\t\t", args.l2_size)
	print("L2_ASSOC:\t\t", args.l2_assoc)
	print("REPLACEMENT POLICY:\t", policyClassName)
	print("INCLUSION PROPERTY:\t", inclusion_property_name)
	print("trace_file:\t\t", trace_file_basename)

	# Create L1 and L2 cache instances with the appropriate configurations
	if args.l2_size > 0:
		l2_cache = Cache(args.l2_size, args.l2_assoc, args.blocksize, PolicyClass, args.inclusion_property, debugger=Debugger(prefix="L2"))
	else:
		l2_cache = None
	l1_cache = Cache(args.l1_size, args.l1_assoc, args.blocksize, PolicyClass, args.inclusion_property, lower_cache=l2_cache, debugger=Debugger(prefix="L1"))

	debugger = Debugger()

	# Access the cache with L1 and L2 instances
	with open(args.trace_file, "r") as trace_file:
		for line in trace_file:
			operation, address = line.split()
			debugger.operationStart(operation, address)
			l1_cache.access(operation, int(address, 16))

	print_results(l1_cache, l2_cache)


def print_results(l1_cache, l2_cache):
	memory_traffic = l1_cache.memory_accesses

	print("===== L1 contents =====")
	l1_cache.print_contents()

	if l2_cache:
		memory_traffic += l2_cache.memory_accesses
		print("\n===== L2 contents =====")
		l2_cache.print_contents()

	print("===== Simulation results (raw) =====")
	print(f"a. number of L1 reads:\t\t{l1_cache.reads}")
	print(f"b. number of L1 read misses:\t{l1_cache.read_misses}")
	print(f"c. number of L1 writes:\t\t{l1_cache.writes}")
	print(f"d. number of L1 write misses:\t{l1_cache.write_misses}")
	print(f"e. L1 miss rate:\t\t{l1_cache.get_miss_rate():.6f}")
	print(f"f. number of L1 writebacks:\t{l1_cache.writebacks}")

	if l2_cache:
		print(f"g. number of L2 reads:\t\t{l2_cache.reads}")
		print(f"h. number of L2 read misses:\t{l2_cache.read_misses}")
		print(f"i. number of L2 writes:\t\t{l2_cache.writes}")
		print(f"j. number of L2 write misses:\t{l2_cache.write_misses}")
		print(f"k. L2 miss rate:\t\t{l2_cache.get_miss_rate():.6f}")
		print(f"l. number of L2 writebacks:\t{l2_cache.writebacks}")
	else:
		print("g. number of L2 reads:\t\t0")
		print("h. number of L2 read misses:\t0")
		print("i. number of L2 writes:\t\t0")
		print("j. number of L2 write misses:\t0")
		print("k. L2 miss rate:\t\t0")
		print("l. number of L2 writebacks:\t0")

	print(f"m. total memory traffic:\t{memory_traffic}")

if __name__ == "__main__":
	main()
