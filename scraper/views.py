from django.http import HttpResponse

from scraper.tasks import scrape_proxies


def runner_function(request):
    scrape_proxies.delay()
    return HttpResponse('Hello World!')