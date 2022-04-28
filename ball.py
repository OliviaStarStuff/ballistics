"""Written by Olivia from nowhere for studies at the USIC"""

from tkinter import *
import decimal
from typing import Callable
from time import time
import random
from string import hexdigits
import math
from PIL import Image, ImageTk

#actually constants
WINSIZE = 700
WINLENGTH = 1500
SCALES = (0.1, 1, 5, 10, 25, 50)
BG = "#7F3C7F"
BOMB_COUNTER = 0

#actually global variables that shouldn't be
ZOOM = 2
SCALE = SCALES[ZOOM]
SCALE_INTERVAL = WINSIZE//(WINSIZE//100)
GRAVITY = -9.81 * SCALE
MULTIPLIER = 4.23*SCALE**-0.495/1.7
FIXED = False
FIXED_MAG = 200
OY = 0
HEART_TOGGLE = False



"""Helper functions"""
def float_range(start, stop, step):
    """Produces a range from floats"""
    while start < stop:
        yield float(start)
        start += decimal.Decimal(step)

def quad_solver(a, b, c):
    # print(a, b, c)
    res = (-b - math.sqrt(b**2-4*a*c))/(2*a)
    # print(res)
    return res

def get_trajectory(xv, yv ,oy=0, time_step=0.01) -> tuple:
    """generates a tuple of trajectory coordinates"""

    time_taken = (2*(WINSIZE-yv)/MULTIPLIER)/-GRAVITY
    uy = (WINSIZE-yv)/MULTIPLIER
    ux = xv/MULTIPLIER
    # print(OY/SCALE)
    time_taken = quad_solver(GRAVITY/SCALE/2, uy/SCALE, OY/SCALE)
    height = (uy**2) / (-2*GRAVITY) / SCALE + OY/SCALE
    point_y = WINSIZE-1
    traj = []
    point = 0
    while point_y <= WINSIZE+100:
    # for point in float_range(0, time_taken+1, time_step):
        point_x = point * ux
        point_y = WINSIZE - (uy * point + (0.5 * GRAVITY * (point**2))) - oy
        traj.extend([point_x,point_y])
        point += time_step
    return traj, time_taken, height, ux, uy

def TrajectoryGenerator(traj, start):
        diff = 0
        #while diff < end:
        yield traj[round(diff*100)*2], traj[round(diff*100)*2+1]
        diff = time() - start
        while traj[round(diff*100)*2+1] < WINSIZE+10:
            yield traj[round(diff*100)*2], traj[round(diff*100)*2+1]
            diff = time() - start

def normalize_coords(x, y):
        xy_mag = math.sqrt(x**2 + (WINSIZE-y-OY)**2)
        # print(FIXED_MAG,xy_mag, (WINSIZE-y-OY)/xy_mag*FIXED_MAG+OY)

        nx = (x/xy_mag * FIXED_MAG)
        ny = ((WINSIZE-y-OY)/xy_mag * FIXED_MAG)+OY
        # print((1/mag * e.x * 20))
        return nx, WINSIZE-ny

