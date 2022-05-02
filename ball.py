"""Written by Olivia from nowhere for studies at the USIC"""
from __future__ import generators
from email import generator
from itertools import chain
import math
from time import time
from tkinter import (N, NE, NW, W, SW, S, RIGHT, LEFT,
                     Tk, Canvas, Event, Label, Button)
import random
from string import hexdigits
from typing import Generator

from PIL import Image, ImageTk

from vector import Trajectory, Vec2


"""constants"""
WINSIZE = 700
WINLENGTH = 1500
SCALES = (0.1, 1, 5, 10, 25, 50)
SCALE_INTERVAL = WINSIZE//(WINSIZE//100)
BG = "#7F3C7F"
WIN = Tk()
CANVAS = Canvas(WIN, width=WINLENGTH, height=WINSIZE, highlightthickness=0)
HEART = ImageTk.PhotoImage(Image.open("heart.png").convert("RGBA"))#.resize((20, 20))


"""Helper functions"""
def quad_solver(a: float, b: float, c: float) -> float:
    """Quadratic Equation the finds positive x"""
    positive_x = (-b - math.sqrt(b**2-4*a*c)) / (2*a)
    return positive_x


def TrajectoryGenerator(traj: list[Vec2],
        start: float) -> Generator[tuple[float, float], float, None]:
    """generates the next set of x,y points for an object"""
    diff = 0
    yield traj[round(diff*100)].x, traj[round(diff*100)].y
    diff = time() - start
    while traj[round(diff*100)].y < (WINSIZE + 10):
        yield traj[round(diff*100)].x, traj[round(diff*100)].y
        diff = time() - start


def get_trajectory(force: Vec2,
    oy: int=0, multiplier: float = 1.0, scale: float = 1.0,
    gravity: float = -9.81, time_step: float = 0.01
    ) -> Trajectory:
    """generates a tuple of trajectory coordinates"""
    mod_force = force.s_div(multiplier)
    time_taken = quad_solver(gravity/2, mod_force.y, oy) # 0 = at^2/2 +ut-s
    height = ((mod_force.y**2) / (-2*gravity) + oy) / scale # s = -u^2/(2a) + c
    point_y = WINSIZE-1
    traj = []
    point = 0
    while point_y <= WINSIZE+100:
        point_x = point * mod_force.x
        point_y = WINSIZE - (mod_force.y * point
                             + (0.5 * gravity * (point**2))) - oy
        traj.append(Vec2(point_x, point_y))
        point += time_step
    return Trajectory(traj, time_taken, height, mod_force)


def find_angle(x:float, y:float) -> float:
    return math.degrees(math.asin(y/math.hypot(x, y)))


