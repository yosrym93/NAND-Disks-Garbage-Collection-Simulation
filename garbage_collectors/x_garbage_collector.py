from config import *
from .garbage_collector import GarbageCollector


class XGarbageCollector(GarbageCollector):
    def __init__(self, physical_disk):
        super().__init__(physical_disk)

    def get_victim_block(self, current_psn):
        # TODO: Change the block selection criteria
        erase_count_difference = self.physical_disk.get_erase_count_difference()
        erase_count_threshold = 0.5 * gc_erase_count_weight * self.physical_disk.get_invalid_blocks_ratio()

        scattering_factor = self.physical_disk.get_scattering_factor()

        if erase_count_difference > erase_count_threshold:
            victim_block = self.physical_disk.get_min_erase_count_block()
        elif scattering_factor > gc_scattering_threshold:
            victim_block = self.physical_disk.get_max_cps_block(current_psn)
        else:
            victim_block = None

        return victim_block

    def reallocate_block(self, victim_block):
        # TODO: Re-implement by creating a function in physical disk that takes a page and allocate it
        #  automatically to the closest block in terms of update frequency (or change reallocation policy)
        valid_pages = []
        for page in victim_block.pages:
            if page.is_valid():
                valid_pages.append(page)

        for page in valid_pages:
            closest_block = self.physical_disk.find_closest_updating_frequency_block(page.logical_page.update_frequency)
            self.copy_operations_count += 1
            logical_page = page.logical_page
            new_physical_page = self.physical_disk.get_free_page(block=closest_block)
            logical_page.set_physical_page(new_physical_page)
