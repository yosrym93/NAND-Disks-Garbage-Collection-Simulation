from garbage_collectors.greedy_garbage_collector import GreedyGarbageCollector
from garbage_collectors.fegc import FeGC
from garbage_collectors.mcsgc_garbage_collector import MCSGCGarbageCollector
from physical_disk.physical_disk import PhysicalDisk
from logical_files.file import File
import random
import time
from config import *
import matplotlib.pyplot as plt


def run_simulation(physical_disk, garbage_collector, files_pages_counts, update_operations):
    current_time = 1
    files = []

    # Create simulation files
    for pages_count in files_pages_counts:
        files.append(File(pages_count, physical_disk, current_time))
        current_time += pages_count     # Each page is allocated in one time step

    # Run simulation updates and invoke the garbage collector
    update_times = []
    gc_times = []
    for idx, (file_index, page_index) in enumerate(update_operations):
        print('\rUpdate operation: {}'.format(idx), end='')
        start = time.time()
        files[file_index].update_page(page_index, current_time)
        checkpoint = time.time()
        garbage_collector.run(current_time)
        end = time.time()
        update_times.append(checkpoint - start)
        gc_times.append(end - checkpoint)
        current_time += 1

    print('')
    print('Simulation total updates time: {0}, total GC time: {1}'.format(sum(update_times), sum(gc_times)))

    erase_counts = [block.erase_count for block in physical_disk.used_blocks]
    erase_counts.append(physical_disk.hot_active_block.erase_count)
    if physical_disk.cold_active_block is not None:
        erase_counts.append(physical_disk.cold_active_block.erase_count)

    statistics = {
        'Total erase operations': garbage_collector.erase_operations_count,
        'Total copy operations': garbage_collector.copy_operations_count,
        'Average erase counts': sum(erase_counts) / len(erase_counts)
    }

    return statistics, erase_counts


def main():
    greedy_physical_disk = PhysicalDisk(is_cold_active_block=False)
    # fegc_physical_disk = PhysicalDisk(is_cold_active_block=True, cold_block_assign_policy=1)
    mcsgc_physical_disk = PhysicalDisk(is_cold_active_block=True, cold_block_assign_policy=1)
    greedy_garbage_collector = GreedyGarbageCollector(greedy_physical_disk)
    # fegc_garbage_collector = FeGC(fegc_physical_disk)
    mcsgc_garbage_collector = MCSGCGarbageCollector(mcsgc_physical_disk)

    simulation_disks_and_gcs = [
        # ('Greedy GC', greedy_physical_disk, greedy_garbage_collector),
        ('MCSGC', mcsgc_physical_disk, mcsgc_garbage_collector)
    ]

    fig, axes = plt.subplots(1, len(simulation_disks_and_gcs))

    # Ensure axes is a list (iterable)
    if len(simulation_disks_and_gcs) == 1:
        axes = [axes]


    # Number of pages in each file
    files_pages_counts = [random.randint(*file_pages_count_range) for _ in range(files_count)]

    update_operations = []
    for _ in range(update_operations_count):
        updated_pages_count = random.randint(*updated_pages_range)
        if uniform_updates:
            file_index = random.randint(0, files_count-1)
        else:
            file_index = int(random.gauss(files_count / 2, files_count/10))
        start_page_index = random.randint(0, files_pages_counts[file_index]-updated_pages_count)
        for page_index in range(start_page_index, start_page_index + updated_pages_count):
            update_operations.append((file_index, page_index))

    for axis, simulation_disk_and_GC in zip(axes, simulation_disks_and_gcs):
        title, physical_disk, garbage_collector = simulation_disk_and_GC
        print(title)
        statistics, erase_counts = run_simulation(
            physical_disk, garbage_collector, files_pages_counts, update_operations
        )
        for description, count in statistics.items():
            print(f'{description} : {count}')

        index = range(len(erase_counts))
        axis.scatter(index, erase_counts, c='b', label='FaGC')
        axis.set_ylim(bottom=0, top=50)
        axis.set_title(title)

    plt.show()


if __name__ == '__main__':
    main()
