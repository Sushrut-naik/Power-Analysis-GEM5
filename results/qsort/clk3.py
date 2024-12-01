import os
import m5
from m5.objects import *

# Create the system
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "3GHz"  # System-wide clock
system.clk_domain.voltage_domain = VoltageDomain()

# Set memory mode and range
system.mem_mode = "timing"
system.mem_ranges = [AddrRange('512MB')]

# Instantiate O3CPU with a separate clock domain
system.cpu = O3CPU()
system.cpu_clk_domain = SrcClockDomain()
system.cpu_clk_domain.clock = "2GHz"  # CPU-specific clock
system.cpu_clk_domain.voltage_domain = VoltageDomain()
system.cpu.clk_domain = system.cpu_clk_domain  # Assign the clock domain to the CPU

system.cpu.fetchWidth = 4
system.cpu.decodeWidth = 4
system.cpu.renameWidth = 4
system.cpu.issueWidth = 4
system.cpu.dispatchWidth = 4
system.cpu.commitWidth = 4

system.cpu.numIQEntries = 128
system.cpu.numROBEntries = 384

# Create and connect instruction cache (I-cache)
system.cpu.icache = Cache(
    size="32kB",  # Size of the instruction cache
    assoc=2,  # Associativity
    tag_latency=2,  # Latency for tag lookup
    data_latency=2,  # Latency for data access
    response_latency=2,  # Total response latency
    mshrs=16,  # Number of MSHRs (Miss Status Holding Registers)
    tgts_per_mshr=20,  # Targets per MSHR
)
system.cpu.icache.cpu_side = system.cpu.icache_port

# Create and connect data cache (D-cache)
system.cpu.dcache = Cache(
    size="32kB",  # Size of the data cache
    assoc=2,  # Associativity
    tag_latency=2,  # Latency for tag lookup
    data_latency=2,  # Latency for data access
    response_latency=2,  # Total response latency
    mshrs=16,  # Number of MSHRs
    tgts_per_mshr=20,  # Targets per MSHR
)
system.cpu.dcache.cpu_side = system.cpu.dcache_port

# Add a shared L2 cache
system.l2cache = Cache(
    size="256kB",  # Size of the L2 cache
    assoc=8,  # Higher associativity for the shared cache
    tag_latency=20,  # Latency for tag lookup
    data_latency=20,  # Latency for data access
    response_latency=20,  # Total response latency
    mshrs=32,  # Number of MSHRs
    tgts_per_mshr=16,  # Targets per MSHR
)

# Add a crossbar for the CPU-side connections to the L2 cache
system.cpu_side_xbar = L2XBar()

# Connect the I-cache and D-cache to the CPU-side crossbar
system.cpu.icache.mem_side = system.cpu_side_xbar.cpu_side_ports
system.cpu.dcache.mem_side = system.cpu_side_xbar.cpu_side_ports

# Connect the CPU-side crossbar to the L2 cache
system.cpu_side_xbar.mem_side_ports = system.l2cache.cpu_side

# Create the memory bus
system.membus = SystemXBar()
system.system_port = system.membus.cpu_side_ports

# Connect the L2 cache to the memory bus
system.l2cache.mem_side = system.membus.cpu_side_ports

# Create and connect memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Add interrupt controller
system.cpu.createInterruptController()

# Path to binary
thispath = os.path.dirname(os.path.realpath(__file__))
binary = os.path.join(thispath, "qsort_large")  # Update path if necessary

# Set the workload and process
system.workload = SEWorkload.init_compatible(binary)
process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()

# Root and instantiate
root = Root(full_system=False, system=system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")