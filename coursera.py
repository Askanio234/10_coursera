import random
import argparse
from lxml import etree
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook


COURSERA_XML_FEED = "https://www.coursera.org/sitemap~www~courses.xml"

MAX_COURSES = 20


def get_courses_list(xml_feed):
    request = requests.get(xml_feed)
    if request.status_code == 200:
        document_tree = etree.fromstring(request.content)
        all_courses_urls = [course.getchildren()[0].text
                        for course in document_tree]
        return all_courses_urls
    else:
        print("Нет ответа от сервера")


def choose_random_courses(all_courses, number_of_courses):
    return random.sample(all_courses, k=number_of_courses)


def get_course_info(course_slug):
    course_info = dict()
    default_info = "Not available"
    request = requests.get(course_slug)
    if request.status_code == 200:
        request.encoding = "utf-8"
        soup = BeautifulSoup(request.text, "html.parser")
        course_info["title"] = soup.find("h1",
                                    class_="title display-3-text").text
        course_info["language"] = soup.find("div",
                                    class_="language-info").text
        startdate = soup.find("div", class_="startdate")
        if startdate is None:
            course_info["start_date"] = default_info
        else:
            course_info["start_date"] = startdate.text
        course_length = soup.find_all("div", class_="week")
        if course_length is None:
            course_info["num_of_weeks"] = default_info
        else:
            course_info["num_of_weeks"] = len(course_length)
        course_ratings = soup.find("div", class_="ratings-text")
        if course_ratings is None:
            course_info["rating"] = default_info
        else:
            course_info["rating"] = course_ratings.text

        return course_info

    else:
        print("Нет ответа от сервера")


def output_courses_info_to_xlsx(filepath, courses):
    work_book = Workbook()
    work_sheet = work_book.active
    work_sheet.title = "Courses from coursera"
    work_sheet.append(["Title", "Language", "Start date",
                        "Length(Weeks)", "Rating"])
    for course in courses:
        work_sheet.append([course["title"], course["language"],
                            course["start_date"], course["num_of_weeks"],
                            course["rating"]])
    work_book.save("{}.xlsx".format(filepath))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Имя файла")
    args = parser.parse_args()
    courses_list = choose_random_courses(get_courses_list(COURSERA_XML_FEED),
                                            MAX_COURSES)
    courses_info = [get_course_info(course) for course in courses_list]
    output_courses_info_to_xlsx(args.filename, courses_info)
