import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import datetime
import matplotlib.pyplot as plt
import math
import csv
from itertools import permutations

class RouteManager:
    def __init__(self):
        self.kategoriaA = []
        self.kategoriaB = []
        self.kategoriaC = []
        self.routes = []
        # Update center coordinates to Spodek's location
        self.center = (50.266247, 19.027401)  # Katowice Spodek coordinates
        
        # GUI Setup
        self.root = tk.Tk()
        self.root.title("Route Manager Pro")
        self.root.geometry("650x600")
        
        # Configure styles
        self.setup_styles()
        self.setup_gui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Main.TFrame', background='#f0f0f0')
        style.configure('Header.TLabel', 
                       font=('Helvetica', 12, 'bold'),
                       padding=10,
                       background='#2c3e50',
                       foreground='white')
        
        # Button styles
        style.configure('Action.TButton',
                       padding=10,
                       font=('Helvetica', 10),
                       background='#3498db')
        
        # Frame styles
        style.configure('Card.TLabelframe',
                       background='white',
                       padding=15)
        style.configure('Card.TLabelframe.Label',
                       font=('Helvetica', 11, 'bold'),
                       background='white',
                       foreground='#2c3e50')

    def setup_gui(self):
        # Main container with background
        main_container = ttk.Frame(self.root, style='Main.TFrame', padding="20")
        main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Configure grid weights for centering
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Header centered
        header = ttk.Label(main_container,
                          text="Route Management System",
                          style='Header.TLabel')
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # Notebook centered
        notebook = ttk.Notebook(main_container)
        notebook.grid(row=1, column=0, sticky="nsew")
        
        # Configure main_container grid weights
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # Data Management Tab
        data_tab = ttk.Frame(notebook, padding="15")
        notebook.add(data_tab, text=" Data Management ")
        
        # Center align all frames in data_tab
        data_tab.grid_columnconfigure(0, weight=1)
        data_tab.grid_rowconfigure(1, weight=1)

        # Control Panel centered
        control_frame = ttk.LabelFrame(data_tab,
                                     text="Operations",
                                     style='Card.TLabelframe',
                                     padding="15")
        control_frame.grid(row=0, column=0, padx=5, pady=5)

        # Button group centered
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.grid(row=0, column=0, pady=5)
        
        # Configure button grid weights
        buttons_frame.grid_columnconfigure((0,1), weight=1)
        
        # Center-aligned buttons
        ttk.Button(buttons_frame,
                  text="📂 Load CSV",
                  style='Action.TButton',
                  command=self.load_csv).grid(row=0, column=0, padx=3, pady=2)
        
        ttk.Button(buttons_frame,
                  text="💾 Save Routes",
                  style='Action.TButton',
                  command=self.save_all_routes).grid(row=0, column=1, padx=3, pady=2)
        
        ttk.Button(buttons_frame,
                  text="⚙️ Process",
                  style='Action.TButton',
                  command=self.process_all_routes).grid(row=1, column=0, padx=3, pady=2)
        
        ttk.Button(buttons_frame,
                  text="📊 Plot",
                  style='Action.TButton',
                  command=self.plot_detailed_routes).grid(row=1, column=1, padx=3, pady=2)

        # Results frame centered
        results_frame = ttk.LabelFrame(data_tab,
                                     text="Results",
                                     style='Card.TLabelframe',
                                     padding="10")  # Reduced padding
        results_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=10)
        
        # Configure results frame grid weights
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)

        # Results text area with custom font
        self.result_text = tk.Text(results_frame,
                                 height=15,  # Reduced height
                                 width=50,   # Set explicit width
                                 font=('Consolas', 9),  # Smaller font
                                 bg='#fafafa',
                                 wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame,
                                orient="vertical",
                                command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        results_frame.columnconfigure(0, weight=1)

        # Statistics Tab
        stats_tab = ttk.Frame(notebook, padding="15")
        notebook.add(stats_tab, text=" Statistics ")
        
        stats_frame = ttk.LabelFrame(stats_tab,
                                   text="Route Statistics",
                                   style='Card.TLabelframe',
                                   padding="15")
        stats_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_frame,
                                height=20,
                                font=('Consolas', 10),
                                bg='#fafafa',
                                wrap=tk.WORD)
        self.stats_text.grid(row=0, column=0, sticky="nsew")

        # Route Ordering Tab
        order_tab = ttk.Frame(notebook, padding="15")
        notebook.add(order_tab, text=" Route Order ")
        
        order_frame = ttk.LabelFrame(order_tab,
                                    text="Manual City Reordering",
                                    style='Card.TLabelframe',
                                    padding="15")
        order_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Category and Route selectors
        select_frame = ttk.Frame(order_frame)
        select_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        ttk.Label(select_frame, text="Category:").grid(row=0, column=0, padx=5)
        self.category_var = tk.StringVar(value="A")
        category_combo = ttk.Combobox(select_frame, 
                                     textvariable=self.category_var,
                                     values=["A", "B", "C"],
                                     state="readonly",
                                     width=5)
        category_combo.grid(row=0, column=1, padx=5)
        category_combo.bind('<<ComboboxSelected>>', self.update_route_selector)
        
        ttk.Label(select_frame, text="Route:").grid(row=0, column=2, padx=5)
        self.route_var = tk.StringVar()
        self.route_combo = ttk.Combobox(select_frame,
                                       textvariable=self.route_var,
                                       state="readonly",
                                       width=15)
        self.route_combo.grid(row=0, column=3, padx=5)
        self.route_combo.bind('<<ComboboxSelected>>', self.update_cities_list)
        
        # Cities listbox
        list_frame = ttk.Frame(order_frame)
        list_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        order_frame.rowconfigure(1, weight=1)
        
        self.cities_listbox = tk.Listbox(list_frame,
                                        height=15,
                                        font=('Consolas', 10),
                                        selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_frame,
                                 orient="vertical",
                                 command=self.cities_listbox.yview)
        self.cities_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.cities_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        list_frame.columnconfigure(0, weight=1)
        
        # Control buttons
        btn_frame = ttk.Frame(order_frame)
        btn_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(btn_frame,
                   text="↑ Move Up",
                   command=self.move_city_up).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame,
                   text="↓ Move Down",
                   command=self.move_city_down).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame,
                   text="Apply Changes",
                   command=self.apply_city_changes).grid(row=0, column=2, padx=5)

        # Status bar with custom style
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_container,
                             textvariable=self.status_var,
                             relief="sunken",
                             padding=(5, 2),
                             background='#ecf0f1')
        status_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

    def update_display(self, text):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.update_stats()

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two points on Earth using Haversine formula.
        Returns distance in kilometers.
        """
        R = 6371  # Earth's radius in kilometers

        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

    def calculate_driver_stats(self):
        stats = []
        
        for category, name in [(self.kategoriaA, "A"), (self.kategoriaB, "B"), (self.kategoriaC, "C")]:
            for i, route in enumerate(category):
                if not route:
                    continue
                    
                total_weight = sum(point[2] for point in route if point[3] != "Spodek")
                
                total_distance = 0
                for j in range(len(route)-1):
                    lat1, lon1 = route[j][1], route[j][0]
                    lat2, lon2 = route[j+1][1], route[j+1][0]
                    total_distance += self.haversine_distance(lat1, lon1, lat2, lon2)
                
                stats.append({
                    'category': name,
                    'driver': i+1,
                    'weight': total_weight,
                    'distance': round(total_distance, 2)  # Round to 2 decimal places
                })
        
        return stats

    def generate_maps_url(self, route):
        """Generate Google Maps URL for a given route with return to starting point"""
        if not route:
            return ""
        
        # Start with base URL
        url = "https://www.google.com/maps/dir/"
        
        # Store starting point coordinates (Spodek location)
        start_point = "50.266247,19.027401"  # Spodek coordinates
        
        # Add starting point
        url += f"{start_point}/"
        
        # Add each waypoint
        for point in route:
            # Skip Spodek points as they're just markers
            if point[3] != "Spodek":
                # Google Maps expects coordinates as "lat,lng"
                url += f"{point[1]},{point[0]}/"
        
        # Add return to starting point
        url += f"{start_point}/"
        
        return url

    def update_stats(self):
        driver_stats = self.calculate_driver_stats()
        
        stats = f"""Route Statistics:

