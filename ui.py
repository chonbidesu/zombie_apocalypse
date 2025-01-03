# ui.py

import pygame
from pygame import Color, Rect, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, USEREVENT

from settings import *

# pygame must be initialized before we can create a Font.
pygame.init()
try:
    # "data.py" is a skellington-ism. The included custom version supports
    # subdirectories by type.
    import data
except:
    print('warning: no data.py in module path: proceeding without it')
finally:
    try:
        font = pygame.font.Font('data/Vera.ttf', 14)
    except:
        print('warning: cannot load font Vera.ttf: using system default')
        font = pygame.font.SysFont(None, 20)

bg_color = Color('grey')
hi_color = Color(155,155,155)
text_color = Color('black')
glint_color = Color(220,220,220)
shadow_color = Color(105,105,105)

margin = 2

class Button(pygame.sprite.Sprite):
    """A button that changes images on mouse events."""
    def __init__(self, name, x, y):
        super().__init__()
        self.name = name
        self.image_up = pygame.image.load(f"assets/{name}_up.bmp")
        self.image_up = pygame.transform.scale(self.image_up, (100, 49))
        self.image_down = pygame.image.load(f"assets/{name}_down.bmp")
        self.image_down = pygame.transform.scale(self.image_down, (100, 49))
        self.image = self.image_up
        self.rect = self.image.get_rect(topleft = (x, y))
        self.is_pressed = False

    def handle_event(self, event):
        """Handle mouse events to change button state."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.image = self.image_down
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed:
                self.image = self.image_up
                self.is_pressed = False
                if self.rect.collidepoint(event.pos):
                    return self.name # Return the button name when clicked
                
        return None
    
    def update(self):
        """Update the button's visual state."""
        # The image has already been changed in handle_event; nothing extra needed here
        pass

# Handle text wrapping
def wrap_text(text, font, max_width):
    """Wrap the text to fit inside a given width."""
    lines = []
    words = text.split(" ")
    current_line = ""

    for word in words:
        # Check if adding the word exceeds the width
        test_line = current_line + (word if current_line == "" else " " + word)
        test_width, _ = font.size(test_line)

        if test_width <= max_width:
            current_line = test_line  # Add the word to the current line
        else:
            if current_line != "":
                lines.append(current_line)  # Append the current line if it's not empty
            current_line = word  # Start a new line with the current word

    if current_line != "":  # Append the last line if it has any content
        lines.append(current_line)

    return lines

# Get the neighbourhood of a city block
def get_neighbourhood(block, neighbourhood_groups):
    for group_name, group in neighbourhood_groups.items():
        if block in group:
            return group_name
    return None

# Draw viewport
viewport_frame = pygame.image.load('assets/viewport_frame.png')

