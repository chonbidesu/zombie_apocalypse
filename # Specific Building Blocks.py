# Specific Building Blocks
class NecroTechLab(BuildingBlock):
    def __init__(self, block_name="Empty Nec"):
        super().__init__(block_name, block_type="NecroTechLab", find_probabilities={"Weapon": 0.3, "Tool": 0.2, "Medicine": 0.4, "Material": 0.1})
        self.block_desc = "NecroTech lab"

        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation("The once-sterile environment is now a chaotic mess. Lab equipment is overturned, with shattered glass and rusted metal strewn across the floor. The NecroTech logo is barely visible on the walls, faded and peeling. Refrigerators and medical cabinets are left open, their contents long expired or spilled. Papers and research notes are scattered about, some partially burned, some disintegrated by age, all hinting at dark experiments gone wrong.")
        self.add_outside_observation("The sleek, modern building has long since lost its corporate sheen. The logo of NecroTech, once glowing bright, is now just a fading shadow on the facade. The building stands isolated, windows dark, with the remnants of security fencing hanging loosely as the place crumbles under years of neglect.")
        self.update_observations()  # Populate the initial observations.


class Mall(BuildingBlock):
    def __init__(self, block_name="Empty Mall"):
        super().__init__(block_name, block_type="Mall", find_probabilities={"Food": 0.3, "Material": 0.2, "Weapon": 0.1, "Tool": 0.4})
        self.block_desc = "mall"
        
                # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "Once a bustling center of commerce, it now stands in eerie silence. Shattered glass from broken storefronts litters the floor, and empty shelves are left half-toppled or stripped bare. The remnants of old advertisements cling to the walls, faded and peeling. The food court area is overrun with mold, the stench of decay heavy in the air. In the distance, the flickering lights of the few still-functioning power sources give the place an unsettling, half-alive glow."
        )
        self.add_outside_observation(
            "The massive building towers over the surrounding ruins, its once-glittering windows now cracked and boarded up. The signs for once-popular stores are barely legible, their colors washed out by years of neglect. An eerie stillness hangs in the air as you approach, broken only by the occasional creak of a structural beam shifting in the wind."
        )
        self.update_observations()  # Populate the initial observations.


class FireStation(BuildingBlock):
    def __init__(self, block_name="Empty FireStation"):
        super().__init__(block_name, block_type="FireStation", find_probabilities={"Tool": 0.3, "Medicine": 0.1, "Food": 0.15})
        self.block_desc = "fire station"
        
        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "The shelves once lined with emergency equipment are now empty or rusted. Old fire suits hang in tatters, and the scent of smoke lingers in the air. Broken fire trucks sit in the garage, their engines long dead, with tires flat and doors hanging ajar."
        )
        self.add_outside_observation(
            "The once-bright red building is now faded and chipped, with rusted fire trucks abandoned outside. The windows are broken, and the structure appears to be slowly sinking into the earth, overtaken by time and decay."
        )
        self.update_observations()  # Populate the initial observations.


class PoliceDepartment(BuildingBlock):
    def __init__(self, block_name="Empty PoliceDepartment"):
        super().__init__(block_name, block_type="PoliceDepartment", find_probabilities={"Weapon": 0.4, "Tool": 0.2, "Food": 0.1})
        self.block_desc = "police station"
        
        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "The desks are overturned, and the cabinets that once held weapons and important files are now emptied and broken. The holding cells are rusted shut, with only shadows and dust remaining. A few old uniforms hang in disarray, and the air is thick with the smell of mildew and rot."
        )
        self.add_outside_observation(
            "The building is a hulking shell, with barred windows and a faded sign reading 'Police'. The front steps are cracked, and the doors hang loosely, offering an eerie view into the abandoned interior."
        )
        self.update_observations()  # Populate the initial observations.


class Warehouse(BuildingBlock):
    def __init__(self, block_name="Empty Warehouse"):
        super().__init__(block_name, block_type="Warehouse", find_probabilities={"Tool": 0.4, "Food": 0.3, "Material": 0.2})
        self.block_desc = "warehouse"     
        
        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "Large, rusted crates and pallets are scattered throughout, their contents long since scavenged or decayed. The air is heavy with the scent of stale cardboard and mold, and the sound of creaking metal echoes as the structure slowly deteriorates."
        )
        self.add_outside_observation(
            "The once bustling industrial complex now stands silent, with cargo crates stacked haphazardly outside. Many are open or crushed, with the remains of their contents spilling into the surrounding dirt."
        )
        self.update_observations()  # Populate the initial observations.


