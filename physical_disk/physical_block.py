from config import *
from .physical_page import PhysicalPage


class PhysicalBlock:
    def __init__(self):
        self.erase_count = 0
        self.invalid_pages_count = 0
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
        self.invalid_pages_count = 0
        self.next_free_page_index = 0
        self.erase_count += 1
        for page in self.pages:
            page.free()

    def __lt__(self, other):
        return self.erase_count < other.erase_count
