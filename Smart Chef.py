import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.app import runTouchApp
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ToggleButtonBehavior
from functools import partial
from kivy.uix.screenmanager import ScreenManager, Screen
import requests
from bs4 import BeautifulSoup
import urllib.request
import time
import re
from kivy.clock import Clock
import threading

#The builder load string is essentailly a window where I can customise each screen of my app. Each screen being a different class
Builder.load_string("""
<MainWindow>:
# For example, Here I am customising the MainWindow Screen, which is also the first screen the user uses
#This screen will have a grid layout with three rows
    GridLayout:
        rows: 3

 # I will have a label as the first row, with the text and customisations described below 
        Label:
            text_size: self.size
            font_size: 25 
            text: "Please Input a Dish:\\nThen select a source for the recipies\\n(If none are selected it will automatically select BakingMad)\\nIf you are looking for ideas select BakingMad and search"
            color: 0.32,1,1,1
            halign: 'center'
            # This is the horizontal allignment of the text, and i want it to be in the centre (kivy uses American english)
            valign: 'middle'
            # This is the verticle allignment of the text, and I want it to also be in the middle of the label

# The second row will have a textinput for the user, where the user descided which dish they want to make
# I have give the text input and id so i can refer back to the specific text input later on
        TextInput:
            id: dish
            multiline: False
            text_size: self.size
            font_size: 30 
            halign: 'center'
            valign: 'middle'

#The final row will infact be another grdi layout with 5 columns
        GridLayout:
            cols:5

# This is the quit button for when the user wants to quit the applicaiton
            Button:
                text: "Quit"
                text_size: self.size
                font_size: 20
                color: 0.32,1,1,1
                halign: 'center'
                valign: 'middle'
                on_release:
                #on_release is what the button does as soon as the button is released
                    app.stop() # This calls main app and closes it

            Button:
                text: "View Recently Completed Dishes"
                text_size: self.size
                font_size: 20
                color: 0.32,1,1,1
                halign: 'center'
                valign: 'middle'
                on_release:
                # This on_release function calles a function I ahve defined below, called old_dishes() which is in the root of the MainWindow class
                    root.old_dishes() 
            
             #I have used toggle buttons here as the user is not allowed to choose both sources (That being BBC and BakingMad Food)
            ToggleButton:
                id: BBC 
                # Therefore once one toggle is selected the other turns off
                text: "BBC Dishes"
                text_size: self.size
                font_size: 20
                color: 0.32,1,1,1
                halign: 'center'
                valign: 'middle'
                group: 'dish' 
                # I use the group statement to link the two toggle buttons, as if they both have the same group, then one will turn off if i press another
                state: 'down'
                #The state is what i have defined as the initial state of the button, so initially BBC will be selected

            ToggleButton:
                id: Bak
                text: "BakingMad Dishes"
                text_size: self.size
                font_size: 20
                color: 0.32,1,1,1
                halign: 'center'
                valign: 'middle'
                group: 'dish'
                #Once again this toggle button is in the same group as the BBC button above, so they are linked as toggle buttons
            

            Button:
                text: "Search"
                text_size: self.size
                font_size: 20
                color: 0.32,1,1,1
                halign: 'center'
                valign: 'middle'
                on_release:
                    root.pressed() 
                    #This calls the pressed() function below
                    app.root.current = "second"
                     # This transitions the current root to the root defined as "second". If you look below you will see I have defined the
                    root.manager.transition.direction = "left"
                    #Options window class under the "second" screen name
                    #^^This chooses the direction of the transition that occurs when the screens are being changed


#Here I have defined all the other classes that are used below, however I have used an alternative method to laying the classes out,
#This is because the Builder_load_screen mothod is inefficient and restricts the amount of customisation that I needed for the next couple screens
<OptionsWindow>:
        
<DishInformation>:

<Ingredients>:

<Instructions>:


""")

#This closes the Builder string, which is an alternative to using a seperate .kv file


class MyDishes(): 
    pass 

