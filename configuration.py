import os
import m5
from m5.objects import *

# Create the system
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"  # System-wide clock
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

system.cpu.numIQEntries = 64
system.cpu.numROBEntries = 192

# Create the memory bus
system.membus = SystemXBar()
system.system_port = system.membus.cpu_side_ports

# Create and connect memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Connect CPU caches to the membus
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports
system.cpu.createInterruptController()

# Path to binary
thispath = os.path.dirname(os.path.realpath(__file__))
binary = os.path.join(thispath, "matmul")  # Update path if necessary

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