def draw_viewport(screen, player, viewport_group, font_small):
    """Draw the 3x3 viewport representing the player's surroundings."""
    
    viewport_frame_width, viewport_frame_height = SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2
    # grid_start_x, grid_start_y = (viewport_frame_width // 9) + 12, (viewport_frame_height // 9) + 12
    current_block = player.get_block_at_player()
    neighbourhood_groups = player.neighbourhood_groups

    scaled_viewport_frame = pygame.transform.scale(viewport_frame, (viewport_frame_width, viewport_frame_height))
    screen.blit(scaled_viewport_frame, (10, 10))

    viewport_group.draw(screen)

    for block in viewport_group:

    # for row_index, row in enumerate(viewport_rows):
        # for col_index, block in enumerate(row):
            # if block is None:
            #    continue

            # Calculate the block's position relative to the viewport
            #block_rect_x = grid_start_x + col_index * BLOCK_SIZE
            #block_rect_y = grid_start_y + row_index * BLOCK_SIZE

            #screen.blit(block.image, (block_rect_x, block_rect_y))

        block_text = wrap_text(block.block_name, font_small, BLOCK_SIZE - 10)
        text_height = sum(font_small.size(line)[1] for line in block_text)
        # Adjust button_rect to align with bottom of block_rect
        button_rect = pygame.Rect(
            block.rect.x, block.rect.y + BLOCK_SIZE - text_height - 10,
            BLOCK_SIZE, text_height + 10)
        pygame.draw.rect(screen, WHITE, button_rect)

        y_offset = button_rect.top + (button_rect.height - text_height)  # Center text vertically
        for line in block_text:
            text = font_small.render(line, True, BLACK)
            text_rect = text.get_rect(center=(button_rect.centerx, y_offset))
            screen.blit(text, text_rect)
            y_offset += font_small.size(line)[1]  # Move down for the next line

    # Draw neighbourhood name
    pygame.draw.rect(screen, ORANGE, (10, viewport_frame_height + 10, viewport_frame_width, 20))
    neighbourhood_name = get_neighbourhood(current_block, neighbourhood_groups)
    text = font_small.render(neighbourhood_name, True, WHITE)
    screen.blit(text, ((viewport_frame_width // 2) - (text.get_width() // 2), viewport_frame_height + 15))

# Draw actions panel
def draw_actions_panel(screen, font_large):
    """Draw the Available Actions panel with button sprites."""

    # Panel dimensions
    panel_x = 10
    panel_y = (SCREEN_HEIGHT // 2) + 30
    panel_width = SCREEN_HEIGHT // 2
    panel_height = (SCREEN_HEIGHT // 4) - 80

    # Draw the panel background and border
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    # Render the title
    title_text = font_large.render("Available Actions", True, BLACK)
    title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 20))
    screen.blit(title_text, title_rect)

# Draw description panel
description_panel_image = pygame.image.load("assets/description_panel.png")

def draw_description_panel(screen, player, font_large):
    """Draw the description panel on the right side of the screen."""

    description_start_x = SCREEN_WIDTH // 3 + 10
    description_width = SCREEN_WIDTH * 2 // 3 - 10
    description_height = SCREEN_HEIGHT * 25 // 32

    scaled_panel_image = pygame.transform.scale(description_panel_image, (description_width, description_height))
    screen.blit(scaled_panel_image, (description_start_x, 10))

    # Determine the setting image
    current_block = player.get_block_at_player()
    for group, blocks in player.outdoor_type_groups.items():
        if current_block in blocks:
            block_type = group.lower()
    for group, blocks in player.building_type_groups.items():
        if current_block in blocks:
            block_type = group.lower()
    image_suffix = "inside" if player.inside else "outside"
    image_path = f"assets/{block_type}_{image_suffix}.png"

    try:
        setting_image = pygame.image.load(image_path)
    except FileNotFoundError:
        setting_image = pygame.Surface((1, 1))  # Fallback if image not found
        setting_image.fill((0, 0, 0))

    # Scale the setting image
    setting_image_width = description_width * 5 // 6
    setting_image_height = setting_image_width * 4 // 9  # 9:4 aspect ratio
    scaled_setting_image = pygame.transform.scale(setting_image, (setting_image_width, setting_image_height))

    # Blit the setting image at the top of the panel
    setting_image_x = description_start_x + (description_width - setting_image_width) // 2
    setting_image_y = 50
    screen.blit(scaled_setting_image, (setting_image_x, setting_image_y))

    # Get the description text and wrap it to fit within the panel
    text_start_y = setting_image_y + setting_image_height + 20
    paragraphs = []
    current_observations = player.description()
    for observation in current_observations:
        wrapped_text = wrap_text(observation, font_large, description_width - 100)  # 50px padding on each side
        for line in wrapped_text:
            paragraphs.append(line)
        paragraphs.append(" ")

    # Render each paragraph inside the description panel
    for line in paragraphs:
        text = font_large.render(line, True, BLACK)
        text_rect = text.get_rect(x=description_start_x + 50, y=text_start_y)  # Padding of 50px on the left
        screen.blit(text, text_rect)
        text_start_y += font_large.size(line)[1]  # Move down for the next line

# Draw the chat panel
def draw_chat(screen, chat_history, input_text, scroll_offset, font_chat):
    """Draw the chat window with scrolling support and text wrapping."""
    chat_width, chat_height = SCREEN_WIDTH // 3 - 10, CHAT_HEIGHT
    chat_start_x, chat_start_y = 10, SCREEN_HEIGHT - chat_height - 10


    # Draw the chat window.
    pygame.draw.rect(screen, BLACK, (chat_start_x, chat_start_y, chat_width, chat_height))
    pygame.draw.rect(screen, WHITE, (chat_start_x, chat_start_y, chat_width, chat_height), 2)

    # Draw messages starting from the bottom of the chat area
    # Calculate the max number of visible lines.
    max_visible_lines = (chat_height - 20) // 20
    wrapped_history = []
    for message in chat_history:
        wrapped_history.extend(wrap_text(f">> {message}", font_chat, chat_width - 20))

    total_lines = len(wrapped_history)

    # Limit scroll_offset to valid bounds.
    scroll_offset = max(0, min(scroll_offset, max(0, total_lines - max_visible_lines)))

    # Determine which messages to display based on scroll_offset
    visible_history = wrapped_history[scroll_offset:scroll_offset + max_visible_lines]
    y_offset = chat_start_y + chat_height - 30

    line_height = font_chat.get_linesize()

    for message in reversed(visible_history):
            text = font_chat.render(message, True, WHITE)
            screen.blit(text, (chat_start_x + 10, y_offset))
            y_offset -= line_height

# Draw the player status panel
def draw_status(screen, player, font_large):
    """Draw the player status panel."""
    status_start_x, status_start_y = SCREEN_WIDTH // 3 + 10, SCREEN_HEIGHT - 150
    status_width, status_height = SCREEN_WIDTH // 4 - 20, 140

    pygame.draw.rect(screen, BLACK, (status_start_x, status_start_y, status_width, status_height))
    pygame.draw.rect(screen, WHITE, (status_start_x, status_start_y, status_width, status_height), 2)

    y_offset = status_start_y + 10
    status_text = []
    for status_type, status in player.status().items():
        line = f"{status_type}: {status}"
        status_text.append(line)

    for line in status_text:
        text = font_large.render(line, True, WHITE)
        screen.blit(text, (status_start_x + 10, y_offset))
        y_offset += 20

# Draw the inventory panel
def draw_inventory_panel(screen, player, font_large):
    """Render the inventory panel in the bottom-right corner of the screen."""
    # Panel dimensionss
    panel_width = SCREEN_WIDTH * 5 // 12 - 20
    panel_height = 140
    panel_x = SCREEN_WIDTH - panel_width - 10
    panel_y = SCREEN_HEIGHT - panel_height - 10

    # Sub-panel dimensions
    equipped_panel_width = panel_width // 4
    equipped_panel_height = panel_height
    equipped_panel_x = panel_x
    equipped_panel_y = panel_y

    inventory_panel_width = panel_width - equipped_panel_width
    inventory_panel_height = panel_height
    inventory_panel_x = panel_x + equipped_panel_width
    inventory_panel_y = panel_y

    # Draw main panel
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2)

    # Draw equipped sub-panel
    pygame.draw.rect(screen, WHITE, (equipped_panel_x, equipped_panel_y, equipped_panel_width, equipped_panel_height))
    pygame.draw.rect(screen, BLACK, (equipped_panel_x, equipped_panel_y, equipped_panel_width, equipped_panel_height), 2)

    # Draw "Equipped" label
    equipped_label = font_large.render("Equipped", True, BLACK)
    label_rect = equipped_label.get_rect(center=(equipped_panel_x + equipped_panel_width // 2, equipped_panel_y + 20))
    screen.blit(equipped_label, label_rect)

    # Render equipped item (if any)
    if player.weapon:
        # Draw enlarged equipped item
        enlarged_image = pygame.transform.scale(player.weapon.sprite.image, (64, 64))
        equipped_item_x = equipped_panel_x + (equipped_panel_width - 64) // 2
        equipped_item_y = equipped_panel_y + 40
        screen.blit(enlarged_image, (equipped_item_x, equipped_item_y))

    # Draw inventory sub-panel
    pygame.draw.rect(screen, WHITE, (inventory_panel_x, inventory_panel_y, inventory_panel_width, inventory_panel_height))
    pygame.draw.rect(screen, BLACK, (inventory_panel_x, inventory_panel_y, inventory_panel_width, inventory_panel_height), 2)

    # Position inventory items
    item_x = inventory_panel_x + 10  # Start with padding
    item_y = inventory_panel_y + (inventory_panel_height // 2 - 16)  # Center items vertically
    for item in player.inventory:
        
        # Update item rect with its position
        item.rect.x = item_x
        item.rect.y = item_y

        # Highlight the equipped item
        if item == player.weapon:
            pygame.draw.rect(screen, WHITE, (item_x - 2, item_y - 2, 36, 36), 2)

        # Move to the next position
        item_x += 36  # Item width + spacing
        if item_x + 36 > inventory_panel_x + inventory_panel_width:  # Wrap to next line if out of space
            item_x = inventory_panel_x + 10
            item_y += 36

# Attempt to create a right-click menu
class PopupMenu(object):
    """popup_menu.PopupMenu
    PopupMenu(data, block=True) : return menu
    
    data -> list; the list of strings and nested lists.
    pos -> tuple; the xy screen coordinate for the topleft of the main menu; if
        None, the mouse position is used.
    block -> boolean; when True popup_menu will run its own event loop, blocking
        your main loop until it exits; when False popup_menu.get_events() will
        intercept events it cares about and return unhandled events to the
        caller.
    
    Note: For a non-blocking menu, use the NonBlockingPopupMenu instead. This
    class supports non-blocking, but it is more cumbersome to use than the
    NonBlockingPopupMenu class.
    
    The first string in the data list is taken as the menu title. The remaining
    strings are menu items. A nested list becomes a submenu. Submenu lists must
    also contain strings for menu title and menu items. Submenus can be
    theoretically infinitely nested.
    
    The menu runs a mini event loop. This will block the caller until it exits.
    Upon exiting, the screen is restored to its prior state.
    
    Left-clicking outside the topmost menu will quit the entire menu. Right-
    clicking anywhere will close the topmost submenu; if only the main menu
    remains the menu will exit. Left-clicking a menu item in the topmost menu
    will post a USEREVENT for the caller to process.
    
    The USEREVENT will have attributes: code='MENU', name=popup_menu.name,
    item_id=menu_item.item_id, text=menu_item.text. name is first element in a
    menu data list. item_id corresponds to the Nth element in a menu data list,
    incremented from 0; submenu items count as one menu_id even though they are
    never posted in an event. text is the string value of the Nth element in the
    menu data list. Thus, combinations of name and menu_id or name and text can
    be used to uniquely identify menu selections.
    
    Example menu data and resulting event data:
        
        ['Main',            # main menu title
         'Item 0',          # name='Main', menu_id=0, text='Item 0'
            ['Submenu',     # submenu title
             'Item 0',      # name='Submenu', menu_id=0, text='Item 0'
             'Item 1',      # name='Submenu', menu_id=0, text='Item 1'
            ],
         'Item 2',          # name='Main', menu_id=2, text='Item 2'
        ]
    
    High-level steps for a blocking menu:

    1.  Fashion a nested list of strings for the PopupMenu constructor.
    2.  Upon creation, the menu runs its own loop.
    3.  Upon exit, control is returned to the caller.
    4.  Handle the resulting USEREVENT event in the caller where
        event.name=='your menu title', event.item_id holds the selected item
        number, and event.text holds the item label.
    
    High-level steps for a non-blocking menu:
    
    Note: This usage exists to support the NonBlockingPopupMenu class and
    custom non-blocking implementations; for typical use NonBlockingPopupMenu
    is recommended.

    1.  Fashion a nested list of strings for the PopupMenu constructor.
    2.  Store the menu object in a variable.
    3.  Devise a means for the main loop to choose whether to draw the menu and pass
        it events.
    4.  Call menu.draw() to draw the menu.
    5.  Pass pygame events to menu.handle_events() and process the unhandled events
        that are returned as you would pygame's events.
    6.  Upon menu exit, one or two USEREVENTs are posted via pygame. Retrieve
        them and recognize they are menu events (event.code=='MENU').
        a.  The menu-exit event signals the main loop it has exited, with or
            without a menu selection. Recognize this by event.name==None. Upon
            receiving this event the main loop should stop using the menu's
            draw() and get_events() (until the next time it wants to post the
            menu to the user).
        b.  The menu-selection event signals the main loop that a menu item was
            selected. Recognize this by event.name=='your menu title'.
            event.menu_id holds the selected item number, and event.text holds
            the item label.
    7.  Destroying the menu is not necessary. But creating and destroying it may
        be a convenient means to manage the menu state (i.e. to post it or not).
    """
    
    def __init__(self, data, pos=None, block=True):
        # list of open Menu() objects
        self.menus = []
        # key to main menu data
        self.top = data[0]
        # dict of menus, keyed by menu title
        self.data = {self.top:[]}
        # walk the nested list, creating the data dict for easy lookup
        self._walk(self.top, list(data))
        
        # make the main menu
        self._make_menu(self.data[self.top], pos)
        
        # Save the display surface; use to clear screen
        self.screen = pygame.display.get_surface()
        self.clear_screen = self.screen.copy()
        
        if block:
            self._run(block)

    def handle_events(self, events, block=False):
        unhandled = []
        for e in events:
            if e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    menu = self.menus[-1]
                    item = menu.menu_item
                    if item:
                        if isinstance(item.text, SubmenuLabel):
                            # open submenu
                            key = item.text[:-3]
                            self._make_menu(self.data[key])
                        else:
                            # pick item (post event)
                            pygame.event.post(self._pick_event(menu, item))
                            self._quit(block)
                            return [self._quit_event()]
                    else:
                        # close menu
                        self._quit(block)
                        return [self._quit_event()]
                elif e.button == 3:
                    # close menu
                    if len(self.menus) == 1:
                        self._quit(block)
                        return [self._quit_event()]
                    else:
                        self._del_menu()
            elif e.type == MOUSEMOTION:
                self.mouse_pos = e.pos
                self.menus[-1].check_collision(self.mouse_pos)
                unhandled.append(e)
            elif e.type == MOUSEBUTTONDOWN:
                pass
            else:
                unhandled.append(e)
        return unhandled
    
    def draw(self):
        for menu in self.menus:
            menu.draw()
    
    def _pick_event(self, menu, item):
        event = pygame.event.Event(USEREVENT, code='MENU',
            name=menu.name, item_id=item.item_id, text=item.text)
        return event
    
    def _quit_event(self):
        event = pygame.event.Event(USEREVENT, code='MENU',
            name=None, item_id=-1, text='_MENU_EXIT_')
        return event
    
    def _run(self, block=True):
        screen = self.screen
        clock = pygame.time.Clock()
        self.mouse_pos = pygame.mouse.get_pos()
        self.running = True
        while self.running:
            self.screen.blit(self.clear_screen, (0,0))
            self.draw()
            pygame.display.flip()
            self.handle_events(pygame.event.get())
            clock.tick(60)

    def _walk(self, key, data):
        # Recursively walk the nested data lists, building the data dict for
        # easy lookup.
        for i,ent in enumerate(data):
            if isinstance(ent, str):
                self.data[key].append(ent)
            else:
                ent = list(ent)
                new_key = ent[0]
                ent[0] = SubmenuLabel(new_key)
                self.data[key].append(ent[0])
                self.data[new_key] = []
                self._walk(new_key, list(ent))
    
    def _make_menu(self, data, pos=None):
        # Make a menu from data list and add it to the menu stack.
        if self.menus:
            # position submenu relative to parent
            parent = self.menus[-1]
            rect = parent.menu_item.rect
            pos = rect.right,rect.top
            # unset the parent's menu_item (for appearance)
            parent.menu_item = None
        else:
            # position main menu at mouse
            if pos is None:
                pos = pygame.mouse.get_pos()
        name = data[0]
        items = data[1:]
        self.menus.append(Menu(pos, name, items))

    def _del_menu(self):
        # Remove the topmost menu from the menu stack.
        self.menus.pop()

    def _quit(self, block):
        # Put the original screen contents back.
        if block:
            self.screen.blit(self.clear_screen, (0,0))
            pygame.display.flip()
        self.running = False


class NonBlockingPopupMenu(PopupMenu):
    """popup_menu.NonBlockingPopupMenu
    NonBlockingPopupMenu(data, pos=None, show=False) : return menu
    
    data -> list; the list of strings and nested lists.
    pos -> tuple; the xy screen coordinate for the topleft of the main menu; if
        None, the mouse position is used.
    show -> boolean; make the menu visible in the constructor.

    visible is a read-write property that sets and gets the boolean value
    representing the state. The show() and hide() methods are equivalent
    alternatives to using the property.

    Note that the constructor does not copy the data argument. Changes to the
    contents will result in changes to the menus once show() is called or
    visible is set to True. In addition, data can be entirely replaced by
    setting menu.init_data.

    High-level steps for a non-blocking menu:

    1.  Fashion a nested list of strings for the NonBlockingPopupMenu constructor.
    2.  Store the menu object in a variable.
    3.  Construct the NonBlockingPopupMenu object.
    4.  Detect the condition that triggers the menu to post, and call menu.show()
        (or set menu.visible=True).
    5.  Call menu.draw() to draw the menu. If it is visible, it will be drawn.
    6.  Pass pygame events to menu.handle_events() and process the unhandled events
        that are returned as you would pygame's events. If the menu is not visible
        the method will immediately return the list passed in, unchanged.
    7.  Upon menu exit, one or two USEREVENTs are posted via pygame. Retrieve them
        and recognize they are menu events (i.e., event.code=='MENU').
        a.  A menu-exit event signals the menu has detected an exit condition, which
            may or many not be accompanied by a menu selection. Recognize this by
            event.name==None or event.menu_id==-1. Upon receiving this event the
            main loop should call menu.hide() (or set menu.visible=False).
        b.  A menu-selection event signals the main loop that a menu item was
            selected. Recognize this by event.name=='your menu title'. event.menu_id
            holds the selected item number, and event.text holds the item label.
    8.  Destroying the menu is optional.
    9.  Assigning to menu.init_data, or changing its contents or that of the
        original list variable, will result in a modified menu the next time
        menu.show() is called (or menu.visible is set to True).
"""
    
    def __init__(self, data, pos=None, show=False):
        self.init_data = data
        self._init_pos = pos
        if show:
            self.show()
        else:
            self.hide()
    
    def show(self):
        """generate the menu geometry and graphics, and makes the menu visible"""
        super(NonBlockingPopupMenu, self).__init__(
            self.init_data, pos=self._init_pos, block=False)
        self._show = True
    
    def hide(self):
        """destroy the menu geometry and grpahics, and hides the menu"""
        if hasattr(self, 'menus'):
            del self.menus[:]
        self._show = False

    @property
    def visible(self):
        return self._show
    @visible.setter
    def visible(self, val):
        if val:
            self.show()
        else:
            self.hide()

    def handle_events(self, events):
        """preemptively return if the menu is not visible; else, call the
        superclass's method.
        """
        if self._show:
            return super(NonBlockingPopupMenu, self).handle_events(events)
        else:
            return events

    def draw(self):
        """preemptively return if the menu is not visible; else, call the
        superclass's method.
        """
        if self._show:
            super(NonBlockingPopupMenu, self).draw()

class SubmenuLabel(str):
    """popup_menu.SubmenuLabel
    SubmenuLabel(s) : return label
    
    s -> str; the label text
    
    This is a helper class for strong-typing of submenu labels.
    
    This class is not intended to be used directly. See PopupMenu or
    NonBlockingPopupMenu.
    """
    
    def __new__(cls, s):
        return str.__new__(cls, s+'...')


class MenuItem(object):
    """popup_menu.MenuItem
    MenuItem(text, item_id) : return menu_item

    text -> str; the display text.
    item_id -> int; the numeric ID; also the item_id attribute returned in the
        pygame event.
    
    This class is not intended to be used directly. Use PopupMenu or
    NonBlockingPopupMenu instead, unless designing your own subclass.
    """
    
    def __init__(self, text, item_id):
        self.text = text
        self.item_id = item_id
        self.image = font.render(text, True, text_color)
        self.rect = self.image.get_rect()


class Menu(object):
    """popup_menu.Menu
    Menu(pos, name, items) : return menu

    pos -> (x,y); topleft coordinates of the menu.
    name -> str; the name of the menu.
    items -> list; a list containing strings for menu items labels.

    This class is not intended to be used directly. Use PopupMenu or
    NonBlockingPopupMenu instead, unless designing your own subclass.
    """
    
    def __init__(self, pos, name, items):
        screen = pygame.display.get_surface()
        screen_rect = screen.get_rect()
        self.name = name
        self.items = []
        self.menu_item = None
        # Make the frame rect
        x,y = pos
        self.rect = Rect(x,y,0,0)
        self.rect.width += margin * 2
        self.rect.height += margin * 2
        # Make the title image and rect, and grow the frame rect
        self.title_image = font.render(name, True, text_color)
        self.title_rect = self.title_image.get_rect(topleft=(x+margin,y+margin))
        self.rect.width = margin*2 + self.title_rect.width
        self.rect.height = margin + self.title_rect.height
        # Make the item highlight rect
        self.hi_rect = Rect(0,0,0,0)

        # Make menu items
        n = 0
        for item in items:
            menu_item = MenuItem(item, n)
            self.items.append(menu_item)
            self.rect.width = max(self.rect.width, menu_item.rect.width+margin*2)
            self.rect.height += menu_item.rect.height + margin
            n += 1
        self.rect.height += margin
        
        # Position menu fully within view
        if not screen_rect.contains(self.rect):
            savex,savey = self.rect.topleft
            self.rect.clamp_ip(screen_rect)
            self.title_rect.top = self.rect.top + margin
            self.title_rect.left = self.rect.left + margin
        
        # Position menu items within menu frame
        y = self.title_rect.bottom + margin
        for item in self.items:
            item.rect.x = self.rect.x + margin
            item.rect.y = y
            y = item.rect.bottom + margin
            item.rect.width = self.rect.width - margin*2
        
        # Calculate highlight rect's left-alignment and size
        self.hi_rect.left = menu_item.rect.left
        self.hi_rect.width = self.rect.width - margin*2
        self.hi_rect.height = menu_item.rect.height

        # Create the menu frame and highlight frame images
        self.bg_image = pygame.surface.Surface(self.rect.size)
        self.hi_image = pygame.surface.Surface(self.hi_rect.size)
        self.bg_image.fill(bg_color)
        self.hi_image.fill(hi_color)
        # Draw menu border
        rect = self.bg_image.get_rect()
        pygame.draw.rect(self.bg_image, glint_color, rect, 1)
        t,l,b,r = rect.top,rect.left,rect.bottom,rect.right
        pygame.draw.line(self.bg_image, shadow_color, (l,b-1), (r,b-1), 1)
        pygame.draw.line(self.bg_image, shadow_color, (r-1,t), (r-1,b), 1)
        # Draw title divider in menu frame
        left = margin
        right = self.rect.width - margin*2
        y = self.title_rect.height + 1
        pygame.draw.line(self.bg_image, shadow_color, (left,y), (right,y))

    def draw(self):
        # Draw the menu on the main display.
        screen = pygame.display.get_surface()
        screen.blit(self.bg_image, self.rect)
        screen.blit(self.title_image, self.title_rect)
        for item in self.items:
            if item is self.menu_item:
                self.hi_rect.top = item.rect.top
                screen.blit(self.hi_image, self.hi_rect)
            screen.blit(item.image, item.rect)

    def check_collision(self, mouse_pos):
        # Set self.menu_item if the mouse is hovering over one.
        self.menu_item = None
        if self.rect.collidepoint(mouse_pos):
            for item in self.items:
                if item.rect.collidepoint(mouse_pos):
                    self.menu_item = item
                    break