class Factory(BuildingBlock):
    def __init__(self, block_name="Empty Factory"):
        super().__init__(block_name, block_type="Factory", find_probabilities={"Tool": 0.3, "Medicine": 0.1, "Food": 0.15})
        self.block_desc = "factory"      
        
        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "The air is thick with the stench of rust and oil, and most of the machines have long since stopped working. Broken assembly lines lay dormant, while piles of discarded tools and broken machinery are scattered across the floor. The faint smell of chemicals still lingers in the stale air."
        )
        self.add_outside_observation(
            "The crumbling building is surrounded by rusted metal walls, broken windows, and piles of scrap. The smell of oil and decay fills the air."
        )
        self.update_observations()  # Populate the initial observations.


class School(BuildingBlock):
    def __init__(self, block_name="Empty School"):
        super().__init__(block_name, block_type="School", find_probabilities={"Tool": 0.3, "Medicine": 0.1, "Food": 0.15})
        self.block_desc = "school"
        
        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "The classrooms are dusty and neglected, with broken desks and chairs scattered about. Faded educational posters cling to the walls, peeling from years of neglect. The halls are eerily silent, and the remnants of a forgotten time seem to hang in the air."
        )
        self.add_outside_observation(
            "The exterior is cracked and weathered, with broken windows and overgrown weeds poking through the concrete. A playground, once filled with laughter, is now overtaken by rusted swings and vines."
        )
        self.update_observations()  # Populate the initial observations.


class Hospital(BuildingBlock):
    def __init__(self, block_name="Empty Hospital"):
        super().__init__(block_name, block_type="Hospital", find_probabilities={"Tool": 0.3, "Medicine": 0.1, "Food": 0.15})
        self.block_desc = "hospital"
        
        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "The sterile white walls are now yellowed with age, and the floor is cracked and littered with broken medical equipment. A few old, unused beds are scattered in the rooms, with sheets long since turned to dust. The smell of stale air and decay is overpowering."
        )
        self.add_outside_observation(
            "The once-pristine building is now a hollow shell, with a faded red cross on the crumbling facade. Shattered windows reveal the desolation within."
        )
        self.update_observations()  # Populate the initial observations.


class AutoRepair(BuildingBlock):
    def __init__(self, block_name="Empty Auto Repair"):
        super().__init__(block_name, block_type="AutoRepair", find_probabilities={"Tool": 0.3, "Medicine": 0.1, "Food": 0.15})
        self.block_desc = "auto repair shop"

        # Initialize default descriptions  
        self.add_inside_observation(f"You are inside an {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside an {self.block_desc}.")
        self.add_inside_observation(
            "The tools are rusted and covered in dust, and most of the car parts are either useless or beyond repair. Disassembled vehicles sit lifeless, their parts scavenged by previous survivors. The air smells of old gasoline and oil, but there’s a strange staleness to it now."
        )
        self.add_outside_observation(
            "The once-busy garage is now a graveyard for broken cars, with rusting bodies and scattered parts strewn across the ground."
        )
        self.update_observations()  # Populate the initial observations.


class Library(BuildingBlock):
    def __init__(self, block_name="Empty Library"):
        super().__init__(block_name, block_type="Library", find_probabilities={"Tool": 0.1, "Medicine": 0.05, "Food": 0.1})
        self.block_desc = "library"

        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "Shelves of books are covered in dust, with many of them either rotting or torn apart by scavengers. Broken windows allow sunlight to filter in, casting eerie shadows over the abandoned reading areas. The silence is oppressive, broken only by the sound of creaking wood."
        )
        self.add_outside_observation(
            "The building is rundown, with vines crawling over the cracked brick walls. The front doors hang loosely on their hinges, and you can barely make out the name on the weathered sign."
        )
        self.update_observations()  # Populate the initial observations.


class Museum(BuildingBlock):
    def __init__(self, block_name="Empty Museum"):
        super().__init__(block_name, block_type="Museum", find_probabilities={"Tool": 0.3, "Medicine": 0.1, "Food": 0.15})
        self.block_desc = "museum"
        
        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "The exhibits are long gone, with empty display cases and broken artifacts scattered across the floor. The walls are cracked, and the dim light from a broken skylight casts a haunting glow over the abandoned space. What was once a place of history is now a forgotten relic."
        )
        self.add_outside_observation(
            "The grand entrance is overrun with vines, and the massive doors hang ajar. Statues outside are weathered and broken, their faces now obscured by grime and decay."
        )
        self.update_observations()  # Populate the initial observations.


class Junkyard(BuildingBlock):
    def __init__(self, block_name="Empty Junkyard"):
        super().__init__(block_name, block_type="Junkyard", find_probabilities={"Tool": 0.3, "Medicine": 0.1, "Food": 0.15})
        self.block_desc = "junkyard"

        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "Piles of scrap metal, broken vehicles, and old machinery are everywhere. The remnants of old appliances and electrical equipment lie in heaps, long past their usefulness. The air is thick with rust and decay."
        )
        self.add_outside_observation(
            "A vast expanse of rusting metal and broken machinery stretches out in all directions. The ground is littered with scraps of metal, glass, and plastic."
        )
        self.update_observations()  # Populate the initial observations.