Total Routes: {len(self.routes)}
Category A Routes: {len(self.kategoriaA)}
Category B Routes: {len(self.kategoriaB)}
Category C Routes: {len(self.kategoriaC)}

Center Point: {self.center}

Driver Details:
"""
        
        for stat in driver_stats:
            category = stat['category']
            driver_num = stat['driver']
            
            route = None
            if category == 'A' and len(self.kategoriaA) > driver_num-1:
                route = self.kategoriaA[driver_num-1]
            elif category == 'B' and len(self.kategoriaB) > driver_num-1:
                route = self.kategoriaB[driver_num-1]
            elif category == 'C' and len(self.kategoriaC) > driver_num-1:
                route = self.kategoriaC[driver_num-1]
            
            stats += f"""
Category {category} Driver #{driver_num}:
- Total Weight: {stat['weight']} kg
- Total Distance: {stat['distance']} km
"""
            if route:
                arrival_times = self.calculate_arrival_time(route)
                stats += "Estimated arrival times:\n"
                for point, time in zip(route, arrival_times):
                    if point[3] != "Spodek":
                        stats += f"- {point[3]}: {time}\n"
                
                maps_url = self.generate_maps_url(route)
                stats += f"Route Link: {maps_url}\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)

    def update_status(self, text):
        self.status_var.set(text)
        self.root.update_idletasks()

    def odleglosc(self, tupple1, tupple2):
        return math.sqrt((tupple1[0] - tupple2[0])**2 + (tupple1[1] - tupple2[1])**2)

    def kategoryzacja(self, lista):
        self.kategoriaA.clear()
        self.kategoriaB.clear()
        self.kategoriaC.clear()
        
        for krotka in lista:
            dystans = self.odleglosc(krotka[:2], self.center)
            waga = krotka[2]
            
            if 0 <= waga <= 100 and 0 <= dystans <= 50:
                self.kategoriaA.append(krotka)
            elif 100 < waga <= 700 and 25 < dystans <= 120:
                self.kategoriaB.append(krotka)
            else:
                self.kategoriaC.append(krotka)

    def sort1(self, lista):
        if len(lista) == 0:
            return []
        
        # First, separate points with and without time constraints
        time_constrained = []
        no_constraints = []
        
        for point in lista:
            # Check if point has hour information (position 4 in tuple)
            if len(point) > 4 and point[4] == "8:00":
                time_constrained.append(point)
            else:
                no_constraints.append(point)
        
        # Sort time constrained points by distance from center
        time_constrained = sorted(time_constrained, 
                                key=lambda x: self.odleglosc(x[:2], self.center))
        
        # Sort unconstrained points by distance
        no_constraints = sorted(no_constraints, 
                              key=lambda x: self.odleglosc(x[:2], self.center))
        
        # Start with time unconstrained points
        result = no_constraints
        
        # Add time constrained points at the end to ensure they're visited later
        result.extend(time_constrained)
        
        return result

    def calculate_arrival_time(self, route):
        """Calculate estimated arrival times for each point in route"""
        AVERAGE_SPEED = 50  # km/h
        current_time = datetime.datetime.strptime("6:00", "%H:%M")  # Start at 6:00
        arrival_times = []
        
        for i in range(len(route)):
            if i > 0:
                # Calculate travel time from previous point
                distance = self.haversine_distance(
                    route[i-1][1], route[i-1][0],  # prev point
                    route[i][1], route[i][0]        # current point
                )
                travel_time = datetime.timedelta(hours=distance/AVERAGE_SPEED)
                current_time += travel_time
            
            # Check if we arrive too early at time-constrained point
            if len(route[i]) > 4 and route[i][4] == "8:00":
                target_time = datetime.datetime.strptime("8:00", "%H:%M")
                if current_time < target_time:
                    current_time = target_time
                    
            arrival_times.append(current_time.strftime("%H:%M"))
        
        return arrival_times

    def podziel(self, lista, max_waga):
        if len(lista) == 0:
            return []
        
        podlisty = []
        aktualna_podlista = []
        suma_wag = 0
        
        for krotka in lista:
            if suma_wag + krotka[2] <= max_waga:
                aktualna_podlista.append(krotka)
                suma_wag += krotka[2]
            else:
                podlisty.append(list(aktualna_podlista))
                aktualna_podlista = [krotka]
                suma_wag = krotka[2]
        
        if aktualna_podlista:
            podlisty.append(list(aktualna_podlista))
        
        return podlisty

    def sort2(self, lista):
        if len(lista) == 0:
            return []
        
        najlepsze = []
        # Update start point to Spodek coordinates
        start_point = (19.027401, 50.266247, 0, "Spodek")
        
        for podlista in lista:
            min_dist = float('inf')
            najkrotsza = None
            permutacje = permutations(podlista)
            
            for perm in permutacje:
                perm = [start_point] + list(perm) + [start_point]
                dlugosc = sum(self.odleglosc(perm[i][:2], perm[i+1][:2]) for i in range(len(perm)-1))
                if dlugosc < min_dist:
                    min_dist = dlugosc
                    najkrotsza = perm
            
            najlepsze.append(najkrotsza)
        
        return najlepsze

    def load_csv(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if filename:
            self.routes.clear()
            with open(filename, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    self.routes.append((
                        float(row['longitude']),
                        float(row['latitude']),
                        float(row['weight']),
                        row['city'],
                        row['hour']
                    ))
            self.update_display(f"Loaded {len(self.routes)} routes from {filename}")

    def process_all_routes(self):
        self.kategoryzacja(self.routes)
        
        # Process category A
        self.kategoriaA = self.sort1(self.kategoriaA)
        self.kategoriaA = self.podziel(self.kategoriaA, 500)
        self.kategoriaA = self.sort2(self.kategoriaA)
        
        # Process category B
        self.kategoriaB = self.sort1(self.kategoriaB)
        self.kategoriaB = self.podziel(self.kategoriaB, 1500)
        self.kategoriaB = self.sort2(self.kategoriaB)
        
        # Process category C
        self.kategoriaC = self.sort1(self.kategoriaC)
        self.kategoriaC = self.podziel(self.kategoriaC, 10000)
        self.kategoriaC = self.sort2(self.kategoriaC)
        
        self.update_display("Routes processed successfully!")
        self.plot_detailed_routes()

    def save_all_routes(self):
        import os
        
        # Create filename with current date in the same directory as tadam.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        nazwa_pliku = os.path.join(current_dir, f"Trasa_{datetime.date.today()}.txt")
        
        # Get driver statistics
        driver_stats = self.calculate_driver_stats()
        
        with open(nazwa_pliku, "w", encoding='utf-8') as plik:
            # Write general statistics
            plik.write("=== Route Management System Report ===\n")
            plik.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            plik.write(f"Total Routes: {len(self.routes)}\n")
            plik.write(f"Category A Routes: {len(self.kategoriaA)}\n")
            plik.write(f"Category B Routes: {len(self.kategoriaB)}\n")
            plik.write(f"Category C Routes: {len(self.kategoriaC)}\n")
            plik.write(f"Center Point (Spodek): {self.center}\n\n")
            
            # Write detailed route information for each category
            for category, name in [(self.kategoriaA, "A"), (self.kategoriaB, "B"), (self.kategoriaC, "C")]:
                plik.write(f"\n=== Category {name} Routes ===\n")
                
                for i, route in enumerate(category):
                    # Get stats for this route
                    stat = next((s for s in driver_stats if s['category'] == name and s['driver'] == i+1), None)
                    if stat:
                        plik.write(f"\nDriver #{i+1}:\n")
                        plik.write(f"Total Weight: {stat['weight']} kg\n")
                        plik.write(f"Total Distance: {stat['distance']} km\n")
                        
                        # Add arrival times
                        arrival_times = self.calculate_arrival_time(route)
                        plik.write("Estimated arrival times:\n")
                        for point, time in zip(route, arrival_times):
                            if point[3] != "Spodek":
                                plik.write(f"- {point[3]}: {time}\n")
                        
                        # Add route points
                        plik.write("\nRoute sequence:\n")
                        for j, point in enumerate(route):
                            if point[3] != "Spodek":
                                plik.write(f"{j}. {point[3]} - Weight: {point[2]}kg\n")
                        
                        # Add Google Maps link
                        maps_url = self.generate_maps_url(route)
                        plik.write(f"\nGoogle Maps Link:\n{maps_url}\n")
                        plik.write("\n" + "-"*50 + "\n")
            
            self.update_display(f"Routes and statistics saved to {nazwa_pliku}")

    def plot_routes(self):
        plt.figure(figsize=(10, 8))
        
        # Plot categories with different colors
        if self.kategoriaA:
            x, y, _, _, _ = zip(*self.kategoriaA)
            plt.scatter(x, y, c='green', label='Category A')
        if self.kategoriaB:
            x, y, _, _, _ = zip(*self.kategoriaB)
            plt.scatter(x, y, c='blue', label='Category B')
        if self.kategoriaC:
            x, y, _, _, _ = zip(*self.kategoriaC)
            plt.scatter(x, y, c='red', label='Category C')

        plt.scatter(self.center[0], self.center[1], c='black', marker='*', s=200, label='Center')
        plt.legend()
        plt.title('Route Categories')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.grid(True)
        plt.show()

    def plot_detailed_routes(self):
        plt.figure(figsize=(12, 8))
        colors = ['g', 'b', 'r']
        categories = [self.kategoriaA, self.kategoriaB, self.kategoriaC]
        
        # Track min/max coordinates for auto-scaling
        all_x = []
        all_y = []
        
        for cat_idx, category in enumerate(categories):
            for i, route in enumerate(category):
                x = [point[0] for point in route]
                y = [point[1] for point in route]
                all_x.extend(x)
                all_y.extend(y)
                plt.plot(x, y, f'{colors[cat_idx]}-o', label=f'Cat {["A","B","C"][cat_idx]} Route {i+1}')
                
                for j, point in enumerate(route):
                    if len(point) >= 4 and point[3] != "Spodek":
                        plt.text(point[0], point[1], 
                                f'{j}, {point[3]}', 
                                fontsize=9,
                                verticalalignment='bottom',
                                horizontalalignment='right')
                    elif point[3] == "Spodek":
                        plt.text(point[0], point[1],
                                'Spodek',
                                fontsize=9,
                                verticalalignment='bottom',
                                horizontalalignment='right')

        plt.scatter(self.center[0], self.center[1], c='black', marker='*', s=200, label='Center')
        
        # Auto-scale the plot with padding
        if all_x and all_y:
            x_min, x_max = min(all_x), max(all_x)
            y_min, y_max = min(all_y), max(all_y)
            x_padding = (x_max - x_min) * 0.1
            y_padding = (y_max - y_min) * 0.1
            plt.xlim(x_min - x_padding, x_max + x_padding)
            plt.ylim(y_min - y_padding, y_max + y_padding)

        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.title('Detailed Routes')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.grid(True)
        plt.tight_layout()  # Adjust layout to prevent text cutoff
        plt.show()

    def update_route_selector(self, event=None):
        category = self.category_var.get()
        routes = self._get_current_category()
        
        # Update route selector with available routes
        route_options = [f"Route {i+1}" for i in range(len(routes))]
        self.route_combo['values'] = route_options
        if route_options:
            self.route_combo.set(route_options[0])
            self.update_cities_list()
        else:
            self.route_combo.set('')
            self.cities_listbox.delete(0, tk.END)

    def update_cities_list(self, event=None):
        self.cities_listbox.delete(0, tk.END)
        
        category = self.category_var.get()
        routes = self._get_current_category()
        
        if not routes or not self.route_var.get():
            return
        
        route_idx = int(self.route_var.get().split()[-1]) - 1
        if 0 <= route_idx < len(routes):
            route = routes[route_idx]
            for point in route:
                if point[3] != "Spodek":
                    self.cities_listbox.insert(tk.END, point[3])

    def move_city_up(self):
        selected = self.cities_listbox.curselection()
        if not selected or selected[0] == 0:
            return
        
        idx = selected[0]
        category = self.category_var.get()
        route_idx = int(self.route_var.get().split()[-1]) - 1
        routes = self._get_current_category()
        
        route = [p for p in routes[route_idx] if p[3] != "Spodek"]
        
        # Swap cities
        route[idx], route[idx-1] = route[idx-1], route[idx]
        
        start_point = (19.28, 50.59, 0, "Spodek")
        routes[route_idx] = [start_point] + route + [start_point]
        
        # Update display
        self.update_cities_list()
        self.cities_listbox.selection_set(idx-1)

    def move_city_down(self):
        selected = self.cities_listbox.curselection()
        if not selected or selected[0] >= self.cities_listbox.size() - 1:
            return
        
        idx = selected[0]
        route_idx = int(self.route_var.get().split()[-1]) - 1
        routes = self._get_current_category()
        
        route = [p for p in routes[route_idx] if p[3] != "Spodek"]
        route[idx], route[idx+1] = route[idx+1], route[idx]
        
        start_point = (19.28, 50.59, 0, "Spodek")
        routes[route_idx] = [start_point] + route + [start_point]
        
        # Update display
        self.update_cities_list()
        self.cities_listbox.selection_set(idx+1)

    def apply_city_changes(self):
        self.update_stats()
        self.update_display("City order updated successfully!")

    def update_route_list(self, event=None):
        self.route_listbox.delete(0, tk.END)
        category = self.category_var.get()
        routes = []
        
        if category == "A":
            routes = self.kategoriaA
        elif category == "B":
            routes = self.kategoriaB
        else:
            routes = self.kategoriaC
        
        for i, route in enumerate(routes):
            cities = [point[3] for point in route if point[3] != "Spodek"]
            self.route_listbox.insert(tk.END, f"Route {i+1}: {' -> '.join(cities)}")

    def move_route_up(self):
        selected = self.route_listbox.curselection()
        if not selected or selected[0] == 0:
            return
        
        idx = selected[0]
        category = self.category_var.get()
        routes = self._get_current_category()
        
        # Swap routes
        routes[idx], routes[idx-1] = routes[idx-1], routes[idx]
        
        # Update display
        self.update_route_list()
        self.route_listbox.selection_set(idx-1)

    def move_route_down(self):
        selected = self.route_listbox.curselection()
        if not selected or selected[0] >= self.route_listbox.size() - 1:
            return
        
        idx = selected[0]
        routes = self._get_current_category()
        
        # Swap routes
        routes[idx], routes[idx+1] = routes[idx+1], routes[idx]
        
        # Update display
        self.update_route_list()
        self.route_listbox.selection_set(idx+1)

    def _get_current_category(self):
        category = self.category_var.get()
        if category == "A":
            return self.kategoriaA
        elif category == "B":
            return self.kategoriaB
        return self.kategoriaC

    def apply_route_changes(self):
        self.update_stats()
        self.update_display("Route order updated successfully!")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = RouteManager()
    app.run()