"""Classes"""
class Game:
    fonts = (("Helvetica", 14), ("Helvetica", 10))
    def __init__(self, zoom: int = 2) -> None:
        """Set up variables"""
        self.zoom = zoom
        self.scale = SCALES[self.zoom]
        self.gravity = -9.81 * self.scale
        self.multiplier = 4.23 * self.scale ** -0.495/1.7
        self.fixed = False
        self.fixed_mag = 200.0
        self.oy = 0
        self.heart_toggle = False
        self.angle_lock = False
        self.bomb_counter = 0
        self.scale_label: list = []
        self.lines: dict = {}
        self.labels: dict = {}
        self.traj: Trajectory = None
        self.bullet_list: list[Bullet] = []

        self._configure_window()
        self._populate_scales()
        self._create_lines()
        self._create_labels()
        self._add_key_bindings()

    def start(self) -> None:
        WIN.mainloop()

    """Setup methods"""
    def _configure_window(self) -> None:
        WIN.title("Ballistics test")
        WIN.geometry(f"{WINLENGTH}x{WINSIZE+28}")
        WIN.resizable(height = False, width = False)
        WIN.configure(background=BG)
        # CANVAS.config(cursor="none")
        CANVAS.pack(pady=0)

    def _populate_scales(self) -> None:
        for i in range(WINSIZE//100):
            CANVAS.create_line(0, i*SCALE_INTERVAL, WINLENGTH,
                               i*SCALE_INTERVAL, fill="#DDDDDD")
            self.scale_label.append(
                CANVAS.create_text(
                    5, WINSIZE-SCALE_INTERVAL*i,
                    font=self.fonts[1], anchor="sw",
                    text=f"{(SCALE_INTERVAL * i) // self.scale:.0f}m"))
        for i in range(1,10):
            self.scale_label.append(
                CANVAS.create_text(
                    WINLENGTH/7.5*i, WINSIZE,
                    font=self.fonts[1], anchor="sw",
                    text=f"{(WINLENGTH/7.5 * i) // self.scale:.0f}m"))

    def _create_lines(self) -> None:
        self.lines["force"] = CANVAS.create_line(0, 0, 0, 0, fill="#FF0000")
        self.lines["traj"] = CANVAS.create_line(0, 0, 0, 0, smooth=0,
                                                dash=(2, 4))
        self.lines["mag_circle"] = CANVAS.create_oval(0, 0, 10, 10,
                                                      state="hidden",
                                                      dash=(8, 255),
                                                      outline="#FF0000")

    def _create_labels(self) -> None:
        self.labels["bomb"] = CANVAS.create_text(1495, 0, font=self.fonts[0],
                                                 anchor=NE,
                                                 text="Balls Thrown: 0")
        self.labels["mag"] = CANVAS.create_text(5, 0, font=self.fonts[0],
                                                anchor=NW)
        self.labels["time"] = CANVAS.create_text(5, 25, font=self.fonts[0],
                                                 anchor=NW)
        self.labels["height"] = CANVAS.create_text(250, 0, font=self.fonts[0],
                                                   anchor=NW)
        self.labels["distance"] = CANVAS.create_text(250, 25,
                                                     font=self.fonts[0],
                                                     anchor=NW)
        self.labels["norm"] = Label(WIN, font=self.fonts[0], bg=BG, fg="#ff0",
                                    text = "Magnitude Locked")
        self.labels["angle"] = CANVAS.create_text(0, 0, font=self.fonts[1],
                                                  anchor=W, text="")
        self.labels["instruction"] = Label(
            WIN, font=self.fonts[1], bg=BG, fg="#fff",
            text="[up/down]: Changes throwing height, [left/right]:changes"\
                "simulation scale, [LMB]:Throws a ball,"\
                "[RMB]:Toggles magnitude lock")
        self.labels["instruction"].pack(side=RIGHT, anchor=N)
        # print(self.labels)
        exit_button = Button(WIN, text="Exit", command=WIN.destroy)
        exit_button.pack(side=RIGHT, padx=50)

    def _add_key_bindings(self) -> None:
        WIN.bind('<Motion>', self._mouse_pos)
        WIN.bind('<Up>', self._increase_height)
        WIN.bind('<Down>', self._decrease_height)
        WIN.bind('<Left>', self._zoom_in)
        WIN.bind('<Right>', self._zoom_out)
        WIN.bind('n', self._toggle_normal)
        WIN.bind('<3>', self._toggle_normal, add="+")
        WIN.bind('<1>', self._shoot)
        WIN.bind('h', self._heart)
        WIN.bind('a', self._toggle_angle)

    """All input bindings"""
    def _draw_scene(self, e: Event) -> None:
        """Updates the UI"""
        o_height = WINSIZE-self.oy
        force = Vec2(e.x, WINSIZE-e.y-self.oy)
        angle = find_angle(*force)
        if self.angle_lock and angle < 0:
            force.y = 0
            angle = 0
        if self.fixed:
            force.normalize(self.fixed_mag)

        self.traj = get_trajectory(force, self.oy, self.multiplier,
                                     self.scale, self.gravity)

        CANVAS.itemconfig(self.labels["time"],
            text=f"Flight Time: {self.traj.time_taken:.1f} seconds")
        magnitude = self.traj.velocity.magnitude()/self.scale
        CANVAS.itemconfig(self.labels["mag"],
                          text=f"Velocity: {magnitude:.3f}m/s")
        distance = self.traj.time_taken*self.traj.velocity.x/self.scale
        CANVAS.itemconfig(self.labels["distance"],
                          text=f"Max Displacement: {distance:.1f}m")
        CANVAS.itemconfig(self.labels["height"],
                          text=f"Max Height: {self.traj.height:.1f}m")

        CANVAS.itemconfig(self.labels["angle"], text=f"{angle:.2f}degrees")

        CANVAS.coords(self.lines["force"], 0,
                      o_height, force.x, o_height-force.y)
        CANVAS.coords(self.labels["angle"], force.x/2+5,
                      o_height-(force.y)/2)
        CANVAS.coords(self.lines["traj"],
                      *chain.from_iterable(self.traj.points))

    def _mouse_pos(self, e: Event) -> None:
        """On mouse movement on Canvas"""
        if isinstance(e.widget.winfo_containing(e.x_root, e.y_root), Canvas):
            self._draw_scene(e)

    def _increase_height(self, e: Event) -> None:
        """Move gun up"""
        self.oy += 50
        self._draw_scene(e)
        self._update_mag_circle(e)

    def _decrease_height(self, e: Event) -> None:
        """Move gun down"""
        self.oy = max(0, self.oy-50)
        self._update_mag_circle(e)

    def _update_mag_circle(self, e: Event) -> None:
        """Move Mag circle up if magnitude is fixed"""
        self._draw_scene(e)
        if self.fixed:
            CANVAS.coords(self.lines["mag_circle"], -self.fixed_mag,
                WINSIZE+self.fixed_mag-self.oy, self.fixed_mag,
                WINSIZE-self.fixed_mag-self.oy)

    def _zoom_out(self, e: Event) -> None:
        self.zoom = min(self.zoom+1, len(SCALES)-1)
        self._update_scale(e)

    def _zoom_in(self, e: Event) -> None:
        self.zoom = max(self.zoom-1, 0)
        self._update_scale(e)

    def _update_scale(self, e: Event) -> None:
        self.scale = SCALES[self.zoom]
        self.gravity = -9.81 * self.scale
        self.multiplier = 4.23 * self.scale ** -0.495
        self._draw_scene(e)
        for i,j in enumerate(self.scale_label):
            if i < WINSIZE//100:
                text = (SCALE_INTERVAL * i) / self.scale
                CANVAS.itemconfig(j, text=f"{text:.0f}m")
            else:
                text = (WINLENGTH/7.5 * (i-WINSIZE//100+1)) / self.scale
                CANVAS.itemconfig(j, text=f"{text:.1f}m")

    def _toggle_normal(self, e: Event) -> None:
        self.fixed_mag =  math.sqrt(e.x**2 + (WINSIZE-e.y-self.oy)**2)
        self.fixed = not self.fixed

        if self.fixed:
            state = "normal"
            CANVAS.coords(self.lines["mag_circle"], -self.fixed_mag,
                          WINSIZE+self.fixed_mag-self.oy, self.fixed_mag,
                          WINSIZE-self.fixed_mag-self.oy)
            self.labels["norm"].pack(side=LEFT, anchor="n")
        else:
            state = "hidden"
            self.labels["norm"].pack_forget()
        CANVAS.itemconfig(self.lines["mag_circle"], state=state)
        self._draw_scene(e)

    def _toggle_angle(self, e: Event) -> None:
        self.angle_lock = not self.angle_lock
        self._draw_scene(e)

    def _shoot(self, e: Event) -> None:
        bullet = Bullet(self, self.traj.points, 10, self.traj.velocity)
        WIN.after(1, bullet.shooting_after)
        self.bullet_list.append(bullet)
        self.bomb_counter += 1
        CANVAS.itemconfig(self.labels["bomb"],
                          text=f"Balls thrown: {self.bomb_counter}")

    def _heart(self, e: Event) -> None:
        self.heart_toggle = not self.heart_toggle
        for i in self.bullet_list:
            i.toggle_heart()


class Bullet:
    def __init__(self, game: Game, traj: list[Vec2],
                 width: int, velocity: Vec2) -> None:
        self.start = time()
        self.traj = TrajectoryGenerator(traj, self.start)
        if game.heart_toggle:
            self.ball = CANVAS.create_image(10, 10, anchor=SW, image=HEART)
        else:
            self.ball = CANVAS.create_oval(
                -width, WINSIZE+width, width+1, WINSIZE-width-1,
                fill="#"+"".join(random.choices(hexdigits,k=6)))
        self.width = width
        self.time = CANVAS.create_text(-width, WINSIZE+width, text="test",
                                       anchor=NE)
        self.vy_label = CANVAS.create_text(-width, WINSIZE+width, text="test",
                                           anchor=NE)
        self.traj_line = CANVAS.create_line(0, 0, 0, 0, smooth=0, dash=(2, 4),
                                            fill="#BFBFBF")
        self.velocity = velocity
        self.game = game
        CANVAS.coords(self.traj_line, 0, WINSIZE,
                      *chain.from_iterable(traj))

    def toggle_heart(self):
        """replaces the represenatation of the bullet with a heart"""
        CANVAS.delete(self.ball)
        if self.game.heart_toggle:
            self.ball = CANVAS.create_image(10, 10, anchor=S, image=HEART)
        else:
            self.ball = CANVAS.create_oval(-self.width, WINSIZE+self.width,
                self.width+1, WINSIZE-self.width-1,
                fill="#"+"".join(random.choices(hexdigits,k=6)))

    def shooting_after(self):
        """Moves the bullet after a certain amount of time"""
        try:
            a = self.traj.__next__()
            width = a[0]-self.width
            height = a[1]-self.width
            CANVAS.moveto(self.ball, width, height)
            CANVAS.moveto(self.time, width, height-10)
            CANVAS.moveto(self.vy_label, width, height-20)
            vy = (self.velocity.y
                  + self.game.gravity
                  * (time() - self.start)) / self.game.scale
            CANVAS.itemconfig(self.time, text=f"{time()-self.start:.1f} s")
            CANVAS.itemconfig(
                self.vy_label,
                text=f"{math.sqrt(vy**2 + self.velocity.x**2):.1f}m/s")
            WIN.after(7, self.shooting_after)
        except StopIteration:
            CANVAS.delete(self.ball)
            CANVAS.delete(self.time)
            CANVAS.delete(self.vy_label)
            CANVAS.delete(self.traj_line)
            self.game.bullet_list.remove(self)


def main() -> None:
    game = Game()
    """Start window"""
    game.start()


if __name__ == "__main__":
    main()