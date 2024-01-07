from helpers import *
import csv
import os


RESTAURANT_FILE_PATH = '/data/restaurants.json'
RECIPIENTS_FILE_PATH = '/data/recipients.json'

# Use all urls to bypass rate limits
tableUrls = [
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/nl-be',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/fr-be',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/fr-fr',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/de-at',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/da-dk',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/en-ie',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/pt-pt',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/de-de',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/it-it',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/fr-ch',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/de-ch',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/es-es',
    # 'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/nl-nl',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/en-gb',
    # 'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/en-int',
    'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/en-usd',
]

def main():
    dates = [
        '2024-01-11',
        '2024-01-12',
        '2024-01-13',
    ]
    
    printDated("Getting gmail service")
    service = get_gmail_service()

    printDated("Loading restaurants file")
    restaurants = load_data(RESTAURANT_FILE_PATH)

    printDated("Loading recipients file")
    recipients = load_data(RECIPIENTS_FILE_PATH)
    
    for date in dates:
        printDated(f'Fetching availabilities for {date}')
        i = 0
        availableRestaurantIds = checkTable(tableUrls[i], load_disney_token(), date, 2)
        while not availableRestaurantIds and i < len(tableUrls):
            i += 1
            printDated(f"Trying url {i+1}")
            availableRestaurantIds = checkTable(tableUrls[i], load_disney_token(), date, 2)

        if availableRestaurantIds:
            for friendly_name, restaurant_name_id in restaurants.items():
                restaurant_name, restaurant_id = restaurant_name_id
                printDated(f"Checking availability for {friendly_name}")

                if restaurant_id in availableRestaurantIds:
                    subject = f"Tafel beschikbaar bij {friendly_name} op {date}"
                    content = f"Er is op {datetime.datetime.today().replace(microsecond=0).isoformat()} een tafel gevonden bij {restaurant_name} voor {2} personen op {date}."
                    printDated(subject)
                    for recipient_friendly_name, recipient_name_email in recipients.items():
                        recipient_name, recipient_email = recipient_name_email
                        gmail_send_message(service, recipient_email, subject, content)
        else:
            printDated("ERROR: no restaurants found after trying all urls")


if __name__ == '__main__':
    main()
