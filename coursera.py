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
        random_courses_urls = random.sample(all_courses_urls, k=MAX_COURSES)
        return random_courses_urls
    else:
        print("Нет ответа от сервера")


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
        if not soup.find("div", class_="startdate") is None:
            course_info["start_date"] = soup.find("div",
                                            class_="startdate").text
        else:
            course_info["start_date"] = default_info
        if not soup.find_all("div", class_="week") is None:
            course_info["num_of_weeks"] = len(soup.find_all("div",
                                                        class_="week"))
        else:
            course_info["num_of_weeks"] = default_info
        if not soup.find("div", class_="ratings-text") is None:
            course_info["rating"] = soup.find("div",
                                            class_="ratings-text").text
        else:
            course_info["rating"] = default_info

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
    courses_list = get_courses_list(COURSERA_XML_FEED)
    courses_info = []
    for course in courses_list:
        courses_info.append(get_course_info(course))
    output_courses_info_to_xlsx(args.filename, courses_info)
