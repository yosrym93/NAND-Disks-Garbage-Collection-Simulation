from sortedcontainers import SortedList
from config import *
from .physical_block import PhysicalBlock


class PhysicalDisk:
    COLD_BLOCK_ASSIGN_MIN_ERASE = 0
    COLD_BLOCK_ASSIGN_MIN_ERASE_OLD_BLOCK = 1

    def __init__(self, is_cold_active_block=True, cold_block_assign_policy=COLD_BLOCK_ASSIGN_MIN_ERASE):
        self.free_pages_count = physical_blocks_count * pages_per_block
        self.valid_blocks_count = 0

        self.cold_block_assign_policy = cold_block_assign_policy

        self.erase_counts = {0: physical_blocks_count}

        self.max_erase_count = 0
        self.min_erase_count = 0
        self.avg_erase_count = 0

        self.used_blocks = []
        self.free_blocks = SortedList()

        free_blocks_count = physical_blocks_count - 2 if is_cold_active_block else physical_blocks_count - 1
        for block in range(free_blocks_count):
            self.free_blocks.add(PhysicalBlock())

        self.hot_active_block = PhysicalBlock()
        if is_cold_active_block:
            self.cold_active_block = PhysicalBlock()
        else:
            self.cold_active_block = None

    def reallocate_to_new_page(self, logical_page, current_time, is_cold=False):
        if is_cold:
            free_physical_page = self.cold_active_block.get_free_page()
            if self.cold_active_block.is_full():
                self.assign_new_cold_active_block()
        else:
            free_physical_page = self.hot_active_block.get_free_page()
            if self.hot_active_block.is_full():
                self.assign_new_hot_active_block()

        if free_physical_page is None:
            print(self.hot_active_block.next_free_page_index)
            print(self.free_blocks)
            raise Exception('Could not allocate a free page')

        current_physical_page = logical_page.physical_page
        if current_physical_page is not None:
            current_physical_page.invalidate(current_time)

        free_physical_page.allocate(logical_page, current_time)
        logical_page.set_physical_page(free_physical_page)

    def assign_new_cold_active_block(self):
        self.used_blocks.add(self.cold_active_block)
        if self.cold_block_assign_policy == PhysicalDisk.COLD_BLOCK_ASSIGN_MIN_ERASE:
            self.cold_active_block = self.free_blocks.pop(0)
        else:
            self.cold_active_block = self.free_blocks.pop(index=len(self.free_blocks) // 2)

    def assign_new_hot_active_block(self):
        self.used_blocks.append(self.hot_active_block)
        self.hot_active_block = self.free_blocks.pop(0)

    def erase_block(self, block):
        block.erase()
        self.used_blocks.remove(block)
        self.free_blocks.add(block)

        self.erase_counts[block.erase_count - 1] -= 1
        if block.erase_count in self.erase_counts:
            self.erase_counts[block.erase_count] += 1
        else:
            self.erase_counts[block.erase_count] = 1
            self.max_erase_count = block.erase_count

        if self.erase_counts[self.min_erase_count] == 0:
            self.min_erase_count += 1

        if self.avg_erase_count == 0:
            self.avg_erase_count += 1
        else:
            self.avg_erase_count = ((self.avg_erase_count * physical_blocks_count) + 1) / self.avg_erase_count

    def calculate_stats(self):
        """
        This function calculate average update frequency and average predicted inter-update time
        :return:
        average update frequency
        average predicted inter-update time
        """
        average_updates = 0
        count_pages_used = 0
        for block in self.used_blocks:
            for page in block.pages:
                if page.is_valid():
                    average_updates += page.last_update
                    count_pages_used += 1
        try:
            average_updates = average_updates/count_pages_used
        except ZeroDivisionError:
            raise Exception('Division by zero, No pages are used')
        average_piu = 0
        for block in self.used_blocks:
            for page in block.pages:
                if page.is_valid():
                    page.piu = fegc_algorithm_alpha * page.last_update + (1-fegc_algorithm_alpha) * average_updates
                    average_piu += page.piu
        try:
            average_piu = average_piu / count_pages_used
        except ZeroDivisionError:
            raise Exception('Division by zero, No pages are used')
        return average_updates, average_piu
