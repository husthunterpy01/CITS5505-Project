class PaginationService:
    @staticmethod
    def build_page_numbers(current_page, total_pages, window=2):
        if total_pages <= 1:
            return [1]
        start = max(1, current_page - window)
        end = min(total_pages, current_page + window)
        return list(range(start, end + 1))
