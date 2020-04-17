from garbage_collectors.adaptivefilewaregarbagecollector import AdaptiveFileWareGarbageCollector
from garbage_collectors.greedy_garbage_collector import GreedyGarbageCollector
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
    """greedy_physical_disk = PhysicalDisk(is_cold_active_block=False)
    greedy_garbage_collector = GreedyGarbageCollector(greedy_physical_disk)"""

    adaptive_fileware_disk = PhysicalDisk(is_cold_active_block=True)
    adaptive_fileware_garbage_collector=AdaptiveFileWareGarbageCollector(adaptive_fileware_disk)

    fig, (fagc_axis, x_axis) = plt.subplots(1, 2)

    # Number of pages in each file
    files_pages_counts = [random.randint(*file_pages_count_range) for _ in range(files_count)]

    update_operations = []
    for _ in range(update_operations_count):
        updated_pages_count = random.randint(*updated_pages_range)
        file_index = random.randint(0, files_count-1)
        start_page_index = random.randint(0, files_pages_counts[file_index]-updated_pages_count)
        for page_index in range(start_page_index, start_page_index + updated_pages_count):
            update_operations.append((file_index, page_index))

    statistics, erase_counts = run_simulation(
        adaptive_fileware_disk, adaptive_fileware_garbage_collector, files_pages_counts, update_operations
    )

    for description, count in statistics.items():
        print(f'{description} : {count}')

    index = range(len(erase_counts))

    fagc_axis.scatter(index, erase_counts, c='b', label='FaGC')
    fagc_axis.set_ylim(bottom=0, top=500)

    # Plot
    plt.show()


if __name__ == '__main__':
    main()
