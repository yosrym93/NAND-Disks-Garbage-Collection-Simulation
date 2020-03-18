from config import *
from .physical_block import PhysicalBlock


class PhysicalDisk:
    def __init__(self):
        self.free_pages_count = physical_blocks_count * pages_per_block
        self.valid_blocks_count = 0

        self.erase_counts = {0: physical_blocks_count}

        self.max_erase_count = 0
        self.min_erase_count = 0

        self.blocks = []

        for block in range(physical_blocks_count):
            self.blocks.append(PhysicalBlock())

        self.free_blocks = set(self.blocks)
        self.blocks_with_free_pages = set(self.blocks)

    def reallocate_pages_to_free_block(self, pages):
        if len(pages) == 0:
            return

        free_block = self.free_blocks.pop()

        self.free_pages_count -= len(pages)
        self.valid_blocks_count += 1

        for page in pages:
            logical_page = page.logical_page
            new_physical_page = free_block.get_free_page()
            logical_page.set_physical_page(new_physical_page)

        if free_block.free_pages_count == 0:
            self.blocks_with_free_pages.remove(free_block)

    def get_free_page(self):
        if len(self.blocks_with_free_pages) > 0:
            self.free_pages_count -= 1
            block = next(iter(self.blocks_with_free_pages))
            if block.state == block.FREE:
                self.valid_blocks_count += 1
                self.free_blocks.remove(block)
            elif block.free_pages_count == 1:
                self.blocks_with_free_pages.remove(block)
            free_page = block.get_free_page()
        else:
            raise Exception('No available physical page')
        return free_page

    def erase_block(self, block):
        self.free_pages_count += pages_per_block - block.free_pages_count

        block.erase()
        self.free_blocks.add(block)
        self.blocks_with_free_pages.add(block)

        self.erase_counts[block.erase_count - 1] -= 1
        if block.erase_count in self.erase_counts:
            self.erase_counts[block.erase_count] += 1
        else:
            self.erase_counts[block.erase_count] = 1
            self.max_erase_count = block.erase_count

        if self.erase_counts[self.min_erase_count] == 0:
            self.min_erase_count += 1

    def get_invalid_blocks_ratio(self):
        return 1 - (self.valid_blocks_count / physical_blocks_count)

    def get_erase_count_difference(self):
        return self.max_erase_count - self.min_erase_count

    def get_min_erase_count_block(self):
        blocks_erase_count = [block.erase_count for block in self.blocks]
        index = blocks_erase_count.index(min(blocks_erase_count))
        return self.blocks[index]

    def get_scattering_factor(self):
        if self.free_pages_count == 0:
            return gc_scattering_threshold + 1
        scattering_factor = (self.free_pages_count -
                             len(self.free_blocks) * pages_per_block) \
                            / self.free_pages_count
        return scattering_factor

    def get_max_cps_block(self, current_psn):
        blocks_cps = [block.get_cps(current_psn) for block in self.blocks]
        index = blocks_cps.index(max(blocks_cps))
        return self.blocks[index]

    # def find_closest_updating_frequency_block(self, update_frequency):
    #     blocks_with_free_pages = [block for block in self.blocks if block.free_pages_count > 0]
    #     min_index = min(range(len(blocks_with_free_pages)),
    #                     key=lambda i: abs(blocks_with_free_pages[i].average_update_frequency - update_frequency))
    #     return blocks_with_free_pages[min_index]
