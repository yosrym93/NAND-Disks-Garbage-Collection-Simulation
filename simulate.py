from garbage_collectors.fagc_plus_garbage_collector import FaGCPlusGarbageCollector
from garbage_collectors.x_garbage_collector import XGarbageCollector
from physical_disk.physical_disk import PhysicalDisk
from logical_files.file import File
import random
import time
from config import *
import matplotlib.pyplot as plt


def run_simulation(physical_disk, garbage_collector, files_pages_counts, update_operations):
    current_psn = 1
    files = []

    # Create simulation files
    for pages_count in files_pages_counts:
        files.append(File(pages_count, physical_disk, current_psn))
        current_psn += 1

    # Run simulation updates and invoke the garbage collector
    update_times = []
    gc_times = []
    for idx, (file_index, page_index) in enumerate(update_operations):
        print('Update operation: {0}, Scattering factor: {1}\r'.
              format(idx, physical_disk.get_scattering_factor()), end='')
        start = time.time()
        files[file_index].update_page(page_index, current_psn)
        checkpoint = time.time()
        garbage_collector.run(current_psn)
        end = time.time()
        update_times.append(checkpoint - start)
        gc_times.append(end - checkpoint)
        current_psn += 1

    print('')
    # print(sum(update_times), sum(gc_times))

    erase_counts = [block.erase_count for block in physical_disk.blocks]

    statistics = {
        'Total erase operations': garbage_collector.erase_operations_count,
        'Total copy operations': garbage_collector.copy_operations_count,
        'Average erase counts': sum(erase_counts) / len(erase_counts)
    }

    return statistics, erase_counts


def main():
    fagc_physical_disk = PhysicalDisk()
    fagc_garbage_collector = FaGCPlusGarbageCollector(fagc_physical_disk)

    # x_physical_disk = PhysicalDisk()
    # x_garbage_collector = XGarbageCollector(x_physical_disk)

    fig, (fagc_axis, x_axis) = plt.subplots(1, 2)

    # Number of pages in each file
    files_pages_counts = [random.randint(*file_pages_count_range) for _ in range(files_count)]

    update_operations = []
    for _ in range(update_operations_count):
        file_index = random.randint(0, files_count-1)
        page_index = random.randint(0, files_pages_counts[file_index]-1)
        update_operations.append((file_index, page_index))

    try:
        statistics, erase_counts = run_simulation(
            fagc_physical_disk, fagc_garbage_collector, files_pages_counts, update_operations
        )
    except KeyError as e:
        print('\nKey Error:')
        print(e)
        print('Scattering factor: {}'.format(fagc_physical_disk.get_scattering_factor()))
        print('# Free blocks: {}'.format(len(fagc_physical_disk.free_blocks)))
        print('# Free pages: {}'.format(fagc_physical_disk.free_pages_count))
        print([block.free_pages_count for block in fagc_physical_disk.blocks])
        exit()

    for description, count in statistics.items():
        print(f'{description} : {count}')

    index = range(len(erase_counts))

    fagc_axis.scatter(index, erase_counts, c='b', label='FaGC')
    fagc_axis.set_ylim(bottom=0, top=200)

    # Plot
    plt.show()


if __name__ == '__main__':
    main()
