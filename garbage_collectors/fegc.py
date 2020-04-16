from .garbage_collector import GarbageCollector


class FeGC(GarbageCollector):
    def __init__(self, physical_disk):
        super().__init__(physical_disk)
        self.average_updates = 0
        self.average_piu = 0

    def run(self, current_time):
        if self.is_gc_needed():
            self.average_updates, self.average_piu = self.physical_disk.calculate_stats()
        super().run(current_time)

    def is_gc_needed(self):
        return len(self.physical_disk.free_blocks) < 2

    def get_victim_block(self, current_time):
        max_caw = 0
        victim_block = None
        all_invalid_block = None

        for block in self.physical_disk.used_blocks:
            # If there exist a block with all the pages invalid in it, Then it will be chooses as the victim block
            if block.invalid_pages_count == len(block.pages):
                all_invalid_block = block
                break
            caw = 0
            # Loop on all pages to calculate Cost with Age (CaW) Value
            for page in block.pages:
                if not page.is_valid():
                    caw += current_time - page.time_invalid
            if caw > max_caw:
                max_caw = caw
                victim_block = block
        if all_invalid_block:
            return all_invalid_block
        else:
            return victim_block

    def reallocate_block(self, victim_block, current_time):
        # Loop on every page in the victim block and classify them into cold or hot
        for page in victim_block.pages:
            if page.is_valid():
                self.copy_operations_count += 1
                if page.piu > self.average_piu:
                    # Pages classified as cold pages needs to be assigned to old blocks
                    self.physical_disk.reallocate_to_new_page(page.logical_page, current_time, is_cold=True)
                else:
                    # Pages classified as hot pages needs to be assigned to young blocks
                    self.physical_disk.reallocate_to_new_page(page.logical_page, current_time, is_cold=False)
