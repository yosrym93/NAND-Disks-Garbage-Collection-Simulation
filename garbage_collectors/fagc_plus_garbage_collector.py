from config import *
from .garbage_collector import GarbageCollector


class FaGCPlusGarbageCollector(GarbageCollector):
    def __init__(self, physical_disk):
        super().__init__(physical_disk)

    def get_victim_block(self, current_psn):
        erase_count_difference = self.physical_disk.get_erase_count_difference()
        erase_count_threshold = 0.5 * gc_erase_count_weight * self.physical_disk.get_invalid_blocks_ratio()

        scattering_factor = self.physical_disk.get_scattering_factor()

        if erase_count_difference > erase_count_threshold:
            victim_block = self.physical_disk.get_min_erase_count_block()
        elif scattering_factor > gc_scattering_threshold:
            victim_block = self.physical_disk.get_max_cps_block(current_psn)
        else:
            victim_block = None  # No garbage collection

        return victim_block

    def reallocate_block(self, victim_block):
        pages_categories = [[], [], [], []]
        for page in victim_block.pages:
            if page.is_valid():
                update_frequency = page.logical_page.update_frequency
                if update_frequency < max_update_frequency / 4:
                    pages_categories[0].append(page)
                elif update_frequency < max_update_frequency / 2:
                    pages_categories[1].append(page)
                elif update_frequency < max_update_frequency * 3 / 4:
                    pages_categories[2].append(page)
                else:
                    pages_categories[3].append(page)

        for category_pages in pages_categories:
            self.copy_operations_count += len(category_pages)
            self.physical_disk.reallocate_pages_to_free_block(category_pages)
