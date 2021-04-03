from .service import ScraperService


class ScraperServiceFactory:

    @classmethod
    def create(cls):
        return ScraperService()
