from .garbage_collector import GarbageCollector
from config import *


class AdaptiveFileWareGarbageCollector(GarbageCollector):
    threshold = 2
    empirical_constant = 0.5

    def __init__(self, physical_disk):
        super().__init__(physical_disk)

    def is_gc_needed(self):
        return len(self.physical_disk.free_blocks) < self.threshold

    def get_victim_block(self, current_time):
        level_invalidate_page_list = [[] for _ in range(pages_per_block + 1)]
        erase_count_threshold = self.physical_disk.min_erase_count + self.empirical_constant * \
                                (self.physical_disk.max_erase_count - self.physical_disk.min_erase_count)
        victim_block = None
        more_stable_block_flag = False
        for block in self.physical_disk.used_blocks:
            if block.erase_count > erase_count_threshold:
                continue
            stability = block.get_block_age(current_time)
            victim_score = stability / (block.erase_count + 1)
            level_invalidate_page_list[pages_per_block - block.invalid_pages_count].append((block, victim_score))

        for idx, level in enumerate(level_invalidate_page_list):
            level_invalidate_page_list[idx] = sorted(level, key=lambda x: -x[1])

        criteria_block = None
        criteria_score = 0
        for level in level_invalidate_page_list:
            if victim_block is not None:
                break
            if len(level) > 1:
                for block, victim_score in level:
                    if victim_score > criteria_score:
                        victim_block = block
                        break
            elif len(level) == 1:
                if criteria_score == 0:
                    criteria_block = level[0][0]
                    criteria_score = level[0][1]

        if victim_block is None:
            victim_block = criteria_block

        # if len(level_invalidate_page_list[0]) > 1:
        #     victim_block = level_invalidate_page_list[0][0][0]
        #     more_stable_block_flag = True
        # elif len(level_invalidate_page_list[0]) == 1:
        #     for level in range(1, len(level_invalidate_page_list)):
        #         if len(level_invalidate_page_list[level]) != 0:
        #             if level_invalidate_page_list[0][0][1] < \
        #                     level_invalidate_page_list[level][0][1] < erase_count_threshold or (
        #                     erase_count_threshold == 0):
        #                 victim_block = level_invalidate_page_list[level][0][0]
        #                 more_stable_block_flag = True
        #                 break
        # if not more_stable_block_flag:
        #     for idx, level in enumerate(level_invalidate_page_list):
        #         if more_stable_block_flag:
        #             break
        #         if len(level) > 0:
        #             for block, victim_score in level:
        #                 victim_block = block
        #                 more_stable_block_flag = True
        #                 break

        return victim_block

    def reallocate_block(self, victim_block, current_time):
        hotness_threshold = 0
        valid_pages_hotness_in_block = []
        for page in victim_block.pages:
            if page.is_valid():
                valid_pages_hotness_in_block.append((page,
                                                     (page.logical_page.update_count /
                                                      (current_time - page.logical_page.allocation_time)) *
                                                     (current_time - page.logical_page.last_update_time)))
        if len(valid_pages_hotness_in_block) != 0:
            hotness_threshold = sum(x[1] for x in valid_pages_hotness_in_block) / len(valid_pages_hotness_in_block)
        else:
            hotness_threshold = 0
        for page, hotness in valid_pages_hotness_in_block:
            if hotness >= hotness_threshold:
                self.physical_disk.reallocate_to_new_page(page.logical_page, current_time)
            else:
                self.physical_disk.reallocate_to_new_page(page.logical_page, current_time, is_cold=True)
            self.copy_operations_count += 1
