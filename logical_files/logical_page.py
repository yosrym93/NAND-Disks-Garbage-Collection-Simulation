from config import *


class LogicalPage:
    def __init__(self, physical_disk, current_psn):
        self.psn = current_psn
        self.physical_page = None
        self.update_frequency = max_update_frequency / 2
        physical_page = physical_disk.get_free_page()
        self.set_physical_page(physical_page)

    def set_physical_page(self, physical_page):
        self.physical_page = physical_page
        self.physical_page.allocate(logical_page=self)

    def update(self, current_psn, physical_disk):
        self.physical_page.invalidate(physical_disk, current_psn)
        self.update_frequency = self.get_update_frequency(self.psn, current_psn)
        self.psn = current_psn
        physical_page = physical_disk.get_free_page()
        self.set_physical_page(physical_page)

    def get_update_frequency(self, current_psn, new_psn):
        psn_difference = (new_psn - current_psn) / physical_blocks_count
        if psn_difference > pages_per_block / 2:
            return min_update_frequency
        elif psn_difference < pages_per_block / 8:
            return self.update_frequency + min_update_frequency
        else:
            return self.update_frequency