class MainWindow(Screen): #This is the class for the main Window, Screen is a class being passes that allows for transitions between screens

    def clean(self, raw_line):   #This subroutine checks for a > in the string applied as the > is classified as a URL text and it then returns true if
        if '>' in raw_line:      # > characters are in the string
            raw_line.find('>')
            return True

    def old_dishes(self): #This is a subroutine called if the user presses the Previously searched dishes button
        popup = Popup(title = "Previously Searched Dishes") #This opens a popup that has the title of Previosly seacrhed dishes
        layout = GridLayout(rows = 2)                       #The popup is useful as it allows me to uses the popup as a layout interface with GridLayout
        old_dishes = ''
        dish_list = open('dishes.txt','r') #Opens up a textfile so the user can store their completed dishes
        dishes = dish_list.readlines() 
        for line in dishes:
            line = line.rstrip()
            old_dishes += line + '\n'
        dish_list.close()
        old_dish_label = Label(text=old_dishes) # This creates a label of the old dishes 
        cnt_btn = Button(text="Continue") # Adds a button that the user can click to close the popup
        cnt_btn.bind(on_release = popup.dismiss)
        layout.add_widget(old_dish_label) # Binds the layout and button onto the Gridlayout
        layout.add_widget(cnt_btn)
        popup.content = layout # Sets the content of the popup to the grid layout previously defined
        popup.open() # Opens the poopup

    def list_of_dishes(self, query, url): #Returns a lost of the dishes the user needs depending on what query and url is (the query being the user input)
        page = urllib.request.urlopen(url) #Connects to the website
        soup = BeautifulSoup(page, 'html.parser')
        content_list = soup.get_text()
        content_list = soup.find_all('h3') # Screen scrapes from the URL nad gets a list of all the didhes (all the dishes are in the h3 category of the html)
        return content_list


    def list_of_websites(self, query, url): #This function is not used anywhere, but is used for future reference
        link = urllib.request.urlopen(url) #Connects to the website
        soup = BeautifulSoup(link, 'html.parser')
        website_list = soup.get_text()
        website_list = soup.find_all('a', href=True) #Searches for all the wesbites the the user is able to select on the specific page given the query
        return website_list
    

    def choices_list(self, content_lis):
        options = [] 
        for i in range(0, len(content_lis)):
            dish = content_lis[i].get_text() #Removes all the html that comes with the text and leaves just the text that the user input
            options.append(dish) 
            self.clean(str(content_lis)) #Clean is a previously defined function
        if toggle != "down":    #"down" is the toggle that the user uses when they select BBC dishes as their options
            if options[-3] == "Recipes":
                options = options[:-3] #Removes the final options from the list that are not dishes but are under the same tag as the dishes are
        return options


    def pressed(self):
        global query                    # I have had to use global variables as the kivy module does not allow classes to get parametres from one another, as that interferes with
        query = self.ids.dish.text      #the screens that are being used, as if i called one class in another, the classes layouts also get copied across which cannot be changed 
        query = "+".join(query.split())
        global toggle                   #As stated above regarding the use of global variables, toggle is the state of the BBC button (either down or normal)
        toggle = self.ids.BBC.state
        BBC = "https://www.bbc.co.uk/food/search?q=" + query #Gets the URL's of the specific query
        bakingMad = "https://www.bakingmad.com/search-results?searchtext=" + query
        if toggle == "down":
            content_list = self.list_of_dishes(query, BBC) #If the user clicks the BBC button, they get the list of BBC dishes
        else:
            content_list = self.list_of_dishes(query, bakingMad) #If the user clicks the BakingMad button, they get a list of BakingMad dishes
        #GoodFood = "https://www.bbcgoodfood.com/search/recipes?query=" + query
        global choices                              #Once again a global variable is used for the same reason as above
        choices = self.choices_list(content_list)
        
        if len(choices) == 0: #If there are no dishes for the user to choose from, it opens a popup that would tell the user there are no dishes available
            popup_alert = Popup(title = "No dishes")
            layout = GridLayout(rows = 2)
            label2 = Label(text="There are no dishes that match your criteria \n Please go back")
            btn2 = Button(text="Accept")
            btn2.bind(on_release = popup_alert.dismiss)
            layout.add_widget(label2)
            layout.add_widget(btn2)
            popup_alert.content = layout
            popup_alert.open()
        return choices
    
