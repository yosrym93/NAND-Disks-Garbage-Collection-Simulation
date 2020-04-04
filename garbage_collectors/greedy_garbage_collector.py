from .garbage_collector import GarbageCollector


class GreedyGarbageCollector(GarbageCollector):
    def __init__(self, physical_disk):
        super().__init__(physical_disk)

    def is_gc_needed(self):
        return len(self.physical_disk.free_blocks) < 2

    def get_victim_block(self, current_time):
        max_invalid_pages_count = 0
        max_invalid_pages_block = None

        for block in self.physical_disk.used_blocks:
            if block.invalid_pages_count > max_invalid_pages_count:
                max_invalid_pages_count = block.invalid_pages_count
                max_invalid_pages_block = block

        return max_invalid_pages_block

    def reallocate_block(self, victim_block):
        for page in victim_block.pages:
            if page.is_valid():
                self.copy_operations_count += 1
                self.physical_disk.reallocate_to_new_page(page.logical_page)
