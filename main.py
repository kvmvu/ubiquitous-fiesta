"""
TODO:
1. Allow user input for max radius and zipcode
2. Get all search results
3. Extract from each result: name, price, vehicle summary and options
4. Save output in .xlsx file
"""
from time import sleep

import pandas as pd
from selenium import webdriver as wb
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select
from tqdm import tqdm

# initialize webdriver

options = wb.ChromeOptions()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"  # path to chrome binary

driver = wb.Chrome('chromedriver', options=options)
driver.get('https://www.tred.com/buy?body_style=&distance=5g0&exterior_color_id=&make=&miles_max=100000&miles_min=0'
           '&model=&page_size=24&price_max=100000&price_min=0&query=&requestingPage=buy&sort=desc&sort_field=updated'
           '&status=active&year_end=2022&year_start=1998&zip=')


def round_off_radius(radius, base=25):
    """
    This function will round off the radius to the nearest 25 miles
    :param base:
    :param radius:
    :return rounded off radius:
    """
    return base * round(radius / base)


def do_search(radius, zipcode):
    """
    This function will select the correct radius from dropdown and input the zipcode. it will then scroll to the end
    of the page. In case the search is unsuccessful, the error message will be displayed
    :return True if successful, False if not:
    """
    # check if radius is greater than 500 miles, if so, assign new radius value as 5000 before doing the search. if
    # less than 25 miles, assign 25 miles
    if radius > 500:
        radius = 5000
    elif radius < 25:
        radius = 25

    # select the radius from dropdown and pass zipcode input
    Select(
        driver.find_element(by='xpath',
                            value='//*[@id="scrollDiv"]/form/div[1]/div[2]/div[1]/select')).select_by_value(
        str(radius))
    driver.find_element(by='xpath', value='//*[@id="scrollDiv"]/form/div[1]/div[2]/div[2]/input').send_keys(
        str(zipcode))

    # scroll to the end of the page
    last_position = driver.execute_script("return window.pageYOffset;")
    scrolling = True

    while scrolling:
        scroll_attempt = 0
        while True:
            # check scroll position
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(2)
            curr_position = driver.execute_script("return window.pageYOffset;")
            if last_position == curr_position:
                scroll_attempt += 1

                # end of scroll region
                if scroll_attempt >= 3:
                    scrolling = False
                    break
                else:
                    sleep(2)  # attempt another scroll
            else:
                last_position = curr_position
                break

    # handle the error if the search is unsuccessful
    try:
        driver.find_element_by_class_name('search-error')
        no_match_found_err_kw = "matching"
        search_error = driver.find_element_by_class_name('search-error').text

        if no_match_found_err_kw in search_error:
            print('Search error:', search_error)
            return False
        else:
            print('Unknown error:', search_error)
            return True
    except NoSuchElementException:
        return True


def get_car_list():
    """
    This function will get the car list if the search is successful
    :return:
    """
    car_list = driver.find_element_by_class_name('inventory').find_elements_by_class_name('card')
    return car_list


def extract_links_from_result(result):
    """
    This function will get a link for each car and extract from each result
    :param result:
    :return list of car links:
    """
    car_links = []
    for car in result:
        gbc = car.find_elements_by_class_name('grid-box-container')
        try:
            car_links.append(gbc[0].find_element_by_tag_name('a').get_attribute('href'))
        except (IndexError, NoSuchElementException):
            pass

    return car_links


def get_car_details_from_link(car_link):
    """
    This function will get the details of each car
    :param car_link:
    :return car details:
    """
    car_details = []
    for i in tqdm(car_link):
        # open the link
        driver.get(i)
        sleep(2)

        try:
            # get the car details
            name = driver.find_element(by='xpath',
                                       value='//*[@id="react"]/div/div/div[2]/div[5]/div[2]/div/h1[1]').text.split(' ')
            if name[0].startswith(str(range(10))):
                name = name[0:-2]
            else:
                name = name[1:-2]
            name = ' '.join(name)
            if driver.find_element(by='xpath', value='//*[@id="header-box"]/div/div/div[2]/div/div/h2'):
                price = driver.find_element(by='xpath', value='//*[@id="header-box"]/div/div/div[2]/div/div/h2').text
            else:
                price = 'N/A'
            summary = driver.find_element(by='xpath',
                                          value='/html/body/section/div/div/div[2]/div[5]/div[2]/div/div['
                                                '5]/div/div/div[ '
                                                '3]/div[1]/table/tbody').text.split('\n')[1:]
            options = driver.find_element(by='xpath', value='//*[@id="options-table"]/tbody').text.split('\n')

            info = {
                'Name': name,
                'Price': price,
                'Vehicle Summary': summary,
                'Vehicle Options': options
            }
            car_details.append(info)
        except (NoSuchElementException, IndexError):
            pass

    return car_details


def save_as_xlsx(results, file_name='car_details.xlsx'):
    """
    This function will save the results as an xlsx file
    :param results:
    :return excel file:
    """
    df = pd.DataFrame(results)
    df.to_excel(file_name, index=False)
    print('Saved as excel file')


def main(radius, zipcode):
    """
    This is the main function
    :return:
    """
    search = do_search(radius, zipcode)
    if search:
        cars = get_car_list()
        links = extract_links_from_result(cars)
        details = get_car_details_from_link(links)
        save_as_xlsx(details)
        print('Done.')


if __name__ == '__main__':
    radius = round_off_radius(int(input('Enter radius: ')))
    zipcode = int(input('Enter zipcode: '))
    main(radius, zipcode)
