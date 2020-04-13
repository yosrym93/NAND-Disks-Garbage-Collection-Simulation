from .garbage_collector import GarbageCollector
from config import *


class AdaptiveFileWareGarbageCollector(GarbageCollector):
    threshold = 5
    empirical_constant = 3
    level_invalidate_page_list = [None] * pages_per_block

    def __init__(self, physical_disk):
        super().__init__(physical_disk)

    def is_gc_needed(self):
        return self.physical_disk.free_pages_count < self.threshold

    def get_victim_block(self, current_time):
        erase_count_threshold = self.physical_disk.min_erase_count * self.empirical_constant * \
                                (self.physical_disk.min_erase_count + self.physical_disk.max_erase_count)
        victim_block = None
        more_stable_block_flag = False
        for block in self.physical_disk.used_blocks:
            stability = current_time - 5
            victim_score = block.erase_count * stability
            self.level_invalidate_page_list[pages_per_block - block.invalid_pages_count].append((block, victim_score))
        for level in self.level_invalidate_page_list:
            sorted(level, key=lambda x: -x[1])
        if len(self.level_invalidate_page_list[0] > 1) and self.level_invalidate_page_list[0][0][1] \
                < erase_count_threshold:
            victim_block = self.level_invalidate_page_list[0][0][0]
        elif len(self.level_invalidate_page_list[0] == 1):
            for level in range(1, len(self.level_invalidate_page_list)):
                if self.level_invalidate_page_list[0][0][1] < \
                        self.level_invalidate_page_list[level][0][1] < erase_count_threshold:
                    victim_block = self.level_invalidate_page_list[level][0][0]
                    more_stable_block_flag = True
                    break
        if not more_stable_block_flag:
            for level in self.level_invalidate_page_list:
                if len(level) != 0 and level[0][1] < erase_count_threshold:
                    more_stable_block_flag = True
                    victim_block = level[0][0]
        if not more_stable_block_flag:
            for level in self.level_invalidate_page_list:
                for block, victim_score in level:
                    if victim_score < erase_count_threshold:
                        victim_block = block
                        break
        return victim_block

    def reallocate_block(self, victim_block, current_time):
        hotness_threshold = 0
        valid_pages_hotness_in_block = []
        for page in victim_block.pages:
            if page.is_valid():
                valid_pages_hotness_in_block.append((page,
                                                     (page.logical_page.update_counter /
                                                      (current_time - page.logical_page.allocation_time)) *
                                                     (current_time - page.logical_page.last_update_time)))
        hotness_threshold = sum(valid_pages_hotness_in_block) / len(valid_pages_hotness_in_block)
        for page, hotness in valid_pages_hotness_in_block:
            if hotness >= hotness_threshold:
                self.physical_disk.reallocate_to_new_page(page.logical_page)
            else:
                self.physical_disk.reallocate_to_new_page(page.logical_page, True)
            self.copy_operations_count += 1