class OptionsWindow(Screen, App): #OptionsWindow is the second screen, which provides a list if all the options that the user has for as dishes

    def on_enter(self):
        popup = Popup(title='Dish Options', size_hint=(1,1))
        layout1 = StackLayout(orientation='lr-bt') #This time the options are layed out in a stack layout, so that I can have multiple options in a small space
        closebutton = Button(text='I want to make a different dish', size_hint=(0.9,0.05)) #This is a button that will make a different dish for the user
        closebutton.bind(on_press= popup.dismiss)                                           #The size_hint is the x and y co-ordinate score of how much percentage of the screen the button will have (with 1 being all the screen)
        closebutton.bind(on_release = self.change_page)
        scrlv = ScrollView(size_hint=(0.9,0.95)) #This adds a scrollable bar to the list of dishes, if there are lots of them
        slid = Slider(min=0, max=1, value=25, orientation='vertical', step=0.01, size_hint=(0.1, 0.95)) #The slid is the physical slider used, which calles the scrlv
        #step is the percentage of the screen it takes up, min and max are always 1 and 0 as they show the ful percentage of the screen covered by the bar
        scrlv.bind(scroll_y=partial(self.slider_change, slid))
        #what this does is, whenever the slider is dragged, it scrolls the previously added scrollview by the same amount the slider is dragged
        slid.bind(value=partial(self.scroll_change, scrlv))
        layout2 = GridLayout(cols=4, size_hint_y=None) #This is another grdi layout used within the popup
        layout2.bind(minimum_height=layout2.setter('height')) #Bind the height of the layout to the minimum height so that the scroll bar functions
        for txt in choices:
            btn = Button(text=txt, size_hint_y=None, height=80, valign='middle', font_size=12) # Add a button for each dish
            btn.text_size = (btn.size) #set the buttons so that their size changes depending on the screen size
            btn.bind(on_press = self.find_dish) #When the button is pressed, call the find_dish subroutine
            btn.bind(on_release = popup.dismiss) #Close the popup if they click the button
            layout2.add_widget(btn) # Add the buttons to the layout
        scrlv.add_widget(layout2)
        layout1.add_widget(closebutton) #Add the close button to the layout
        layout1.add_widget(scrlv) # Add the scroll bar to the layout
        layout1.add_widget(slid)  #Add the slider to the layout for the scroll bar
        popup.content = layout1
        popup.open()
        if len(choices) == 0:
            popup.dismiss()
            sm.current = "main" #This changes the screen back to the original "main" screen if there are no dishes, which allows the users to choose another dish


    def change_page(self, event):
        sm.current = "main" #This is a function that changes a page to the "main" page

    def scroll_change(self, scrlv, instance, value):
        scrlv.scroll_y = value # This updates the scroll value of the scroll_y 

    def slider_change(self, s, instance, value):
        if value >= 0:
        #this to avoid 'maximum recursion depth exceeded' error
            s.value=value

    def find_dish(self, btn):
        global dish_choice #Sets dish choice as global as it is used in another class and i cannot call one class in another due to kivy 
        dish_choice = "+".join(btn.text.split())    # not allowing class calling without also moving the layout, which causes interference
        sm.current = "third" #Changes the screen to the screen labeled as "third" below i.e DishInformation