class Church(BuildingBlock):
    def __init__(self, block_name="Empty Church"):
        super().__init__(block_name, block_type="Church", find_probabilities={"Tool": 0.05, "Medicine": 0.15, "Food": 0.1})
        self.block_desc = "church"

        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "The once-beautiful stained glass windows are now shattered, and the pews are rotting away. Dust covers the altar, and cobwebs fill the corners of the room. A faint smell of mildew lingers in the air, making the place feel abandoned and forgotten."
        )
        self.add_outside_observation(
            "The steeple is cracked, and the doors hang off their hinges. The facade is chipped, and the once-pristine grounds are now overrun by weeds and moss."
        )
        self.update_observations()  # Populate the initial observations.


class Pub(BuildingBlock):
    def __init__(self, block_name="Empty Pub"):
        super().__init__(block_name, block_type="Pub", find_probabilities={"Tool": 0.3, "Medicine": 0.1, "Food": 0.15})
        self.block_desc = "pub"

        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "The bar is empty, and bottles of liquor are cracked and spilled on the counter. The tables are overturned, and old, rotting chairs are scattered across the floor. The air smells of stale beer and decay, with a sense of abandonment filling the space."
        )
        self.add_outside_observation(
            "The neon sign flickers faintly, almost out of power, and the building's exterior is worn and weathered. Broken windows and peeling paint reveal the building's abandonment."
        )
        self.update_observations()  # Populate the initial observations.


class Nightclub(BuildingBlock):
    def __init__(self, block_name="Empty Nightclub"):
        super().__init__(block_name, block_type="Nightclub", find_probabilities={"Tool": 0.3, "Medicine": 0.1, "Food": 0.15})
        self.block_desc = "nightclub"

        # Initialize default descriptions
        self.add_inside_observation(f"You are inside a {self.block_desc}.")
        self.add_outside_observation(f"You are standing outside a {self.block_desc}.")
        self.add_inside_observation(
            "The dance floor is empty, covered in dust, and the speakers have long since stopped working. The neon lights flicker weakly, casting an eerie glow across the abandoned space. Broken furniture and shattered glass litter the ground."
        )
        self.add_outside_observation(
            "The once-vibrant building is now dim and lifeless, with darkened windows and a door that creaks open only to reveal emptiness inside."
        )
        self.update_observations()  # Populate the initial observations.
    

# Outdoor Spaces
class Street(CityBlock):
    def __init__(self, block_name="Empty Str"):
        super().__init__(block_name, block_type="Street")
        self.block_desc = "street"

        # Initialize default descriptions
        self.add_outside_observation(f"You are standing in a {self.block_desc}.")
        self.add_outside_observation("The asphalt stretches ahead, lined with buildings.")
        self.update_observations()  # Populate the initial observations.


class Park(CityBlock):
    def __init__(self, block_name="Empty Par"):
        super().__init__(block_name, block_type="Park")
        self.block_desc = "park"

        # Initialize default descriptions
        self.add_outside_observation(f"You are standing in a {self.block_desc}.")
        self.add_outside_observation("Open space with benches and fountains.")
        self.update_observations()  # Populate the initial observations.


class Carpark(CityBlock):
    def __init__(self, block_name="Empty Car"):
        super().__init__(block_name, block_type="Carpark")
        self.block_desc = "carpark"

        # Initialize default descriptions
        self.add_outside_observation(f"You are standing in a {self.block_desc}.")
        self.add_outside_observation("Lines of empty parking spaces spread around you.")
        self.update_observations()  # Populate the initial observations.


class Cemetery(CityBlock):
    def __init__(self, block_name="Empty Cem"):
        super().__init__(block_name, block_type="Cemetery")
        self.block_desc = "cemetery"

        # Initialize default descriptions
        self.add_outside_observation(f"You are standing in a {self.block_desc}.")
        self.add_outside_observation("Rows of gravestones mark this solemn place.")
        self.update_observations()  # Populate the initial observations.


class Monument(CityBlock):
    def __init__(self, block_name="Empty Mon"):
        super().__init__(block_name, block_type="Monument")
        self.block_desc = "monument"

        # Initialize default descriptions
        self.add_outside_observation(f"You are standing at a {self.block_desc}.")
        self.add_outside_observation("The towering structure is made of stone, its "
                                     "surface chipped and cracked, with deep scars left "
                                     "by years of neglect. Faded engravings and worn "
                                     "inscriptions are barely legible, telling the stories "
                                     "of a long-forgotten past.")
        self.update_observations()  # Populate the initial observations.
