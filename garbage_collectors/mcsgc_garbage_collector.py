from .garbage_collector import GarbageCollector


class MCSGCGarbageCollector(GarbageCollector):
    def __init__(self, physical_disk):
        super().__init__(physical_disk)

    def is_gc_needed(self):
        return len(self.physical_disk.free_blocks) < 10

    def get_victim_block(self, current_time):
        victim_block = self.physical_disk.get_min_migration_cost_block(current_time)
        return victim_block

    def reallocate_block(self, victim_block, current_time):
        for page in victim_block.pages:
            if page.is_valid():
                self.copy_operations_count += 1
                avg_update_frequency_time = self.physical_disk.get_average_update_frequency_time(current_time)
                if(page.get_update_frequency_time(current_time) > avg_update_frequency_time):
                    self.physical_disk.reallocate_to_new_page(page.logical_page, current_time)
                else:
                    self.physical_disk.reallocate_to_new_page(page.logical_page, current_time, True)