class DishInformation(Screen, App):

    def on_enter(self): #on_enter is run as soon as the user enters this screen
        popup = Popup(title='Dish Information')
        if toggle == "down": #If the BBC toggle was selected earlier
            website_list = self.get_websites()
            matched_link = self.list_matcher(website_list)
            soup = self.initial_info(matched_link)
            try:
                cook_time = soup.find('p',attrs={"class":"recipe-metadata__cook-time"}).text #Finds all the p objects in the html code in the page with the class_name as the name as cook_time
            except AttributeError:
                cook_time = 'Not stated' #If there is no class, then state none is stated
            try:
                prep_time = soup.find('p',attrs={"class":"recipe-metadata__prep-time"}).text #Finds all the p objects in the html code in the page with the class_name as the prep time
            except AttributeError:
                prep_time = 'Not stated' #If there is no class, then state none is stated
            try:
                dietary = soup.find('p',attrs={"class":"recipe-metadata__dietary-vegetarian-text"}).text #Finds all the p objects in the html code in the page with the class_name as the vegetarien
            except AttributeError:
                dietary = 'Not Suitable for Vegetarians' #If there is no class, then state none is stated
            try:
                serves = soup.find('p',attrs={"class":"recipe-metadata__serving"}).text
            except AttributeError:
                serves = 'Not stated'
            cook_time = 'The time it will take to cook is: ' +'\n' + cook_time
            prep_time = 'The time it will take to prepare is: ' +'\n' + prep_time
            dietary = 'The dish is: '+'\n' + dietary
            if len(serves) > 25:
                serves = serves[:25] + ':\n'+ serves[25:] #If the line of people it serves goes over the page, then i cut it down into size
            serves = 'The dish:' +'\n' + serves

        if toggle == "normal": # As both the BBC and BakingMad have different classes, then i use have to have different class names as different 
            website_link = self.get_websites_mad()
            global full_link #Full link is made global as i cannot pass one class as a paremtre into another due to overlap of the screens
            full_link = 'https://www.bakingmad.com'+ str(website_link)
            soup = self.initial_info(full_link)
            try:
                cook_time = soup.find('div',attrs={"class":"recipe-info__prep-time"}).text
            except AttributeError:
                cook_time = 'Not stated'
            try:
                prep_time = soup.find('div',attrs={"class":"recipe-info__total-time"}).text
            except AttributeError:
                prep_time = 'Not stated'
            try:
                dietary = soup.find('li',attrs={"class":"recipe-info__diet has-child"}).text
            except AttributeError:
                dietary = 'Not Suitable for Vegetarians'
            try:
                serves = soup.find('li',attrs={"class":"recipe-info__yield"}).text
            except AttributeError:
                serves = 'Not stated'
            cook_time = 'The time it will take to cook is: ' +'\n' + cook_time
            prep_time = " ".join(prep_time.split())
            prep_time = prep_time[:11] + ':\n'+ prep_time[11:]
        first_layout = GridLayout(cols=2)
        prep_info = Label(text =prep_time,
                        font_size=20,
                        halign="center", #halign is the horizontal align
                        valign = "bottom") #valign is the horizontal align
        cook_info = Label(text =cook_time,
                        font_size=20,
                        halign="center",
                        valign = "bottom")
        dietary_info = Label(text = dietary,
                        font_size=20,
                        halign="center",
                        valign = "bottom")
        serve_info = Label(text= serves,
                        font_size=20,
                        halign="center",
                        valign = "bottom")
        back_btn = Button(text="Would you like to go back?", size_hint = (0.8,0.2))
        back_btn.bind(on_press = self.go_back)        
        back_btn.bind(on_release = popup.dismiss) #If the back button is clicked, then the popup is closed 

        next_btn = Button(text='Next page?',size_hint = (0.8,0.2))
        next_btn.bind(on_press = self.go_forward) #Call the go_forward function if the next button is pressed
        next_btn.bind(on_release = popup.dismiss)
        first_layout.add_widget(prep_info)  #Add all the labels and buttons i just made to the grid layout that was made
        first_layout.add_widget(cook_info)
        first_layout.add_widget(dietary_info)
        first_layout.add_widget(serve_info)
        first_layout.add_widget(back_btn)
        first_layout.add_widget(next_btn)

        popup.content = first_layout #Set the popup content as the layout defined at the start
        popup.open()


    def get_websites_mad(self): #This is a function solelly for the BakingMad, where it gets a list of websites on the pages so that i can get the links used
        url = "https://www.bakingmad.com/search-results?searchtext=" +query #Redefine the URL used for baking mad
        r = requests.get(url)
        data = r.text
        soup =BeautifulSoup(data, "html.parser") #Gets all the BeautifulSoup data from the page
        web_list = []
        for link in soup.find_all('a'):
            web_list.append(link.get('href'))
        new_web_list = []
        for val in web_list:
            if val not in new_web_list:
                new_web_list.append(val) #Get rid of all duplicates in the url list (as all the URL's were scraped twice)
        new_dish = dish_choice.replace('&', '') 
        newer_dish = new_dish.replace('+', '-')
        newest_dish = newer_dish.replace('--', '-')
        newest_dish = newest_dish[:46] #These 4 lines ^^ fix the link found and match the queries with the links that are used online, by removing all double dahes and pluess and shortening the lines
        other_new_dish = dish_choice.replace('&', 'and')
        other_newer_dish = other_new_dish.replace('+', '-')
        other_newest_dish = other_newer_dish.replace('--', '-')
        other_newest_dish = other_newest_dish[:49] #This fixes the other newest dish as with similar propoerties to that of the link above, so we can compare the queries and links
        for val in new_web_list:
            if newest_dish.lower() in str(val): #If the query that I have made is in the list of websites then record the wesbite used, as that will be the website used
                link = val
            if other_newest_dish.lower() in str(val):
                link = val
        return link #Return the link for the queery that the user has selected


    def go_back(self, event): #A function that passes the go_back and changes the page
        sm.current = "second"

    def get_websites(self): #This is a mirror of the get_websites_mad but is used instead for the BBC query, and is therefore different in wesbites and how the 
        url = "https://www.bbc.co.uk/food/search?q=" + query #websites list are treated as both of the lists are very different
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        web_list = []
        for link in soup.find_all('a'):
           web_list.append(link.get('href'))
        pages = []
        for link2 in web_list:
            if  "/food/search?q="+query+"&page=" in link2:
                pages.append(link2)
        for web in pages:
            if web in web_list:
                web_list.remove(web)
        for link3 in range(0, len(web_list)):        
            if web_list[link3] == "/food/my/favourites": #This is always the item in the list right before the list of websites
                num1 = link3
            if web_list[link3] == "/food/faqs": #This is always the final item in the list right after the last item in the dish
                num2 = link3
        web_list = web_list[num1+1:num2] #Return the list of dishes 
        return web_list

    def list_matcher(self, web_list): #This is a function that searches for lists and matches the list to the query (for BBC only)
        dish_choices = dish_choice.replace('+', ' ')
        for dish in range(0, len(choices)):
            if dish_choices == (choices[dish]).strip():
                num = int(dish)
        global full_link
        full_link = 'https://www.bbc.co.uk'+ web_list[num] #It searcheds for the website in the list that closeslly matches the query stripped down
        return full_link

    def initial_info(self, full_link): #This is the function that gets all the html code that is searched through in the main code
        url = full_link
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        return soup #Return all the HTML code
    
    def go_forward(self, event):
        sm.current = "forth" #Chnages the screen to the firth screen i.e Ingredients screen

