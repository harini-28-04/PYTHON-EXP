import tkinter as tk
import random

# --- Global Game Constants (remain the same) ---
WIDTH = 1200 
HEIGHT = 500
BALL_SIZE = 15
HORIZONTAL_SPEED = 8
INITIAL_LIVES = 3
GAME_SPEED = 30 

root = None
canvas = None
p1_game = None
p2_game = None

p1_name_entry = None
p1_color_var = None
p2_name_entry = None
p2_color_var = None
setup_frame = None

# --- Game Class Definition (MODIFIED) ---
class PlayerGame:
    def __init__(self, master_canvas, name, color, side_x_offset, control_keys):
        self.canvas = master_canvas
        self.name = name
        self.color = color
        self.offset = side_x_offset
        self.control_keys = control_keys
        
        self.lives = INITIAL_LIVES
        self.score = 0
        self.balls = []
        self.is_moving_left = False
        self.is_moving_right = False
        self.is_active = True
        
        # Player (stick figure) dimensions
        self.player_width = 20 # Width of the body/head
        self.player_height = 40 # Total height of the stick figure
        
        # Starting position for the center of the stick figure's body
        self.player_center_x = self.offset + (WIDTH // 4)
        self.player_base_y = HEIGHT - 10 # Where feet touch ground
        
        # --- Stick Figure Animation State ---
        self.animation_frame = 0 # 0 or 1 for two frames
        self.animation_speed = 3 # Change animation frame every X game loops
        self.animation_counter = 0

        # Draw the player stick figure (initial pose)
        self.player_parts = self.draw_stick_figure(self.player_center_x, self.player_base_y, self.color, self.animation_frame)
        
        # Draw the boundary
        self.canvas.create_rectangle(
            self.offset, 0, self.offset + WIDTH//2, HEIGHT, 
            outline="#444444", width=3
        )
        
        # Display Player Info
        self.canvas.create_text(
            self.offset + 10, 10, anchor="nw", fill="white", font=("Arial", 14, "bold"), 
            text=f"Player: {self.name} ({self.control_keys['left'].upper()}/{self.control_keys['right'].upper()})"
        )
        self.score_text = self.canvas.create_text(
            self.offset + 10, 35, anchor="nw", fill="white", font=("Arial", 14), 
            text=f"Score: {self.score}"
        )
        self.lives_text = self.canvas.create_text(
            self.offset + (WIDTH // 2) - 10, 35, anchor="ne", fill="red", font=("Arial", 14), 
            text=f"Lives: {self.lives}"
        )

        self.bind_controls()
        self.spawn_ball()

    def draw_stick_figure(self, center_x, base_y, color, frame):
        """Draws a simple stick figure based on center_x, base_y, color, and animation frame."""
        head_radius = 8
        body_length = 20
        limb_length = 15
        
        # Head
        head = self.canvas.create_oval(
            center_x - head_radius, base_y - self.player_height,
            center_x + head_radius, base_y - self.player_height + (head_radius * 2),
            fill=color, outline=color
        )
        
        # Body (from neck to hip)
        neck_y = base_y - self.player_height + (head_radius * 2)
        hip_y = neck_y + body_length
        body = self.canvas.create_line(center_x, neck_y, center_x, hip_y, width=2, fill=color)
        
        # Arms (animated)
        if frame == 0: # Pose 1: one arm forward, one back
            # Left Arm (forward)
            arm1 = self.canvas.create_line(center_x, neck_y + 5, center_x - limb_length + 5, neck_y + 5 + limb_length, width=2, fill=color)
            # Right Arm (back)
            arm2 = self.canvas.create_line(center_x, neck_y + 5, center_x + limb_length - 5, neck_y + 5 + limb_length, width=2, fill=color)
        else: # Pose 2: opposite arms forward/back
            # Left Arm (back)
            arm1 = self.canvas.create_line(center_x, neck_y + 5, center_x - limb_length + 5, neck_y + 5 - limb_length, width=2, fill=color)
            # Right Arm (forward)
            arm2 = self.canvas.create_line(center_x, neck_y + 5, center_x + limb_length - 5, neck_y + 5 - limb_length, width=2, fill=color)

        # Legs (animated)
        if frame == 0: # Pose 1: one leg forward, one back
            # Left Leg (forward)
            leg1 = self.canvas.create_line(center_x, hip_y, center_x - 5, base_y, width=2, fill=color)
            # Right Leg (back)
            leg2 = self.canvas.create_line(center_x, hip_y, center_x + 5, base_y, width=2, fill=color)
        else: # Pose 2: opposite legs forward/back
            # Left Leg (back)
            leg1 = self.canvas.create_line(center_x, hip_y, center_x + 5, base_y, width=2, fill=color)
            # Right Leg (forward)
            leg2 = self.canvas.create_line(center_x, hip_y, center_x - 5, base_y, width=2, fill=color)

        return [head, body, arm1, arm2, leg1, leg2]

    def redraw_stick_figure(self, new_center_x):
        """Redraws the stick figure at the new position and updates animation frame."""
        # Delete old parts
        for part in self.player_parts:
            self.canvas.delete(part)
        
        # Update animation frame if moving
        if self.is_moving_left or self.is_moving_right:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_frame = 1 - self.animation_frame # Toggle 0 to 1, or 1 to 0
                self.animation_counter = 0
        else:
            self.animation_frame = 0 # Default pose when standing still
            self.animation_counter = 0

        # Draw new parts
        self.player_parts = self.draw_stick_figure(new_center_x, self.player_base_y, self.color, self.animation_frame)
        self.player_center_x = new_center_x # Update current center_x

    def bind_controls(self):
        root.bind(f'<KeyPress-{self.control_keys["left"]}>', lambda e: self.set_movement(True, True))
        root.bind(f'<KeyRelease-{self.control_keys["left"]}>', lambda e: self.set_movement(False, True))
        root.bind(f'<KeyPress-{self.control_keys["right"]}>', lambda e: self.set_movement(True, False))
        root.bind(f'<KeyRelease-{self.control_keys["right"]}>', lambda e: self.set_movement(False, False))

    def set_movement(self, state, is_left):
        if self.is_active:
            if is_left:
                self.is_moving_left = state
            else:
                self.is_moving_right = state

    def spawn_ball(self):
        if not self.is_active: return

        ball_x = random.randint(self.offset, self.offset + (WIDTH//2) - BALL_SIZE)
        ball_y = 0
        
        ball_obj = self.canvas.create_oval(
            ball_x, ball_y, 
            ball_x + BALL_SIZE, ball_y + BALL_SIZE, 
            fill="red"
        )
        
        speed = random.randint(3, 7)
        self.balls.append({'id': ball_obj, 'speed': speed})
        
        root.after(random.randint(500, 1500), self.spawn_ball)

    def update(self):
        if not self.is_active: return

        # 1. Player Movement
        player_move_x = 0
        if self.is_moving_left:
            player_move_x = -HORIZONTAL_SPEED
        elif self.is_moving_right:
            player_move_x = HORIZONTAL_SPEED
            
        new_player_center_x = self.player_center_x + player_move_x
        
        # Simplified collision check for boundary (using center x)
        # Left boundary (x-offset + half player width)
        min_x = self.offset + (self.player_width / 2)
        # Right boundary (x-offset + half screen width - half player width)
        max_x = self.offset + (WIDTH // 2) - (self.player_width / 2)
        
        # Clamp new_player_center_x within boundaries
        new_player_center_x = max(min_x, min(new_player_center_x, max_x))

        # Redraw player at new position
        self.redraw_stick_figure(new_player_center_x)

        # Get current player coordinates for collision (using calculated bounding box)
        player_x1 = self.player_center_x - (self.player_width / 2)
        player_y1 = self.player_base_y - self.player_height
        player_x2 = self.player_center_x + (self.player_width / 2)
        player_y2 = self.player_base_y
        player_bbox = [player_x1, player_y1, player_x2, player_y2]

        # 2. Ball Movement and Collision
        balls_to_remove = []
        
        for ball_info in self.balls:
            ball_id = ball_info['id']
            self.canvas.move(ball_id, 0, ball_info['speed'])
            ball_coords = self.canvas.coords(ball_id)

            # Check for Hit (Collision with stick figure's bounding box)
            if (ball_coords[2] > player_bbox[0] and ball_coords[0] < player_bbox[2]): # Horizontal overlap
                if (ball_coords[3] > player_bbox[1] and ball_coords[1] < player_bbox[3]): # Vertical overlap
                    self.lives -= 1
                    self.canvas.itemconfig(self.lives_text, text=f"Lives: {self.lives}")
                    balls_to_remove.append(ball_info) 
                    
                    if self.lives <= 0:
                        self.is_active = False
                        return

            # Check for Miss (Scored)
            elif ball_coords[1] > HEIGHT:
                self.score += 1
                self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                balls_to_remove.append(ball_info)
        
        # Clean up balls
        for ball_info in balls_to_remove:
            self.canvas.delete(ball_info['id'])
            self.balls.remove(ball_info)


# --- Rest of the code (Game Management, Setup UI, Application Entry Point) ---
# (These remain the same as the previous full code block)

# --- Game Management Functions ---
def main_game_loop():
    global p1_game, p2_game

    if p1_game and not p1_game.is_active:
        declare_winner(p2_game.name, p2_game.color)
        return
    elif p2_game and not p2_game.is_active:
        declare_winner(p1_game.name, p1_game.color)
        return
    
    if p1_game: p1_game.update()
    if p2_game: p2_game.update()

    root.after(GAME_SPEED, main_game_loop)

def declare_winner(winner_name, winner_color):
    canvas.delete("all")
    
    canvas.create_text(WIDTH/2, HEIGHT/2 - 30, fill="white", 
                       font=("Arial", 50, "bold"), text="GAME OVER")
    
    canvas.create_text(WIDTH/2, HEIGHT/2 + 40, fill=winner_color, 
                       font=("Arial", 40, "bold"), text=f"{winner_name} WINS!")
    
    canvas.create_text(WIDTH/2, HEIGHT/2 + 100, fill="yellow", 
                       font=("Arial", 20), text=f"{p1_game.name}'s Score: {p1_game.score} | {p2_game.name}'s Score: {p2_game.score}")
    
    button_frame = tk.Frame(root, bg="#111111")
    button_frame.place(relx=0.5, rely=0.85, anchor="center")

    tk.Button(
        button_frame, 
        text="Play Again!", 
        command=start_setup, 
        font=("Arial", 20, "bold"), 
        bg="#00ff00", fg="black", activebackground="#00cc00"
    ).pack(padx=20, pady=10)

def start_game():
    global p1_game, p2_game, canvas, root
    
    p1_name = p1_name_entry.get() or "Player 1"
    p1_color = p1_color_var.get()
    p2_name = p2_name_entry.get() or "Player 2"
    p2_color = p2_color_var.get()
    
    if setup_frame:
        setup_frame.destroy()
    
    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#111111")
    canvas.pack(fill="both", expand=True)

    p1_controls = {"left": "a", "right": "d"}
    p2_controls = {"left": "Left", "right": "Right"} 

    p1_game = PlayerGame(canvas, p1_name, p1_color, 0, p1_controls)
    p2_game = PlayerGame(canvas, p2_name, p2_color, WIDTH//2, p2_controls)

    main_game_loop()

# --- Setup UI Functions ---
def start_setup():
    global root, setup_frame, p1_name_entry, p1_color_var, p2_name_entry, p2_color_var
    
    if canvas:
        canvas.destroy()
        
    for widget in root.winfo_children():
        widget.destroy()

    setup_frame = tk.Frame(root, padx=20, pady=20)
    setup_frame.pack()
    
    tk.Label(setup_frame, text="Two-Player Dodge Setup", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
    tk.Label(setup_frame, text="Controls: A/D", font=("Arial", 12)).grid(row=1, column=0, padx=10)
    tk.Label(setup_frame, text="Controls: Left/Right Arrows", font=("Arial", 12)).grid(row=1, column=1, padx=10)

    tk.Label(setup_frame, text="Player 1 Name:", anchor="w").grid(row=2, column=0, sticky="w", pady=5)
    p1_name_entry = tk.Entry(setup_frame)
    p1_name_entry.insert(0, "Neo")
    p1_name_entry.grid(row=3, column=0, padx=5)

    tk.Label(setup_frame, text="Player 1 Color:", anchor="w").grid(row=4, column=0, sticky="w", pady=5)
    p1_color_var = tk.StringVar(root)
    p1_color_var.set("cyan")
    p1_color_menu = tk.OptionMenu(setup_frame, p1_color_var, "red", "blue", "green", "cyan", "magenta", "yellow")
    p1_color_menu.grid(row=5, column=0, padx=5)

    tk.Label(setup_frame, text="Player 2 Name:", anchor="w").grid(row=2, column=1, sticky="w", pady=5)
    p2_name_entry = tk.Entry(setup_frame)
    p2_name_entry.insert(0, "Trinity")
    p2_name_entry.grid(row=3, column=1, padx=5)

    tk.Label(setup_frame, text="Player 2 Color:", anchor="w").grid(row=4, column=1, sticky="w", pady=5)
    p2_color_var = tk.StringVar(root)
    p2_color_var.set("yellow")
    p2_color_menu = tk.OptionMenu(setup_frame, p2_color_var, "red", "blue", "green", "cyan", "magenta", "yellow")
    p2_color_menu.grid(row=5, column=1, padx=5)

    tk.Button(setup_frame, text="Start Duel", command=start_game, font=("Arial", 16, "bold")).grid(row=6, column=0, columnspan=2, pady=20)


# --- Application Entry Point ---
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Dual Screen Dodge Game")
    start_setup()
    root.mainloop()
