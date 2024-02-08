import scrapy
import urllib


class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["ru.wikipedia.org"]
    start_urls = ["https://ru.wikipedia.org/wiki/Категория:Фильмы_по_годам"]


    def parse_film(self, response):
        url = urllib.parse.unquote(response.url)

        if not self.is_film_page(response):
            self.logger.warning(f'Skipping not a film page at {url}')
            return

        title = self.parse_title(response)
        genre = self.parse_genre(response)
        director = self.parse_director(response)
        country = self.parse_country(response)
        year = self.parse_year(response)

        if not title:
            self.logger.error(f'no title at url {url}')

        if not genre:
            self.logger.error(f'no genre at url {url}')

        if not director:
            self.logger.error(f'no director at url {url}')
        
        if not country:
            self.logger.error(f'no country at url {url}')

        if not year:
            self.logger.error(f'no year at url {url}')

        yield {
            'title': title,
            'genre': genre,
            'director': director,
            'country': country,
            'year': year
        }

    def is_film_page(self, response):
        return response.css('table[data-name="Фильм"]').getall() or response.css('table[data-name="Мультфильмы"]').getall()

    def parse_property(self, id: str, response):
        return response.css(f'span[data-wikidata-property-id="{id}"] *::text').getall()

    def parse_title(self, response):
        return response.css('th.infobox-above::text').get()
    
    def parse_genre(self, response):
        return self.parse_property('P136', response)

    def parse_director(self, response):
        return self.parse_property('P57', response)

    def parse_country(self, response):
        return self.parse_property('P495', response)

    def parse_year(self, response):
        return (
            self.parse_property('P577', response)
            or self.parse_property('P571', response)
            or response.css('span[class="dtstart"]::text').getall()
        )
    
    def parse_local_page(self, response):
        for local_link in response.css('div.mw-category-group > ul > li > a::attr(href)').getall():
            if local_link:
                yield response.follow(local_link, callback=self.parse_film)


    def parse(self, response):
        for global_link in response.css("div.CategoryTreeItem > a::attr(href)").getall():
            if global_link:
                yield response.follow(global_link, callback=self.parse_local_page)