class Ingredients(Screen, App): #App is called as it is a class that allows incoroporation of the kivy screens into App formatting

    def on_enter(self):
        popup = Popup(title='Ingredients-List') #On entering this screen, a popup is made
        g_layout = GridLayout(rows=2)
        g_layout2 = GridLayout(cols=2, size_hint=(1,0.3))
        cont_btn = Button(text='Would you like to continue?',size_hint_y=None, font_size=20) #Size_hint_y is the horizontal size of the button, and i made it set such that it has no fixed value
        cont_btn.bind(on_press = popup.dismiss)
        cont_btn.bind(on_release = self.advance)
        back_btn = Button(text='Would you like to go back?', size_hint_y=None, font_size=20)
        back_btn.bind(on_press = self.back)
        back_btn.bind(on_release = popup.dismiss)
        ingredients_list = self.ingredients()
        ingredient_string = ''
        for ingredient in ingredients_list: # Add a ingredient into the ingredient_list
            if len(ingredient) > 70:
                ingredient = ingredient[:70] + '\n'+ ingredient[70:] # It makes sure that the ingredients length of each line does not exceed the allowed size of the border, by shortening it down
            ingredient_string += ingredient + '\n' # Add the string to the line 
        ingred_list = Label(text=ingredient_string, # Uses the ingredient_String line used as the text in the label
                                 halign="center",
                                 valign = "top")
        g_layout2.add_widget(back_btn)              
        g_layout2.add_widget(cont_btn)   
        g_layout.add_widget(ingred_list) 
        g_layout.add_widget(g_layout2)   
        popup.content = g_layout 
        popup.open()


    def back(self, event):
        sm.current = "second"

    def advance(self, event):
        sm.current = "fifth"


    def ingredients(self): #This function gets all the ingredients from the source website, and makes a list of the ingredients
        url = full_link
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        ingredient_list = []
        if toggle == "down": #
            ingredient =  soup.find_all('li',attrs={"class":"recipe-ingredients__list-item"})
            for a in ingredient[0:]:
                result = a.text.strip() 
                ingredient_list.append(result)

        if toggle == "normal": #If the user selects BBC GoodFood
            ingredient = soup.find_all('li', attrs={"itemprop":"recipeIngredient"}) #Finds all the recipe ingredients with the html tag li
            for a in ingredient[0:]:
                result = a.text.strip()
                new_result = result.replace("\n",' ') #Removes all the new lines with breaks
                long_int = new_result.find("   ") #Find the triple gap in the text, as that text is the on with a long caption attatched to it that we need to remove
                if long_int > 0:
                    new_result  = new_result[:int(long_int)]
                ingredient_list.append(new_result)
        #This ingredient_list is going to have the list of all necessary ingredients for the dish
        return ingredient_list


