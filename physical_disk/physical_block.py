from config import *
from .physical_page import PhysicalPage


class PhysicalBlock:
    def __init__(self):
        self.allocation_time = 0
        self.erase_count = 0
        self.invalid_pages_count = 0
        self.valid_pages_count = 0
        self.pages = []
        for page in range(pages_per_block):
            self.pages.append(PhysicalPage(physical_block=self))
        self.next_free_page_index = 0

    def get_free_page(self):
        if self.next_free_page_index == pages_per_block:
            return None
        free_page = self.pages[self.next_free_page_index]
        self.next_free_page_index += 1
        return free_page

    def is_full(self):
        return self.next_free_page_index >= pages_per_block

    def erase(self):
        self.allocation_time = 0
        self.invalid_pages_count = 0
        self.valid_pages_count = 0
        self.next_free_page_index = 0
        self.erase_count += 1
        for page in self.pages:
            page.free()

    def __lt__(self, other):
        return self.erase_count < other.erase_count

    def get_block_age(self, current_time):
        block_last_update = 0
        for page in self.pages:
            if page.last_update > block_last_update:
                block_last_update = page.last_update
        block_age = current_time - block_last_update
        return block_age

    def get_block_migration_cost(self, current_time, avg_erase_count, max_erase_count):
        valid_pages_percentage = self.valid_pages_count / pages_per_block
        if max_erase_count > 0:
            block_age = self.get_block_age(current_time) * (1 - valid_pages_percentage)\
                        / pow(1 + valid_pages_percentage, 2 - avg_erase_count / max_erase_count)
        else:
            block_age = self.get_block_age(current_time) * (1 - valid_pages_percentage)\
                        / pow(1 + valid_pages_percentage, 1)
        return block_age
