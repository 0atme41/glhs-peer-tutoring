from flask import Blueprint, request, render_template
import random
from fpdf import FPDF
import os
import csv

seating_chart_bp = Blueprint('seating_chart', __name__, template_folder="templates", static_folder="static", static_url_path="/seating_chart/static")

def seating_chart(new_student_name):
    rectangles = "static/seating_chart/images/rectangles.svg"
    num_section = int(request.form["num_groups"])
    desk_in_row = int(request.form["num_columns"])
    desk_in_column = int(request.form["num_rows"])
    width = desk_in_row * 460
    height = desk_in_column * 350 * num_section
    with cairo.SVGSurface(rectangles, width, height) as surface:
        context = cairo.Context(surface)
        context.set_source_rgba(0, 0, 0, 1)
        def find_space_name(name, x, y):
            if " " in name:
                space = name.find(" ")
                context.stroke()
                context.move_to(x, y+35)
                context.show_text(name[0:space])
                context.stroke()
                context.move_to(x, y+65)
                context.show_text(name[space+1:])
            elif len(name) >= 12:
                context.stroke()
                context.move_to(x, y+35)
                context.show_text(name[0:11] + "-")
                context.stroke()
                context.move_to(x, y+65)
                context.show_text(name[11:])
            else:
                context.stroke()
                context.move_to(x, y+35)
                context.show_text(name)

        #first and last name
        def desk_name(x, y, name, placement):
            context.move_to(x,y-15)
            context.set_font_size(25)
            context.select_font_face("Arial")
            find_space_name(name[0], x, y-65)
            find_space_name(name[1], x, y)
            context.move_to(x, y+115)
            context.show_text(placement)

        #rectangle
        def rectangle_desk(x, y, x_dash, y_dash):
            context.set_line_width(10)
            context.set_dash([])
            context.rectangle(x, y, 400, 200) #(x, y, width, height)
            context.set_line_join(cairo.LINE_JOIN_BEVEL)
            context.stroke()
            context.set_dash([10.0])
            context.move_to(x_dash, y_dash) #(where,length of line)
            context.line_to(x_dash, y_dash - 200)
            context.stroke()

        #VARIABLES
        sections = "abcdefghijklmnopqurstuvwxyz"
        #desk_number = len(new_student_name)/2   #TOTAL DESKS
        shuffle_or_no = request.form["shuffle"]
        if shuffle_or_no[0].upper() == "Y":
            random.shuffle(new_student_name)
        placement_num_ltr = [1, sections[0].upper()]
        if num_section == 1:
            placement_num_ltr[1] = " "
        place_name_list = []

        #name_place_file = open("static/name_place.txt", "r+")
        x_desk = 30
        y_desk = 90
        x_dash = 225
        y_dash = 285
        x_name = 50
        y_name = 160

        for section in range(num_section):
            if new_student_name == 0:
                break
            placement_num_ltr[0] = 1
            placement_num_ltr[1] = sections[section].upper()
            if num_section == 1:
                placement_num_ltr[1] = " "
            #random.shuffle(main_gym_list)
            if section == 0:
                context.move_to(30,60)
                context.set_font_size(50)
            else:
                y_name += 100
            context.show_text("Section "+ str(sections[section].upper()))
            for column in range(desk_in_column):
                for desk in range(desk_in_row):
                    desks = rectangle_desk(x_desk, y_desk, x_dash, y_dash)
                    x_desk += 450
                    x_dash += 450

                for name in range(desk_in_row*2):
                    if new_student_name != []:
                        name_pop = new_student_name.pop(0)
                        name_on_desk = desk_name(x_name, y_name, name_pop, str(placement_num_ltr[0]))
                        place_name_list.append([[name_pop[1], name_pop[0]], placement_num_ltr[0], placement_num_ltr[1]])
                        placement_num_ltr[0] += 1
                        x_name += 200
                        if name % 2:
                            x_name += 50
                x_dash = 225
                x_desk = 30
                x_name = 50
                y_desk += 250
                y_dash += 250
                y_name += 250
                #if column == desk_in_column:
                #    break
            y_desk += 100
            y_dash += 100
            y_name += 0
            context.move_to(30, y_name)
            context.set_font_size(50)

        context.stroke()
        #print(place_name_list)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size = 12)
        count = 1
        for name in place_name_list:
            pdf.cell(200, 10, txt = str(name[0][0]) + ", " + str(name[0][1]) + " " + str(name[1]) + str(name[2]),
                ln = 5, align = 'L')
            count += 1
        pdf.output("static/seating_chart/images/Roster2.pdf")
        place_name_list.sort()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size = 12)
        count = 1
        for name in place_name_list:
            pdf.cell(200, 10, txt = str(name[0][0]) + ", " + str(name[0][1]) + " " + str(name[1]) + str(name[2]),
                ln = 5, align = 'L')
            count += 1
        pdf.output("static/seating_chart/images/Roster.pdf")
        return render_template("seating_chart/together.html")



@seating_chart_bp.route('/seating-chart-type', methods=['GET', 'POST'])
def seating_chart_type():
    if request.method == "GET":
        return render_template("seating_chart/seating_chart_type.html")

    student_names = request.form["studentsType"]
    new_student_name = student_names.split(",")
    for student in range(len(new_student_name)):
        if new_student_name[student].startswith(" "):
            new_student_name[student] = new_student_name[student][1:]
        new_student_name[student] = new_student_name[student].title()
    for student in range(len(new_student_name)):
        new_student_name[student] = new_student_name[student].split(" ")


    seating_chart_return = seating_chart(new_student_name)
    return seating_chart_return

@seating_chart_bp.route('/seating-chart-upload', methods=['GET', 'POST'])
def seating_chart_upload():
    if request.method == "GET":
        return render_template("seating_chart/seating_chart_upload.html")
    student_names = request.files["studentsUpload"]
    #filename = secure_filename(student_names.filename)
    #basedir = os.path.abspath(os.path.dirname(__file__))
    if student_names.filename != "":
        file_path = os.path.join("static/seating_chart/files", student_names.filename)
        student_names.save(file_path)
    file_path_str = str(file_path)
    period_index = file_path_str.find(".")
    if file_path_str[period_index:] == ".csv":
        with open(file_path, 'r') as file:
          csvreader = csv.reader(file)
          new_student_name = []
          for row in csvreader:
                first_name = row[0]
                last_name = row[1]
                new_student_name.append([first_name.title(), last_name.title()])
    elif file_path_str[period_index:] == ".xlsx":
        pass
    seating_chart_return = seating_chart(new_student_name)
    return seating_chart_return

@seating_chart_bp.route("/seating_chart_main_page")
def seating_chart_main_page():
    return render_template("seating_chart/seating_chart_main_page.html")

@seating_chart_bp.route("/seating_chart_webpage")
def seating_chart_webpage():
    return render_template("seating_chart/seating_chart_webpage.html")