class Instructions(Screen, App):

    def on_enter(self):
        popup = Popup(title="Instructions") 
        instructions = self.get_instructions()
        g_layout = GridLayout(rows=2, spacing=10)
        g_layout2 = GridLayout(cols=2, size_hint=(1,0.25))
        fin_btn = Button(text='Would you like to Finish?',size_hint_y=None, font_size=20)
        fin_btn.bind(on_press = popup.dismiss) #This is a finish button that dismisses the popup when clicked
        fin_btn.bind(on_release = self.finish)
        timer_btn = Button(text='Would you like to use a timer?', size_hint_y=None, font_size=20) #The timer button class the time_Setup function when called
        timer_btn.bind(on_press = self.timer_setup)
        instruction_string = ''
        for i in instructions:
            instruction_string += i + '\n'
        instruc_lbl = Label(text=instruction_string, text_size=self.size, font_size=13,
                                 halign="center",
                                  valign="middle") #This is a label that adds every instruction received in the string onto the instruction_Strong and then passes it
        g_layout2.add_widget(timer_btn)
        g_layout2.add_widget(fin_btn)
        g_layout.add_widget(instruc_lbl)
        g_layout.add_widget(g_layout2)
        popup.content = g_layout
        popup.open()


    def finish(self, event): #This function opens a list and then adds the dish choice the user selected into the list of completed dishes when the user decides to finish the code
        dish_list = open("dishes.txt",'a')
        dish_list.write(dish_choice.replace('+',' ') + '\n') #The + are replaced with a space so that the user cna easily view the dish they chose
        dish_list.close()
        sm.current = "main" # It send the user back to the main page, through changing the screen to the one under the "main" title
            
    def timer_setup(self, event):
        popup2 = Popup(title = "Interval time:")
        grid_layout = GridLayout(cols=2) #When the timer button is clicked, a timer popup appears whcih allows the user to choose a time
        anchor = AnchorLayout(anchor_x = 'center', anchor_y='bottom') #The Anchor layout is used here as it is easier for the user to see what thye need to do and where
        input_time = Label(text="Please input the time you \nwould like to set a timer for: ", font_size=20,) #This is a label that allows the user to chosse what time thye want
        dropdown = DropDown() #The user chooses the time they want througha  dropdown menu openedup
        for minutes in range(19): #The user will have 20 choises of intervals of 5 minutes for their timer
            btn = Button(text=(str(int(minutes+1)*5)), size_hint_y=None, height = 44) #This creates a button with the title of 5 minute intervals for every single selections choice
            btn.bind(on_release = lambda btn: dropdown.select(btn.text)) #This binds each button to the original button with the text "Minutes" so that the dropdown effect occurs when that button is clicked
            dropdown.add_widget(btn) #This adds the btn to the dropdown effect menu
        mainbutton = Button(text="Minutes", size_hint_y=None) #This is the original button that will use the dropdown effect when clicked
        mainbutton.bind(on_release = dropdown.open) #This dropdown effect is what happens when the button is released (i.e it opens the dropdown)
        dropdown.bind(on_select = lambda instance, x: setattr(mainbutton, 'text', x)) #The users selection of time is then set as the buttons text
        dropdown.bind(on_select = self.timeset) #The button also runs the timeset function when selected
        dropdown.bind(on_dismiss = popup2.dismiss) #When the button is pressed the poopup is closed

        anchor.add_widget(mainbutton) #This adds the buttons to the anchor layout
        grid_layout.add_widget(input_time)
        grid_layout.add_widget(anchor)
        popup2.content = grid_layout
        popup2.open()

    def get_instructions(self): #This function once again calls a screen scraper depending on the URL (which is a global variable) and then gets a list of instructions
        url = full_link
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        instructions_list = []
        if toggle == "down": #If the user selects BBC GoodFood
            instruction =  soup.find_all('li',attrs={"class":"recipe-method__list-item"}) #The BBC GoodFood html tag for its instructions is different to the BakingMad One, so they work differently
        if toggle == "normal":
            instruction = soup.find_all('div',attrs={"class":"method__text"})  #Therefore they need an if statement as it depends on what the user selects
        for a in instruction[0:]:
            result = a.text.strip()
            result = str(result).replace(".","\n") #This changes the full stops in the text adn converts them to a new line so all the instructions fit the box
            instructions_list.append(result)
        return instructions_list

    def timeset(self, instance, x):
        global count_num #Count_num is made global as it is a dependancy within another class, and kivy does not allow one to get functions from one class into another without the layousts interfering
        count_num = (int(x)*60) #Gets the user input and times it by 60 (to get the time in seconds)
        popup4 = Popup(title = "Confirmation")
        layout = GridLayout(rows = 2)
        label2 = Label(text="Your timer has been set \n You do not need to set another \n Unless you want to")
        btn2 = Button(text="Agreed")
        btn2.bind(on_release = popup4.dismiss) #This closes the popup when the button that is called "agreed" is pressed
        layout.add_widget(label2)
        layout.add_widget(btn2)
        popup4.content = layout
        popup4.open()
        thread = threading.Thread(target= self.threading_timer) #I put the timer into a multithreader as it allows the user to search for different recipies and dishes while also having the timer run in the background
        thread.start() #This starts the multithreading when the timer is pressed

    def threading_timer(self): 
        time.sleep(count_num) #This makes the thread sleep for the amount of seconds depending on what the user has set 
        layout = GridLayout(rows=2)
        popup = Popup(title="Countdown Finished!")#After the timer has slept the popup saynig that the countdown has finished opens
        lbl = Label(text="Your countdown is complete",font_size=20)
        btn = Button(text="Close?") #The user is then prompted to close the program with a button
        btn.bind(on_release = popup.dismiss) #When pressed the popup is dismissed
        layout.add_widget(lbl)
        layout.add_widget(btn)
        popup.content = layout
        popup.open()
        

sm = ScreenManager() #Screenmanager is the class allowing me to manage all my screens
sm.add_widget(MainWindow(name="main")) #Here I have taken every class and given them a name, which is then called in the "sm.current" title you see used above multiple times
sm.add_widget(OptionsWindow(name="second"))
sm.add_widget(DishInformation(name="third"))
sm.add_widget(Ingredients(name="forth"))
sm.add_widget(Instructions(name="fifth"))

class MyApp(App): #There needs to be a MyApp class for kivy to detect an app working, so often it just returns the first line of code
    def build(self): #build(self) is a function performed as soon as the class is .run()
        return sm


if __name__ == '__main__': #This intialitises the code
    MyApp().run()

