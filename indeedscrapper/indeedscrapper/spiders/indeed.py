import scrapy
import json
import scrapy
from urllib.parse import urlencode
from gc import callbacks
import re

class IndeedSpider(scrapy.Spider):
    name = "indeed"
    
    
    def get_url(self,keyword,location,offset=0):
        parameters = {"q" : keyword, "l": location, "start" : offset, "filter" : 0}
        return "https://in.indeed.com/jobs?" + urlencode(parameters)
    
    
    def start_requests(self):
        keywords = ["work from home"]
        locations = ["Tamil Nadu"]
        for keyword in keywords:
            for location in locations:
                search_url = self.get_url(keyword,location)
                yield scrapy.Request(url = search_url, callback = self.parse_jobs, meta= {"keyword" : keyword, "location" : location, "offset" : 0})
        
    def parse_jobs(self, response):
        keyword = response.meta["keyword"]
        location = response.meta["location"]
        offset = response.meta["offset"]
        
        next_page_relative_url = response.css("a[data-testid=pagination-page-next] ::attr(href)").get()
        if next_page_relative_url is not None:
            next_page_url = f"https://in.indeed.com{next_page_relative_url}"

            offset = next_page_relative_url.split("&")[-1].split("=")[-1]
            if int(offset) < 510:
                yield scrapy.Request(url = next_page_url, callback = self.parse_jobs, meta= {"keyword" : keyword, "location" : location, "offset" : offset})
        
        js = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+\});', response.text)
        if js is not None:
             json_blob = json.loads(js[0])
        
        jobs = json_blob['metaData']['mosaicProviderJobCardsModel']['results']
        
        for index,job in enumerate(jobs):
            yield{
                "keyword" : keyword,
                "location" : location,
                "page" : int(int(offset)/10),
                "job position" : f"{index+1}/15 in page {int(int(offset)/10)}",
                "company" : job.get('company'),
                "company rating" : job.get('companyRating'),
                "company review count" : job.get('companyReviewCount'),
                "title" : job.get('displayTitle'),
                "job key" : job.get('jobkey'),
                "Formatted Location": job.get('formattedLocation'),
                "Salary" : job.get('salarySnippet').get('text'),
                "Job Link" : f"https://in.indeed.com/{job.get('link')}",
                
                }
            