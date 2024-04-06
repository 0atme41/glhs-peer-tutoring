import cairo
import os
import random

class Desk():
    '''Represents desk coordinates and student names'''

    def __init__(self,x,y,ln1,fn1,ln2,fn2,seat,context_in): # Initialization of attributes
        self.x = x
        self.y = y
        self.ln1 = ln1
        self.fn1 = fn1
        self.ln2 = ln2
        self.fn2 = fn2
        self.midx = x + 150
        self.midy = y + 100
        self.seat1 = str(seat)
        self.seat2 = str(seat + 1)
        self.endx = x + 300
        self.context = context_in

    
    def draw_rect(self): # Desk Outline
        self.context.set_dash([1,0])
        self.context.rectangle(self.x,self.y,300,100)
        self.context.stroke()

    def draw_nums(self): # Desk Numbers, logic ensures alignment to top right corner based on size
        if len(self.seat1) == 1:
            x_offset_1 = 14
        elif len(self.seat1) == 2:
            x_offset_1 = 20
        else:
            x_offset_1 = 30
        if len(self.seat2) == 1:
            x_offset_2 = 14
        elif len(self.seat2) == 2:
            x_offset_2 = 20
        else:
            x_offset_2 = 30
        self.context.move_to(self.midx-x_offset_1,self.y+15)
        self.context.show_text(self.seat1)
        self.context.stroke()
        self.context.move_to(self.endx-x_offset_2,self.y+15)
        self.context.show_text(self.seat2)
        self.context.stroke()
    
    def draw_dash(self): # Draws dash separator between halves of desk
        self.context.set_dash([5])
        self.context.move_to(self.midx,self.y)
        self.context.line_to(self.midx,self.midy)
        self.context.stroke()

    def name_1(self): # Draws first name, logic checks for 2 names, if is 2 splits between lines
        self.context.move_to(self.x+10,self.y+30)
        if ' ' not in self.ln1:
            self.context.show_text(self.ln1)
            self.context.stroke()
        else:
            ln_split = self.ln1.split(' ')
            self.context.show_text(ln_split[0])
            self.context.move_to(self.x+10,self.y+45)
            self.context.show_text(ln_split[1])
        
        self.context.move_to(self.x+10,self.y+70)
        if ' ' not in self.fn1:  
            self.context.show_text(self.fn1)
            self.context.stroke()
        else:
            fn_split = self.fn1.split(' ')
            self.context.show_text(fn_split[0])
            self.context.move_to(self.x+10,self.y+85)
            self.context.show_text(fn_split[1])
            self.context.stroke()
    
    def name_2(self): # Draws second name, logic checks for 2 names, if is 2 splits between lines
        self.context.move_to(self.midx+10,self.y+30)

        if ' ' not in self.ln2:
            self.context.show_text(self.ln2)
            self.context.stroke()
        else:
            ln_split = self.ln2.split(' ')
            self.context.show_text(ln_split[0])
            self.context.move_to(self.midx+10,self.y+45)
            self.context.show_text(ln_split[1])
            self.context.stroke()

        self.context.move_to(self.midx+10, self.y+70)
        if ' ' not in self.fn2:
            self.context.show_text(self.fn2)
            self.context.stroke()
        else:
            fn_split = self.fn2.split(' ')
            self.context.show_text(fn_split[0])
            self.context.move_to(self.midx+10,self.y+85)
            self.context.show_text(fn_split[1])
            self.context.stroke()
    
    def names(self): # Draws both names
        self.name_1()
        self.name_2()

    def full(self): # Full desk drawing
        self.draw_rect()
        self.draw_nums()
        self.draw_dash()
        self.names()
    
    def student_data_entry_1(self): # Formats right student's data for output
        return self.ln1 + ', ' + self.fn1 + ' ' + self.seat1

    def student_data_entry_2(self): # Formats left student's data for output
        return self.ln2 + ', ' + self.fn2 + ' ' + self.seat2

def row_loop(col_lim_in,seat_num_in,y_offset_in,context_in): # Iterates through students to make a row of desks
    student_entries = []
    for x in range(col_lim_in): # Makes number of desks that fit within limit
        student = students_list.pop(0)
        ln1 = student[0]
        fn1 = student[1]

        student = students_list.pop(0)
        ln2 = student[0]
        fn2 = student[1]

        h_offset = 310 * x + 5

        desk_obj = Desk(h_offset,y_offset_in,ln1,fn1,ln2,fn2,seat_num_in,context_in) # Creates desk object
        desk_obj.full() # Draws desk with method of desk object
        seat_num_in += 2
        student_entries.append(desk_obj.student_data_entry_1()) # Updates student location list
        student_entries.append(desk_obj.student_data_entry_2()) # Updates student location list
    return student_entries
   
def room_loop(rooms_list): # Iterates through 
    student_locations_out = []
    for i in rooms_list:
        global students_list
        students_list = students_create(i[0])

        room_name = i[1]
        col_lim = i[2]
        row_lim = i[3]
        row_num = 0
        seat_num = 1

        print(room_name,str(col_lim),str(row_lim))

        with cairo.SVGSurface(room_name,col_lim*310 + 5,row_lim*110 + 5) as surface: # Creates canvas, size based on # of rows/columns
            context = cairo.Context(surface)
            context.set_source_rgba(0,0,0,1)
            context.set_line_width(4)
            context.set_line_join(cairo.LINE_JOIN_MITER)
            context.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            context.set_font_size(16)

            try:
                while students_list: # Until student list is empty, makes rows
                    y_offset = row_num * 110 + 5
                    row_num += 1
                    
                    if row_num == row_lim + 1: # Stops creating rows after max # are created
                        break
                    
                    new_entries = row_loop(col_lim,seat_num,y_offset,context) # Inputs
                    for i in new_entries:
                        student_locations_out.append(i + ' ' + room_name)
                    seat_num += col_lim * 2
            except:
                pass
    return student_locations_out

def students_create(file_name):
    ''' Imports .csv file, returns list of names in random order'''
    roster = open(file_name,'r+')
    roster_lines = roster.readlines()
    students = []
    for i in roster_lines:
        sep = i.find(',')
        students.append([i[0:sep],i[sep+1:].strip(',\n')]) # Splits by comma into first and last name ('Doe, John' into ['Doe','John'])
    roster.close()
    random.shuffle(students)
    return students

rooms = [['PSAT Main Gym Roster.csv','Main Gym',10,16],['PSAT Aux Gym Roster.csv','Aux Gym',5,14]]

student_locations = room_loop(rooms)
student_locations.sort()
print(student_locations)

student_index = open('Student Index.txt','w+')

for i in range(len(student_locations)):
    student_index.write('{:5<}. {}\n'.format(i+1,student_locations[i]))