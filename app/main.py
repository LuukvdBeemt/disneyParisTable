from helpers import *
import csv
import os


RESTAURANT_FILE_PATH = '/data/restaurants.json'
RECIPIENTS_FILE_PATH = '/data/recipients.json'

tableUrl_1 = 'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/en-us'
tableUrl_2 = 'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/en-gb'
tableUrl_3 = 'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/en-ie'
tableUrl_4 = 'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/nl-be'
tableUrl_5 = 'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/en-int'
tableUrl_6 = 'https://dlp-is-sales-drs-book-dine.wdprapps.disney.com/prod/v4/book-dine/availabilities/be-be'

def main():
    dates = [
        '2024-01-11',
        '2024-01-12',
        '2024-01-13',
    ]
    
    # restaurants = [
    #     {
    #         'name': 'Ratatouille',
    #         'id': 'P2TR02',
    #     },
    #     {
    #         'name': 'Captain Jack',
    #         'id': 'P1AR00',
    #     },
    #     {
    #         'name': 'Cape Cod',
    #         'id': 'H03R00',
    #     },
    # ]

    printDated("Getting gmail service")
    service = get_gmail_service()

    printDated("Loading restaurants file")
    restaurants = load_data(RESTAURANT_FILE_PATH)

    printDated("Loading recipients file")
    recipients = load_data(RECIPIENTS_FILE_PATH)
    
    for date in dates:
        availableRestaurantIds = checkTable(tableUrl_1, os.environ['AUTH_KEY'], date, 2)
        if not availableRestaurantIds:
            availableRestaurantIds = checkTable(tableUrl_1, os.environ['AUTH_KEY_SECONDARY'], date, 2)
        if not availableRestaurantIds:
            availableRestaurantIds = checkTable(tableUrl_2, os.environ['AUTH_KEY'], date, 2)
        if not availableRestaurantIds:
            availableRestaurantIds = checkTable(tableUrl_2, os.environ['AUTH_KEY_SECONDARY'], date, 2)
        if not availableRestaurantIds:
            availableRestaurantIds = checkTable(tableUrl_3, os.environ['AUTH_KEY'], date, 2)
        if not availableRestaurantIds:
            availableRestaurantIds = checkTable(tableUrl_3, os.environ['AUTH_KEY_SECONDARY'], date, 2)
        if not availableRestaurantIds:
            availableRestaurantIds = checkTable(tableUrl_4, os.environ['AUTH_KEY'], date, 2)
        if not availableRestaurantIds:
            availableRestaurantIds = checkTable(tableUrl_4, os.environ['AUTH_KEY_SECONDARY'], date, 2)
        if not availableRestaurantIds:
            availableRestaurantIds = checkTable(tableUrl_5, os.environ['AUTH_KEY'], date, 2)
        if not availableRestaurantIds:
            availableRestaurantIds = checkTable(tableUrl_5, os.environ['AUTH_KEY_SECONDARY'], date, 2)
        if not availableRestaurantIds:
            availableRestaurantIds = checkTable(tableUrl_6, os.environ['AUTH_KEY'], date, 2)
        if not availableRestaurantIds:
            availableRestaurantIds = checkTable(tableUrl_6, os.environ['AUTH_KEY_SECONDARY'], date, 2)

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
            printDated("Error, no restaurants found")


if __name__ == '__main__':
    main()