def main() -> None:
    """Build Window"""
    win = Tk()
    win.title("Ballistics test")
    win.geometry(f"{WINLENGTH}x{WINSIZE+28}")
    win.resizable(height = False, width = False)
    win.configure(background=BG)
    # win.wm_attributes("-transparentcolor", "white")
    """Add canvas"""
    canvas=Canvas(win, width=WINLENGTH, height=WINSIZE, highlightthickness=0)
    canvas.config(cursor="none")
    canvas.pack(pady=0)

    # canvas.place(relx=0.5, rely=0.5, anchor=CENTER)

    font = ("Helvetica", 14)
    font2 = ("Helvetica", 10)
    scale_label = []

    """Add vertical scale"""
    for i in range(WINSIZE//100):
         canvas.create_line(0,i*SCALE_INTERVAL,WINLENGTH,i*SCALE_INTERVAL, fill="#DDDDDD")
         scale_label.append(canvas.create_text(5, WINSIZE-SCALE_INTERVAL*i, font=font2, anchor="sw", text=f"{(SCALE_INTERVAL * i) // SCALE:.0f}m"))
    for i in range(1,10):
        scale_label.append(canvas.create_text(WINLENGTH/7.5*i, WINSIZE, font=font2, anchor="sw", text=f"{(WINLENGTH/7.5 * i) // SCALE:.0f}m"))
    """Add interactive lines"""
    force_line = canvas.create_line(0,0,0,0, fill="#FF0000")
    traj_line = canvas.create_line(0,0,0,0, smooth=0, dash = (2, 4))
    mag_circle = canvas.create_oval(0,0,10,10, state="hidden", dash = (8, 255), outline="#FF0000")
    # angle_arc = canvas.create_arc(-50, WINSIZE+50, 50, WINSIZE-50, style= ARC, start=0, extent=80, width=3) does not work
    img = Image.open("heart.png").convert("RGBA")#.resize((20, 20))
    imgtk = ImageTk.PhotoImage(img)

    """Add labels"""
    bomb_counter = canvas.create_text(1495, 0, font=font, anchor="ne", text="Balls Thrown: 0")
    mag_label = canvas.create_text(5, 0, font=font, anchor="nw")
    time_label = canvas.create_text(5, 25, font=font, anchor="nw")
    height_label = canvas.create_text(250, 0, font=font, anchor="nw")
    distance_label = canvas.create_text(250, 25, font=font, anchor="nw")
    norm_label = Label(win, font=font, bg=BG, fg="#ff0", text = "Magnitude Locked")
    angle_label = canvas.create_text(0,0, font=font2, anchor="w", text="")
    instruction_label = Label(win, font=font2, bg=BG, fg="#fff", text="[up/down]: Changes throwing height, [left/right]:changes simulation scale, [LMB]:Throws a ball, [RMB]:Toggles magnitude lock")
    instruction_label.pack(side=RIGHT, anchor="n")
    # exit_button = Button(win, text="Exit", command=win.destroy)
    # exit_button.pack(side=RIGHT, padx=50)

    bullet_list = []

    """Bullet class for shooting"""
    class Bullet:
        def __init__(self, traj: Callable, time_taken, width, canvas, ux, uy) -> None:
            self.start = time()
            self.traj = TrajectoryGenerator(traj, self.start)
            if HEART_TOGGLE:
                self.ball = canvas.create_image(10, 10, anchor=SW, image=imgtk)
            else:
                self.ball = canvas.create_oval(-width, WINSIZE+width,
                                   width+1, WINSIZE-width-1,
                                   fill="#"+"".join(random.choices(hexdigits,k=6)))
            self.width = width
            self.time = canvas.create_text(-width, WINSIZE+width, text="test", anchor="ne")
            self.vy_label = canvas.create_text(-width, WINSIZE+width, text="test", anchor="ne")
            self.traj_line = canvas.create_line(0,0,0,0, smooth=0, dash = (2, 4), fill="#BFBFBF")
            self.ux = ux
            self.uy = uy
            canvas.coords(self.traj_line, 0, WINSIZE, *traj)

        def toggle_heart(self):
            canvas.delete(self.ball)
            if HEART_TOGGLE:
                self.ball = canvas.create_image(10, 10, anchor=S, image=imgtk)
            else:
                self.ball = canvas.create_oval(-self.width, WINSIZE+self.width,
                                   self.width+1, WINSIZE-self.width-1,
                                   fill="#"+"".join(random.choices(hexdigits,k=6)))

        def shooting_after(self):
            try:
                a = self.traj.__next__()
                width = a[0]-self.width
                height = a[1]-self.width
                canvas.moveto(self.ball, width, height)
                canvas.moveto(self.time, width, height-10)
                canvas.moveto(self.vy_label, width, height-20)
                vy = (self.uy + GRAVITY * (time() - self.start))/SCALE
                canvas.itemconfig(self.time, text=f"{time()-self.start:.1f} s")
                canvas.itemconfig(self.vy_label, text=f"{math.sqrt(vy**2 + self.ux**2):.1f}m/s")
                win.after(7, self.shooting_after)
            except StopIteration:
                # print("deleted")
                canvas.delete(self.ball)
                canvas.delete(self.time)
                canvas.delete(self.vy_label)
                canvas.delete(self.traj_line)
                bullet_list.remove(self)

    """All input bindings"""
    def draw_scene(e):
        global traj, time_taken, ux, uy

        x = e.x
        y = e.y
        if FIXED:
            x,y = normalize_coords(x, y)
            # print(x, y, e.x, e.y)
            # if (WINSIZE-y) < OY:
            #     x = FIXED_MAG

        traj, time_taken, height, ux, uy  = get_trajectory(xv=x, yv=y+OY, oy=OY)
        canvas.itemconfig(time_label, text=f"Flight Time: {time_taken:.1f} seconds")
        canvas.itemconfig(mag_label, text=f"Velocity: {math.sqrt(ux**2+uy**2)/SCALE:.3f}m/s")
        canvas.itemconfig(distance_label, text=f"Max Displacement: {time_taken*ux/SCALE:.1f}m")
        canvas.itemconfig(height_label, text=f"Max Height: {height:.1f}m")
        # Calculate angle
        hyp = math.sqrt((WINSIZE-y-OY)**2 + x ** 2)
        if hyp:
            angle =  math.degrees(math.acos(x/hyp))
        else:
            angle = 0
        canvas.itemconfig(angle_label, text=f"{angle:.2f}degrees")


        canvas.coords(force_line, 0, WINSIZE-OY, x, y)
        canvas.coords(angle_label, x/2+5, WINSIZE-(WINSIZE-y+OY)/2)
        canvas.coords(traj_line, *traj)
        # canvas.itemconfig(angle_arc, extent=angle)

    def mouse_pos(e) -> None:
        if isinstance(e.widget.winfo_containing(e.x_root, e.y_root), Canvas):
            draw_scene(e)
        # print(f"Pointer is currently at {e.x}, {e.y}, {canvas.winfo_height()} {type(e.widget.winfo_containing(e.x_root, e.y_root))}")
    def increase_height(e) -> None:
        global OY
        OY += 50
        draw_scene(e)
        # canvas.moveto(angle_arc, 0, WINSIZE-50-OY)
        if FIXED:
            canvas.coords(mag_circle, -FIXED_MAG,WINSIZE+FIXED_MAG-OY,FIXED_MAG,WINSIZE-FIXED_MAG-OY)

    def decrease_height(e) -> None:
        global OY
        OY = max(0, OY-50)
        # canvas.moveto(angle_arc, 0, WINSIZE-50-OY)
        draw_scene(e)
        if FIXED:
            canvas.coords(mag_circle, -FIXED_MAG,WINSIZE+FIXED_MAG-OY,FIXED_MAG,WINSIZE-FIXED_MAG-OY)

    def zoom_out(e) -> None:
        global ZOOM, SCALE, GRAVITY, MULTIPLIER
        ZOOM = min(ZOOM+1, len(SCALES)-1)
        SCALE = SCALES[ZOOM]
        GRAVITY = -9.81 * SCALE
        MULTIPLIER = 4.23*SCALE**-0.495
        draw_scene(e)
        for i,j in enumerate(scale_label):
            if i < WINSIZE//100:
                canvas.itemconfig(j, text=f"{(SCALE_INTERVAL * i) / SCALE:.0f}m")
            else:
                # (WINLENGTH/7.5 * i) // SCALE:.0f}
                canvas.itemconfig(j, text=f"{(WINLENGTH/7.5 * (i-WINSIZE//100+1)) / SCALE:.1f}m")

    def zoom_in(e) -> None:
        global ZOOM, SCALE, GRAVITY, MULTIPLIER
        ZOOM = max(ZOOM-1, 0)
        SCALE = SCALES[ZOOM]
        GRAVITY = -9.81 * SCALE
        MULTIPLIER = 4.23*SCALE**-0.495
        draw_scene(e)
        for i,j in enumerate(scale_label):
            if i < WINSIZE//100:
                canvas.itemconfig(j, text=f"{(SCALE_INTERVAL * i) / SCALE:.0f}m")
            else:
                canvas.itemconfig(j, text=f"{(WINLENGTH/7.5 * (i-WINSIZE//100+1)) / SCALE:.1f}m")

    def toggle_normal(e) -> None:
        global FIXED, FIXED_MAG
        FIXED_MAG =  math.sqrt(e.x**2 + (WINSIZE-e.y-OY)**2)
        FIXED = not FIXED

        if FIXED:
            state = "normal"
            canvas.coords(mag_circle, -FIXED_MAG, WINSIZE+FIXED_MAG-OY, FIXED_MAG, WINSIZE-FIXED_MAG-OY)
            norm_label.pack(side=LEFT, anchor="n")
        else:
            state = "hidden"
            norm_label.pack_forget()
        canvas.itemconfig(mag_circle, state=state)
        draw_scene(e)

    def shoot(e) -> None:
        # print("shoot")
        global traj, time_taken, ux, uy, BOMB_COUNTER
        bullet = Bullet(traj, time_taken, 10, canvas, ux, uy)
        win.after(1, bullet.shooting_after)
        bullet_list.append(bullet)
        BOMB_COUNTER += 1
        canvas.itemconfig(bomb_counter, text=f"Balls thrown: {BOMB_COUNTER}")

    def heart(e) -> None:
        global HEART_TOGGLE
        HEART_TOGGLE = not HEART_TOGGLE
        for i in bullet_list:
            i.toggle_heart()

    win.bind('<Motion>', mouse_pos)
    win.bind('<Up>', increase_height)
    win.bind('<Down>', decrease_height)
    win.bind('<Left>', zoom_in)
    win.bind('<Right>', zoom_out)
    win.bind('n', toggle_normal)
    win.bind('<3>', toggle_normal, add="+")
    win.bind('<1>', shoot)
    win.bind('h', heart)


    """Start window"""
    win.mainloop()

if __name__ == "__main__":
    main()